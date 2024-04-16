import logging

import numpy as np

from .reader.factory import GetFile
from .utils.nemo_bdy_lib import sub2ind


# Query name
class Depth:
    """
    Generate Depth information.

    Written by John Kazimierz Farey, Sep 2012
    Port of Matlab code of James Harle

    # Generates depth points for t, u and v in one loop iteration

    Initialise with bdy t, u and v grid attributes (Grid.bdy_i) and
    settings dictionary
    """

    def __init__(self, bdy_t, bdy_u, bdy_v, settings):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("init Depth")

        # set assign Boundary class grid and get bathy levels
        self.settings = settings
        self.mbathy = self.get_mbathy()
        self.bdy_t = bdy_t
        self.bdy_u = bdy_u
        self.bdy_v = bdy_v

        # set source data for target vertical grid
        if settings["interp"]:
            self.set_dst_z_grid_3d()
        else:
            self.set_src_z_grid_3d()

        # find bdy indices from subscripts
        self.t_ind = sub2ind(self.mbathy.shape, bdy_t[:, 0], bdy_t[:, 1])

        self.u_ind = sub2ind(self.mbathy.shape, bdy_u[:, 0], bdy_u[:, 1])
        self.u_ind2 = sub2ind(self.mbathy.shape, bdy_u[:, 0] + 1, bdy_u[:, 1])

        self.v_ind = sub2ind(self.mbathy.shape, bdy_v[:, 0], bdy_v[:, 1])
        self.v_ind2 = sub2ind(self.mbathy.shape, bdy_v[:, 0], bdy_v[:, 1] + 1)

        # initialise depth arrays
        self.initialise_depth_arrays()

        # assign depths to Bounday class grid
        for k in range(self.nz):
            self.assign_depths_to_flattened_array(k)

    def get_mbathy(self):
        """Get mbathy from dst grid."""
        # open dst_hgr
        nc = GetFile(self.settings["dst_hgr"])

        # get bottom_level
        mbathy = nc["bottom_level"][:, :, :].squeeze()

        # numpy requires float dtype to use NaNs
        mbathy = np.float16(mbathy)
        mbathy[mbathy == 0] = np.NaN

        nc.close()  # close dst_hgr

        return mbathy

    def set_dst_z_grid_3d(self):
        """Set vertical grid according to dst coordinates."""
        # open dst_zgr
        nc = GetFile(self.settings["dst_zgr"])

        # get number of depth levels
        self.nz = len(nc["nav_lev"][:])

        # assign 3d depth information from dst
        self.wrk1 = nc["gdept_0"][0, :, :, :]
        self.wrk2 = nc["gdepw_0"][0, :, :, :]

        nc.close()  # close dst_zgr

    def set_src_z_grid_3d(self):
        """Set vertical grid according to src coordinates."""
        # open dst_zgr
        nc = GetFile(self.settings["src_zgr"])

        # get number of depth levels
        self.nz = len(nc["nav_lev"][:])

        # set shape according to src z and dst x/y
        dst_shape = self.mbathy.shape + (self.nz,)

        # assign 3d depth information from src
        self.wrk1 = np.broadcast_to(nc["gdept_1d"][0, :], dst_shape)
        self.wrk2 = np.broadcast_to(nc["gdepw_1d"][0, :], dst_shape)

        # transpose from (y,x,z) to (z,y,x)
        self.wrk1 = np.array(np.moveaxis(self.wrk1, 2, 0))
        self.wrk2 = np.array(np.moveaxis(self.wrk2, 2, 0))

        nc.close()  # close dst_zgr

    def initialise_depth_arrays(self):
        """Assign depth variables according to grid set in Bounday class."""
        # Set up arrays
        t_nbdy = len(self.bdy_t[:, 0])
        u_nbdy = len(self.bdy_u[:, 0])
        v_nbdy = len(self.bdy_v[:, 0])
        zp = ["t", "wt", "u", "wu", "v", "wv"]
        self.zpoints = {}
        for z in zp:
            if "t" in z:
                nbdy = t_nbdy
            elif "u" in z:
                nbdy = u_nbdy
            elif "v" in z:
                nbdy = v_nbdy
            self.zpoints[z] = np.zeros((self.nz, nbdy))

    # RDP: the following is not functional but is retained for reference
    #    def create_sco_grid(self):
    #
    #        hc = settings["hc"]
    #        # Depth of water column at t-point
    #        hbatt = nc["hbatt"][:, :, :].squeeze()
    #        # Replace land with NaN
    #        hbatt[mbathy == 0] = np.NaN
    #
    #        for k in range(nz):
    #
    #            # sigma coeffs at t-point (1->0 indexed)
    #            gsigt = nc["gsigt"][0, k, :, :]  # nc.variables['gsigt'][0,k,:,:]
    #            # sigma coeffs at w-point
    #            gsigw = nc["gsigw"][0, k, :, :]  # nc.variables['gsigw'][0,k,:,:]
    #
    #            # NOTE:  check size of gsigt SKIPPED
    #            print (nc["gsigt"])
    #
    #            wrk1 = (hbatt - hc) * gsigt[:, :] + (hc * (k + 0.5) / (nz - 1))
    #            wrk2 = (hbatt - hc) * gsigw[:, :] + (hc * (k + 0.5) / (nz - 1))

    def assign_depths_to_flattened_array(self, k):
        """Assign depth information to k level of Bounday class variables."""
        wrk1 = self.wrk1[k]
        wrk2 = self.wrk2[k]

        # Replace deep levels that are not used with NaN
        wrk2[self.mbathy + 1 < k + 1] = np.NaN
        wrk1[self.mbathy < k + 1] = np.NaN
        zshapes = {}

        for p in list(self.zpoints.keys()):
            zshapes[p] = self.zpoints[p].shape
        wshapes = []
        wshapes.append(wrk1.shape)
        wshapes.append(wrk2.shape)
        wrk1, wrk2 = wrk1.flatten("F"), wrk2.flatten("F")

        self.zpoints["t"][k, :] = wrk1[self.t_ind]
        self.zpoints["wt"][k, :] = wrk2[self.t_ind]

        self.zpoints["u"][k, :] = 0.5 * (wrk1[self.u_ind] + wrk1[self.u_ind2])
        self.zpoints["wu"][k, :] = 0.5 * (wrk2[self.u_ind] + wrk2[self.u_ind2])

        self.zpoints["v"][k, :] = 0.5 * (wrk1[self.v_ind] + wrk1[self.v_ind2])
        self.zpoints["wv"][k, :] = 0.5 * (wrk2[self.v_ind] + wrk2[self.v_ind2])

        for p in list(self.zpoints.keys()):
            self.zpoints[p] = self.zpoints[p].reshape(zshapes[p])

        self.logger.debug("Done loop, zpoints: %s ", self.zpoints["t"].shape)
