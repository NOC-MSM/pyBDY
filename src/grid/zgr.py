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
from grid import hgr

# Internal imports
from pybdy.reader.factory import GetFile


class Depth:
    def __init__(self, zgr_file, hgr_type, logger):
        """
        Master depth class.

        Args:
        ----
            zgr_file (str)           : string of file for loading zgr data
            hgr_type (str)           : horizontal grid type
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
        missing_vars = list(set(vars_want) - set(self.var_list))
        self.grid = fill_zgrid_vars(self.grid_type, self.grid, hgr_type, missing_vars)

        return self.grid

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
        elif self.grid["mbathy"] not in self.var_list:
            raise Exception("No mbathy variable present in zgr file.")
        elif "gdept" not in self.var_list:
            self.grid_type = "z"
        else:
            # Could still be z, z-partial-step (zps) or sigma
            # Check if all levels are equal
            dep_test1 = np.tile(
                self.grid["gdept"][0, 0, 0, :],
                (self.grid["gdept"].shape[1], self.grid["gdept"].shape[2], 1),
            )

            # Don't select levels within 2 grid cells of bathy to remove partial steps
            # Then check if levels are equal
            ind = self.grid["gdept"] <= self.grid["mbathy"]
            ind[0, :-2, ...] = ind[0, 2:, ...]
            dep_mask = np.ma.masked_where(ind is False, self.grid["gdept"])
            sel = np.nonzero(np.ma.max(dep_mask) == dep_mask)
            dep_test2 = np.tile(
                dep_mask[sel[0][0], :, sel[2][0], sel[3][0]],
                (self.grid["gdept"].shape[1], self.grid["gdept"].shape[2], 1),
            )

            # Check if how many levels are below the bathy
            ind1 = self.grid["gdept"] >= self.grid["mbathy"]
            dep_mask = np.ma.masked_where(ind1, self.grid["gdept"])
            dep_test3 = np.ma.max(np.ma.count(dep_mask, axis=1))

            if (dep_test1 == self.grid["gdept"][0, ...]).all():
                # z-level
                self.grid_type = "z"
            elif (dep_test2[ind] == self.grid["gdept"][ind]).all():
                # z-partial-step
                self.grid_type = "zps"
            elif dep_test3 >= (self.grid["gdept"].shape[1] - 1):
                # sigma-level
                self.grid_type = "s"
            else:
                raise Exception("Unknown/unaccounted for vertical grid type.")

        self.logger.info("Vertical grid is type: " + self.sc_grid_type)


def fill_zgrid_vars(grid_type, grid, hgr_type, missing):
    """
    Calculate the missing vertical grid variables and add them to grid.

    Args:
    ----
            grid_type (str)     : type of horizontal grid (z, zps or s)
            grid (dict)         : dictionary of grid data variable
            hgr_type (str)      : horizontal grid type
            missing (list)      : list of missing variables to calculate

    Returns:
    -------
            grid (dict)          : vertical grid data dictionary
    """
    t_done = "gdept" not in missing
    if t_done is False:
        # Fill in the 3D gdept data from 1D gdept_0
        if ("gdept_0" in missing) | ("mbathy" in missing):
            raise Exception("No gdept_0 and mbathy in vertical grid file (zgr).")
        else:
            grid["gdept"] = np.tile(
                grid["gdept_0"],
                (1, grid["mbathy"].shape[1], grid["mbathy"].shape[2], 1),
            )
            grid["gdept"] = np.transpose(grid["gdept"], axes=[0, 3, 1, 2])
        missing = list(set(missing) - set(["gdept"]))

    w_done = "gdepw" not in missing
    if w_done is False:
        # Fill in the 3D gdepw data from gdept
        grid["gdepw"] = calc_gdep(grid["gdept"], "gdepw")
        missing = list(set(missing) - set(["gdepw"]))

    for vi in missing:
        if "gdep" in vi:
            if "w" in vi:
                # select which level is used for averaging
                # for uw and vw
                ig = "w"
            else:
                # for u, v and f
                ig = "t"

            if hgr_type == "A":
                grid[vi] = grid[vi[:-1] + ig]
            elif hgr_type == "B":
                grid[vi] = calc_gdep(grid["gdep" + ig], "f")
            elif hgr_type == "C":
                grid[vi] = calc_gdep(grid["gdep" + ig], vi)

    for vi in missing:
        if "e" in vi[0]:
            if "u" in vi:
                grid[vi] = calc_e3(grid["gdepu"], grid["gdepuw"], vi)
            elif "v" in vi:
                grid[vi] = calc_e3(grid["gdepv"], grid["gdepvw"], vi)
            else:
                grid[vi] = calc_e3(grid["gdept"], grid["gdepw"], vi)
    return grid


def calc_gdep(gdeptw, lev):
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
        dep_out = np.zeros((gdeptw.shape))
        dep_out[:, 1:, ...] = (gdeptw[:, 1:, ...] + gdeptw[:, :-1, ...]) / 2
        diff = np.abs(dep_out[:, 1, ...] - gdeptw[:, 0, ...])
        dep_out[:, 0, ...] = gdeptw[:, 0, ...] - diff
    elif "t_0" in lev:
        dep_out = gdeptw
    else:
        dep_out = hgr.calc_grid_from_t(gdeptw, lev)

    if "_0" in lev:
        # Do we need _0 vars?
        dep_out = dep_out[:, :, 0, 0]

    return dep_out


def calc_e3(gdep_mid, gdep_top, lev):
    """
    Calculate missing scale factors e3 from gdep.

    Args:
    ----
            gdep_mid (np.array)  : mesh variable on t levels
            gdep_top (np.array)  : mesh variable on w levels
            lev (str)         : grid level type (e3 of t, w, u, v)

    Returns:
    -------
            e3 (np.array)    : vertical distance scale factor e3
    """
    gs = gdep_top.shape
    gdep_temp = np.zeros((gs[0], gs[1] + 1, gs[2], gs[3]))

    if "w" in lev:
        # get e3w from gdept and gdepw
        gdep_temp[:, 1:, ...] = gdep_mid
        diff = np.abs(gdep_top[:, 0, ...] - gdep_mid[:, 0, ...])
        gdep_temp[:, 0, ...] = gdep_top[:, 0, ...] - diff
        e3 = gdep_temp[:, 1:, ...] - gdep_temp[:, :-1, ...]
    else:
        # get e3t, e3u, e3v from gdep_mid and gdep_top
        gdep_temp[:, :-1, ...] = gdep_top
        diff = np.abs(gdep_mid[:, -1, ...] - gdep_top[:, -1, ...])
        gdep_temp[:, -1, ...] = gdep_mid[:, -1, ...] + diff
        e3 = gdep_temp[:, 1:, ...] - gdep_temp[:, :-1, ...]

    return e3
