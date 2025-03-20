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
import json

import numpy as np
import scipy.interpolate as interp

# Internal imports
from pybdy.reader.factory import GetFile


class Z_Grid:
    def __init__(self, zgr_file, name_map_file, hgr_type, e_dict, logger, dst=1):
        """
        Master depth class.

        Args:
        ----
            zgr_file (str)           : string of file for loading zgr data
            name_map_file (str)      : string of file for mapping variable names
            hgr_type (str)           : horizontal grid type
            e_dict (dict)       : dictionary of e1 and e2 scale factors
            logger (object)          : log error and messages
            dst (bool)               : flag for destination (true) or source (false)

        Returns:
        -------
            Depth (object)          : Depth object
        """
        # Set up variables
        self.file_path = zgr_file
        self.name_map = name_map_file
        self.logger = logger
        self.dst = dst
        self.grid_type = ""
        self.grid = {}  # grid variables

        # TODO: enable .ncml option for loading variables
        if ".ncml" in self.file_path:
            raise Exception("Use .nc file for zgr input not .ncml")

        nc = GetFile(self.file_path)
        self.var_list = nc.nc.variables.keys()
        nc.close()

        # Load what we can from grid file
        vars_want = [
            "mbathy",
            "gdept_0",
            "gdept",
            "gdepu",
            "gdepv",
            "gdepf",
            "gdepw",
            "gdepuw",
            "gdepvw",
            "e3t",
            "e3w",
            "e3u",
            "e3v",
            "e3f",
            "e3uw",
            "e3vw",
            "e3fw",
        ]
        #    "gdepw_0",
        #    "e3t_0",
        #    "e3w_0",

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
        if self.dst:
            vm = "dst_"
        else:
            vm = "sc_"

        with open(self.name_map, "r") as j:
            nm = json.loads(j.read())[vm + "variable_map"]
        nc = GetFile(self.file_path)
        for vi in vars_want:
            if vi in self.var_list:
                self.grid[vi] = nc.nc[nm[vi]][:]
        nc.close()

    def find_zgrid_type(self):
        """Find out what type of vertical grid is provided zco, zps or sigma levels (sco)."""
        if ("gdept" not in self.var_list) & ("gdept_0" not in self.var_list):
            if "e3t" in self.var_list:
                self.grid["gdept"] = np.cumsum(self.grid["e3t"], axis=1)
                self.var_list = self.var_list.append("gdept")
            else:
                raise Exception("No gdept or gdept_0 variable present in zgr file.")

        if "mbathy" not in self.var_list:
            raise Exception("No mbathy variable present in zgr file.")

        if "gdept" not in self.var_list:
            self.grid_type = "zco"
        else:
            # Could still be z, z-partial-step (zps) or sigma
            # "z" - Check if all levels are equal
            x_diff = np.diff(self.grid["gdept"], axis=3).sum() == 0
            y_diff = np.diff(self.grid["gdept"], axis=2).sum() == 0
            dep_test_z = x_diff & y_diff

            # "zps" - Select levels 2 above bathy to remove partial steps.
            # Then check if levels of deepest profile are equal to all levels
            z_ind = np.indices(self.grid["gdept"].shape)[1]
            m_tile = np.tile(self.grid["mbathy"], (self.grid["gdept"].shape[1], 1, 1))[
                np.newaxis, ...
            ]
            mask_bottom = z_ind >= (m_tile - 2)
            dep_mask = np.ma.masked_where(mask_bottom, self.grid["gdept"])

            sel = np.nonzero(np.ma.max(dep_mask) == dep_mask)
            dep_deepest = np.tile(
                dep_mask[sel[0][0], :, sel[2][0], sel[3][0]],
                (self.grid["gdept"].shape[3], self.grid["gdept"].shape[2], 1),
            ).T[np.newaxis, :, :, :]
            dep_test_zps = (
                dep_deepest[mask_bottom is False]
                == self.grid["gdept"][mask_bottom is False]
            )

            # Check if all levels are inside the bathy anywhere
            lev_deepest = np.ma.max(self.grid["mbathy"])
            dep_test_sigma = lev_deepest >= (self.grid["gdept"].shape[1] - 1)
            if dep_test_z:
                # z-level
                self.grid_type = "zco"
            elif dep_test_zps.all():
                # z-partial-step
                self.grid_type = "zps"
            elif dep_test_sigma:
                # sigma-level
                self.grid_type = "sco"
            else:
                raise Exception("Unknown/unaccounted for vertical grid type.")

        self.logger.info("Vertical grid is type: " + self.grid_type)


