# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""
Created on Mon Feb 03 18:01:00 2025.

@author James Harle
@author Benjamin Barton
@author Ryan Patmore
@author Anthony Wise
"""

# External imports
import numpy as np
import scipy.interpolate as interp
from grid import hgr

# Internal imports
from pybdy.reader.factory import GetFile


class Depth:
    def __init__(self, zgr_file, hgr_type, e_dict, logger):
        """
        Master depth class.

        Args:
        ----
            zgr_file (str)           : string of file for loading zgr data
            hgr_type (str)           : horizontal grid type
            e_dict (dict)       : dictionary of e1 and e2 scale factors
            logger (object)          : log error and messages

        Returns:
        -------
            Depth (object)          : Depth object
        """
        # Set up variables
        self.file_path = zgr_file
        self.logger = logger
        self.grid_type = ""
        self.grid = {}  # grid variables

        nc = GetFile(self.file_path)
        self.var_list = nc.nc.variables.keys()
        nc.close()

        # Load what we can from grid file
        vars_want = [
            "mbathy",
            "gdept",
            "gdepu",
            "gdepv",
            "gdepf",
            "gdepw",
            "gdepuw",
            "gdepvw",
            "e3t",
            "e3u",
            "e3v",
            "e3w",
            "gdept_0",
            "gdepw_0",
            "e3t_0",
            "e3w_0",
        ]
        self.get_vars(vars_want)

        # Work out what sort of source grid we have
        self.find_zgrid_type()

        # Fill in missing variables we need for the grid type
        missing_vars = sorted(list(set(vars_want) - set(self.var_list)))

        self.grid = fill_zgrid_vars(
            self.grid_type, self.grid, hgr_type, e_dict, missing_vars
        )
        self.var_list = list(self.grid.keys())

    def get_vars(self, vars_want):
        """
        Get the gdep and e3 scale factors from file if possible.

        Args:
        ----
            vars_want (list)       : variables needed from file.
        """
        nc = GetFile(self.file_path)
        for vi in vars_want:
            if vi in self.var_list:
                self.grid[vi] = nc.nc[vi][:]
        nc.close()

    def find_zgrid_type(self):
        """Find out what type of vertical grid is provided z, zps or sigma levels."""
        if ("gdept" not in self.var_list) & ("gdept_0" not in self.var_list):
            raise Exception("No gdept or gdept_0 variable present in zgr file.")
        elif "mbathy" not in self.var_list:
            raise Exception("No mbathy variable present in zgr file.")
        elif "gdept" not in self.var_list:
            self.grid_type = "z"
        else:
            # Could still be z, z-partial-step (zps) or sigma
            # Check if all levels are equal
            # NOTE: This won't work because level near bathy is different
            np.tile(
                self.grid["gdept"][0, :, 0, 0],
                (self.grid["gdept"].shape[3], self.grid["gdept"].shape[2], 1),
            ).T

            # Don't select levels within 2 grid cells of bathy to remove partial steps
            # Then check if levels are equal
            ind = self.grid["gdept"] <= self.grid["mbathy"]
            ind[0, :-2, ...] = ind[0, 2:, ...]
            dep_mask = np.ma.masked_where(ind is False, self.grid["gdept"])
            sel = np.nonzero(np.ma.max(dep_mask) == dep_mask)
            dep_test2 = np.tile(
                dep_mask[sel[0][0], :, sel[2][0], sel[3][0]],
                (self.grid["gdept"].shape[3], self.grid["gdept"].shape[2], 1),
            ).T[np.newaxis, :, :, :]

            # Check if how many levels are below the bathy
            ind1 = self.grid["gdept"] >= self.grid["mbathy"]
            dep_mask = np.ma.masked_where(ind1, self.grid["gdept"])
            dep_test3 = np.ma.max(np.ma.count(dep_mask, axis=1))

            # if (dep_test1 == self.grid["gdept"][0, ...]).all():
            #    # z-level
            #    self.grid_type = "z"
            if (dep_test2[ind] == self.grid["gdept"][ind]).all():
                # z-partial-step
                self.grid_type = "z"
            elif dep_test3 >= (self.grid["gdept"].shape[1] - 1):
                # sigma-level
                self.grid_type = "s"
            else:
                raise Exception("Unknown/unaccounted for vertical grid type.")

        self.logger.info("Vertical grid is type: " + self.grid_type)


def fill_zgrid_vars(grid_type, grid, hgr_type, e_dict, missing):
    """
    Calculate the missing vertical grid variables and add them to grid.

    Args:
    ----
            grid_type (str)     : type of horizontal grid (z, zps or s)
            grid (dict)         : dictionary of grid data variable
            hgr_type (str)      : horizontal grid type
            e_dict (dict)       : dictionary of e1 and e2 scale factors
            missing (list)      : list of missing variables to calculate

    Returns:
    -------
            grid (dict)          : vertical grid data dictionary
    """
    # if "e3u" in missing:
    #    missing.append("gdepuw")
    # if "e3v" in missing:
    #    missing.append("gdepvw")
    if "mbathy" in missing:
        raise Exception("No mbathy in vertical grid file (zgr).")

    t_done = "gdept" not in missing
    if t_done is False:
        # Fill in the 3D gdept data from 1D gdept_0
        if "gdept_0" in missing:
            raise Exception("No gdept_0 in vertical grid file (zgr).")
        else:
            if len(grid["mbathy"].shape) == 2:
                grid["mbathy"] = grid["mbathy"][np.newaxis, :, :]
            elif len(grid["mbathy"].shape) != 3:
                raise Exception("mbathy is not 2D or 3D.")

            grid["gdept"] = np.tile(
                grid["gdept_0"],
                (
                    grid["mbathy"].shape[0],
                    grid["mbathy"].shape[1],
                    grid["mbathy"].shape[2],
                    1,
                ),
            )
            grid["gdept"] = np.transpose(grid["gdept"], axes=[0, 3, 1, 2])
        missing = sorted(list(set(missing) - set(["gdept"])))

    w_done = "gdepw" not in missing
    if w_done is False:
        # Fill in the 3D gdepw data from gdept
        grid["gdepw"] = calc_gdep(grid["gdept"], grid["mbathy"], "gdepw")
        missing = sorted(list(set(missing) - set(["gdepw"])))

    for vi in missing:
        if "gdep" in vi:
            if "w" in vi:
                # select which level is used for averaging
                # w for uw and vw
                ig = "w"
            else:
                # t for u, v and f
                ig = "t"

            if hgr_type == "A":
                grid[vi] = grid[vi[:-1] + ig]
            elif hgr_type == "B":
                if ("u" in vi) | ("v" in vi):
                    grid[vi] = calc_gdep(grid["gdep" + ig], grid["mbathy"], "f")
                else:
                    grid[vi] = calc_gdep(grid["gdep" + ig], grid["mbathy"], vi)
            elif hgr_type == "C":
                grid[vi] = calc_gdep(grid["gdep" + ig], grid["mbathy"], vi)

    e3t_done = "e3t" not in missing
    if e3t_done is False:
        grid["e3t"] = vert_calc_e3(grid["gdept"], grid["gdepw"], "e3t")
        missing = sorted(list(set(missing) - set(["e3t"])))

    for vi in missing:
        # Calculate e values
        if "e" in vi[0]:
            if hgr_type == "A":
                if ("u" in vi) | ("v" in vi) | ("f" in vi):
                    grid[vi] = grid["e3t"][:]
                else:
                    # e3t, e3w
                    grid[vi] = vert_calc_e3(grid["gdept"], grid["gdepw"], vi)

            elif hgr_type == "B":
                if ("u" in vi) | ("v" in vi) | ("f" in vi):
                    e3u = horiz_interp_e3(e_dict, grid["e3t"], vi)
                    grid[vi] = horiz_interp_e3(e_dict, e3u, vi)
                else:
                    # e3t, e3w
                    grid[vi] = vert_calc_e3(grid["gdept"], grid["gdepw"], vi)

            elif hgr_type == "C":
                if "u" in vi:
                    # grid[vi] = calc_e3(grid["gdepu"], grid["gdepuw"], vi)
                    grid[vi] = horiz_interp_e3(e_dict, grid["e3t"], vi)
                elif "v" in vi:
                    # grid[vi] = calc_e3(grid["gdepv"], grid["gdepvw"], vi)
                    grid[vi] = horiz_interp_e3(e_dict, grid["e3t"], vi)
                elif "f" in vi:
                    e3u = horiz_interp_e3(e_dict, grid["e3t"], vi)
                    grid[vi] = horiz_interp_e3(e_dict, e3u, vi)
                else:
                    # e3t, e3w
                    grid[vi] = vert_calc_e3(grid["gdept"], grid["gdepw"], vi)
    return grid


def calc_gdep(gdeptw, mbathy, lev):
    """
    Calculate missing gdep from gdeptw.

    Args:
    ----
            gdeptw (np.array)  : mesh variable gdep on t-grid or w-grid
            lev (str)         : grid level type (gdep of u, v, w, f, uw, vw)

    Returns:
    -------
            dep_out (dict)    : vertical grid mesh data variable
    """
    if "gdepw" == lev:
        # interpolate gdept to gdepw
        dep_out = np.zeros((gdeptw.shape))
        indxt = np.arange(gdeptw.shape[1])
        indxw = indxt[:-1] + 0.5
        for j in range(gdeptw.shape[2]):
            for i in range(gdeptw.shape[3]):
                func = interp.interp1d(indxt, gdeptw[0, :, j, i], kind="cubic")
                # top gdepw is zero
                dep_out[0, 1:, j, i] = func(indxw)

    elif "_0" in lev:
        dep_out = gdeptw[:, :, 0, 0]
    else:
        dep_out = hgr.calc_grid_from_t(gdeptw, lev)

    return dep_out


def vert_calc_e3(gdep_mid, gdep_top, lev):
    """
    Calculate missing vertical scale factors e3 from gdep.

    Args:
    ----
            gdep_mid (np.array)  : mesh variable on t levels
            gdep_top (np.array)  : mesh variable on w levels
            lev (str)            : grid level type (e3 of t, w, u, v)

    Returns:
    -------
            e3 (np.array)    : vertical distance scale factor e3 of lev
    """
    gs = gdep_top.shape
    gdep_temp = np.zeros((gs[0], gs[1] + 1, gs[2], gs[3]))

    if "w" in lev:
        # get e3w from gdep_mid and gdep_top
        gdep_temp[:, 1:, ...] = gdep_mid
        diff = np.abs(gdep_top[:, 0, ...] - gdep_mid[:, 0, ...])
        gdep_temp[:, 0, ...] = gdep_top[:, 0, ...] - diff
        e3 = gdep_temp[:, 1:, ...] - gdep_temp[:, :-1, ...]
    else:
        # get e3t from gdep_mid and gdep_top
        gdep_temp[:, :-1, ...] = gdep_top
        diff = np.abs(gdep_mid[:, -1, ...] - gdep_top[:, -1, ...])
        gdep_temp[:, -1, ...] = gdep_mid[:, -1, ...] + diff
        e3 = gdep_temp[:, 1:, ...] - gdep_temp[:, :-1, ...]

    if "_0" in lev:
        e3 = e3[:, :, 0, 0]

    return e3


def horiz_interp_e3(e_in, var_in, lev):
    """
    Horizontally interpolate the vertical scale factors e3u, e3v, e3f.

    Use the horizontal scale factors to calculate interpolation factors.
    To interpolate to get e3u or e3v, input var_in as e3t data but for e3f this
    should be e3u.

    Args:
    ----
            e_in (dict)       : all horizontal scale factors e1 and e2 in dictionary
            var_in (np.array) : e scale factor to interpolate from e3t (or e3u for f)
            lev (str)         : grid level type (e3 of u, v, f)

    Returns:
    -------
            e3 (np.array)    : vertical distance scale factor e3 of lev
    """
    e1t = e_in["e1t"]
    e2t = e_in["e2t"]
    e1u = e_in["e1u"]
    e2u = e_in["e2u"]
    e1v = e_in["e1v"]
    e2v = e_in["e2v"]
    e1f = e_in["e1f"]
    e2f = e_in["e2f"]
    e1e2t = np.tile(e1t[0, :, :] * e2t[0, :, :], (var_in.shape[1], 1, 1))[
        np.newaxis, ...
    ]
    e1e2u = np.tile(e1u[0, :, :] * e2u[0, :, :], (var_in.shape[1], 1, 1))[
        np.newaxis, ...
    ]
    e1e2v = np.tile(e1v[0, :, :] * e2v[0, :, :], (var_in.shape[1], 1, 1))[
        np.newaxis, ...
    ]
    e1e2f = np.tile(e1f[0, :, :] * e2f[0, :, :], (var_in.shape[1], 1, 1))[
        np.newaxis, ...
    ]
    e3_tmp = np.ma.zeros(var_in.shape)

    if "u" in lev:
        e3_tmp[:, :, :, :-1] = (0.5 / e1e2u[..., :-1]) * (
            (e1e2t[..., :-1] * var_in[..., :-1]) + (e1e2t[..., 1:] * var_in[..., 1:])
        )
        e3_tmp[:, :, :, -1] = e3_tmp[:, :, :, -2]

    if ("v" in lev) | ("f" in lev):
        e3_tmp[:, :, :-1, :] = (0.5 / e1e2v[..., :-1, :]) * (
            (e1e2t[..., :-1, :] * var_in[..., :-1, :])
            + (e1e2t[..., 1:, :] * var_in[..., 1:, :])
        )
        e3_tmp[:, :, -1, :] = e3_tmp[:, :, -2, :]

    if "f" in lev:
        # use e3u here as var_in
        e3_tmp[:, :, :-1, :] = (0.5 / e1e2f[..., :-1, :]) * (
            (e1e2u[..., :-1, :] * var_in[..., :-1, :])
            + ((e1e2u[..., 1:, :] * var_in[..., 1:, :]))
        )
        e3_tmp[:, :, -1, :] = e3_tmp[:, :, -2, :]

    return e3_tmp
