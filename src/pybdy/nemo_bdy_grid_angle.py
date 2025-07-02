# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Calculates Grid Angles                                              #
#                                                                     #
# Written by John Kazimierz Farey, Sep 2012                           #
# Port of Matlab code of James Harle                                  #
#                                                                     #
# I have substituted the nemo_phycst for numpy inbuilts               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# coord_fname: nemo coordinate file
# i: model zonal indices
# j: model meridional indices
# cd_type: define the nature of pt2d grid points

import logging

import numpy as np


class GridAngle:
    """Class to get orientation of grid from I and J offsets for different grid types."""

    def __init__(self, hgr, imin, imax, jmin, jmax, cd_type):
        """
        Get sin and cosin files for the grid angle from North.

        Parameters
        ----------
            hgr  : grid object
            imin : minimum model zonal indices
            imax : maximum model zonal indices
            jmin : minimum model meridional indices
            jmax : maximum model meridional indices
            cd_type: define the nature of pt2d grid points

        Returns
        -------
            None : object
        """
        # set case and check validity
        self.CASES = {
            "t": [0, 0, 0, -1],
            "u": [0, 0, 0, -1],
            "v": [0, 0, -1, 0],
            "f": [0, 1, 0, 0],
        }
        self.MAP = {"t": "v", "u": "f", "v": "f", "f": "u"}
        self.CD_T = cd_type.lower()
        self.logger = logging.getLogger(__name__)
        if self.CD_T not in ["t", "u", "v", "f"]:
            raise ValueError("Unknown grid grid_type %s" % cd_type)
        self.M_T = self.MAP[self.CD_T]

        self.hgr = hgr
        self.logger.debug("Grid Angle: ", self.CD_T)

        # set constants
        self.IMIN, self.IMAX = imin, imax
        self.JMIN, self.JMAX = jmin, jmax

        ndim = len(self.hgr.grid["glamt"].shape)
        if ndim == 4:
            self.DIM_STR = 0, 0
        elif ndim == 3:
            self.DIM_STR = 0
        else:
            self.DIM_STR = None

        # Get North pole direction and modulus for cd_type
        np_x, np_y, np_n = self.get_north_dir()

        # Get i or j MAP segment Direction around cd_type
        sd_x, sd_y, sd_n = self.get_seg_dir(np_n)

        # Get cosinus and sinus
        self.sinval, self.cosval = self.get_sin_cos(np_x, np_y, np_n, sd_x, sd_y, sd_n)

    def get_sin_cos(self, nx, ny, nn, sx, sy, sn):
        """Get sin and cos from lat and lon using using scaler/vectorial products."""
        # Geographic mesh
        i, j, ii, jj = self.CASES[self.CD_T]
        var_one = self.get_lam_phi(map=True, i=i, j=j, single=True)
        var_two = self.get_lam_phi(map=True, i=ii, j=jj, single=True)

        ind = (np.abs(var_one - var_two) % 360) < 1.0e-8

        # Cosinus and sinus using using scaler/vectorial products
        if self.CD_T == "v":
            sin_val = (nx * sx + ny * sy) / sn
            cos_val = -(nx * sy - ny * sx) / sn
        else:
            sin_val = (nx * sy - ny * sx) / sn
            cos_val = (nx * sx + ny * sy) / sn

        sin_val[ind] = 0
        cos_val[ind] = 1

        return sin_val, cos_val

    def get_north_dir(self):
        """Find North pole direction and modulus of some point."""
        zlam, zphi = self.get_lam_phi()
        z_x_np = self.trig_eq(-2, "cos", zlam, zphi)
        z_y_np = self.trig_eq(-2, "sin", zlam, zphi)
        z_n_np = np.power(z_x_np, 2) + np.power(z_y_np, 2)

        return z_x_np, z_y_np, z_n_np

    def get_seg_dir(self, north_n):
        """Find segmentation direction of some point."""
        i, j, ii, jj = self.CASES[self.CD_T]
        zlam, zphi = self.get_lam_phi(map=True, i=i, j=j)
        z_lan, z_phh = self.get_lam_phi(map=True, i=ii, j=jj)

        z_x_sd = self.trig_eq(2, "cos", zlam, zphi) - self.trig_eq(
            2, "cos", z_lan, z_phh
        )
        z_y_sd = self.trig_eq(2, "sin", zlam, zphi) - self.trig_eq(
            2, "sin", z_lan, z_phh
        )  # N

        z_n_sd = np.sqrt(north_n * (np.power(z_x_sd, 2) + np.power(z_y_sd, 2)))
        z_n_sd[z_n_sd < 1.0e-14] = 1.0e-14

        return z_x_sd, z_y_sd, z_n_sd

    def get_lam_phi(self, map=False, i=0, j=0, single=False):
        """
        Get lam/phi in (offset) i/j range for init grid type.

        Data must be converted to float64 to prevent dementation of later results.
        """
        d = self.DIM_STR
        i, ii = self.IMIN + i, self.IMAX + i
        j, jj = self.JMIN + j, self.JMAX + j
        if j < 0:
            jj -= j
            j = 0
        if i < 0:
            ii -= i
            i = 0

        if map:
            case = self.M_T
        else:
            case = self.CD_T
        zlam = np.float64(self.hgr.grid["glam" + case][d, j:jj, i:ii])
        if single:
            return zlam
        zphi = np.float64(self.hgr.grid["gphi" + case][d, j:jj, i:ii])

        return zlam, zphi

    def trig_eq(self, x, eq, z_one, z_two):
        """Calculate long winded equation of two vars; some lam and phi."""
        if eq == "cos":
            z_one = np.cos(np.radians(z_one))
        elif eq == "sin":
            z_one = np.sin(np.radians(z_one))
        else:
            raise ValueError('eq must be "cos" or "sin"')

        z_two = np.tan(np.pi / 4 - np.radians(z_two) / 2)

        return x * z_one * z_two