def fill_zgrid_vars(zgr_type, grid, hgr_type, e_dict, missing):
    """
    Calculate the missing vertical grid variables and add them to grid.

    Args:
    ----
            zgr_type (str)      : type of vertical grid (zco, zps or sco)
            grid (dict)         : dictionary of grid data variable
            hgr_type (str)      : horizontal grid type
            e_dict (dict)       : dictionary of e1 and e2 scale factors
            missing (list)      : list of missing variables to calculate

    Returns:
    -------
            grid (dict)          : vertical grid data dictionary
    """
    if "mbathy" in missing:
        raise Exception("No mbathy in vertical grid file (zgr).")

    # gdep

    t_done = "gdept" not in missing
    if t_done is False:
        # Fill in the 3D gdept data from 1D gdept_0
        if "e3t" not in missing:
            grid["gdept"] = np.cumsum(grid["e3t"], axis=1)
        elif "gdept_0" in missing:
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

    if "gdept_0" in missing:
        missing = sorted(list(set(missing) - set(["gdept_0"])))

    w_done = "gdepw" not in missing
    if w_done is False:
        if "e3w" not in missing:
            grid["gdepw"] = np.cumsum(grid["e3w"], axis=1)
        else:
            # Fill in the 3D gdepw data from gdept
            grid["gdepw"] = calc_gdepw(grid["gdept"])
            missing = sorted(list(set(missing) - set(["gdepw"])))

    # Calculate other gdep values
    gdep = horiz_interp_lev(grid["gdept"], grid["gdepw"], zgr_type, hgr_type)

    for vi in missing:
        if "gdep" in vi:
            if "e3" + vi[4:] not in missing:
                grid[vi] = np.cumsum(grid["e3" + vi[4:]], axis=1)
            else:
                grid[vi] = gdep[vi[4:]]

    # e3

    e3t_done = "e3t" not in missing
    if e3t_done is False:
        grid["e3t"] = vert_calc_e3(grid["gdept"], grid["gdepw"], "e3t")
        missing = sorted(list(set(missing) - set(["e3t"])))

    e3w_done = "e3w" not in missing
    if e3w_done is False:
        grid["e3w"] = vert_calc_e3(grid["gdept"], grid["gdepw"], "e3w")
        missing = sorted(list(set(missing) - set(["e3w"])))

    # Calculate other e3 values
    e3 = horiz_interp_lev(grid["e3t"], grid["e3w"], zgr_type, hgr_type)

    for vi in missing:
        if "e" in vi[0]:
            grid[vi] = e3[vi[2:]]

    return grid


def calc_gdepw(gdept):
    """
    Calculate missing gdepw from gdept.

    Args:
    ----
            gdept (np.array)   : mesh variable gdept on t-grid

    Returns:
    -------
            dep_out (np.array) : vertical grid mesh data variable
    """
    # interpolate gdept to gdepw
    dep_out = np.zeros((gdept.shape))
    indxt = np.arange(gdept.shape[1])
    indxw = indxt[:-1] + 0.5
    for j in range(gdept.shape[2]):
        for i in range(gdept.shape[3]):
            func = interp.interp1d(indxt, gdept[0, :, j, i], kind="cubic")
            # top gdepw is zero
            dep_out[0, 1:, j, i] = func(indxw)

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

    return e3


def horiz_interp_lev(t, w, zgr_type, hgr_type):
    """
    Horizontally interpolate the vertical scale factors e3 and gdep.

    For A-Grids, u, v and f values are set to t and w values.
    For C-Grids, zps or sco verticle coords are used to define u, v, and f.
    For B-Grids, u and v values are set to f values following zps or sco.

    Args:
    ----
            t (np.array)       : vertical scale factors e or dep on t points
            w (np.array)       : vertical scale factors e or dep on w points
            zgr_type (str)     : type of vertical grid (zco, zps or sco)
            hgr_type (str)     : horizontal grid type (A, B or C)

    Returns:
    -------
            lev (dict)            : vertical distance scale factor e or gdep
    """
    # If zgr == zco or hgr == "A" just copy t and w
    lev = {}
    lev["u"] = t.copy()
    lev["v"] = t.copy()
    lev["uw"] = w.copy()
    lev["vw"] = w.copy()
    lev["f"] = t.copy()
    lev["fw"] = w.copy()

    if zgr_type == "zps":
        lev["u"][..., :, :-1] = np.minimum(t[..., :, 1:], t[..., :, :-1])  # i
        lev["v"][..., :-1, :] = np.minimum(t[..., 1:, :], t[..., :-1, :])  # j
        lev["uw"][..., :, :-1] = np.minimum(w[..., :, 1:], w[..., :, :-1])  # i
        lev["vw"][..., :-1, :] = np.minimum(w[..., 1:, :], w[..., :-1, :])  # j
        lev["f"][..., :, :-1] = np.minimum(
            lev["v"][..., :, 1:], lev["v"][..., :, :-1]
        )  # i
        lev["fw"][..., :, :-1] = np.minimum(
            lev["vw"][..., :, 1:], lev["vw"][..., :, :-1]
        )  # i

    elif zgr_type == "sco":
        lev["u"][..., :, :-1] = 0.5 * (t[..., :, 1:] + t[..., :, :-1])  # i
        lev["v"][..., :-1, :] = 0.5 * (t[..., 1:, :] + t[..., :-1, :])  # j
        lev["uw"][..., :, :-1] = 0.5 * (w[..., :, 1:] + w[..., :, :-1])  # i
        lev["vw"][..., :-1, :] = 0.5 * (w[..., 1:, :] + w[..., :-1, :])  # j
        lev["f"][..., :, :-1] = 0.5 * (
            lev["v"][..., :, 1:] + lev["v"][..., :, :-1]
        )  # i
        lev["fw"][..., :, :-1] = 0.5 * (
            lev["vw"][..., :, 1:] + lev["vw"][..., :, :-1]
        )  # i

    if hgr_type == "B":
        lev["u"] = lev["f"].copy()
        lev["v"] = lev["f"].copy()
        lev["uw"] = lev["fw"].copy()
        lev["vw"] = lev["fw"].copy()

    return lev


def horiz_interp_e3_old(e_in, var_in, lev):
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
