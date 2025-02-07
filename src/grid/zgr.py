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
Created on Thu Dec 22 18:01:00 2024.

@author James Harle
@author Benjamin Barton
@author Ryan Patmore
@author Anthony Wise
"""

# External imports
import numpy as np

# Internal imports
from pybdy.reader.factory import GetFile


class Depth:
    def __init__(self, SC, DC, settings, hgr_type, logger):
        """
        Master depth class.

        Args:
        ----
            SC (Source object)       : object with source grid info
            DC (Destination object)  : object with destination grid info
            settings (dict)          : dictionary of settings for loading data
            hgr_type (str)           : horizontal grid type
            logger                   : log error and messages

        Returns:
        -------
            Depth (object)          : Depth object
        """
        # Set up variables
        self.settings = settings
        self.grid_type = ""
        self.grid = {}  # grid variables

        nc = GetFile(self.settings["src_zgr"])
        self.var_list = nc.variables.keys()
        nc.close()

        # Load what we can from grid file
        vars_want = [
            "mbathy",
            "gdept",
            "gdepu",
            "gdepv",
            "gdepw",
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
        missing_vars = set(self.var_list) - set(vars_want)
        self.grid = fill_zgrid_vars(self.grid_type, self.grid, hgr_type, missing_vars)

        return self.grid

    def get_vars(self, vars_want):
        """
        Get the gdep and e3 scale factors from file if possible.

        Args:
        ----
            vars_want (list)       : variables needed from file.
        """
        nc = GetFile(self.settings["src_zgr"])
        for vi in vars_want:
            if vi in self.var_list:
                self.grid[vi] = nc[vi][:]
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
            # Could still be z, z-partial-step or sigma
            # Check if all levels are equal
            dep_test1 = np.tile(
                self.grid["gdept"][0, 0, 0, :],
                (self.grid["gdept"].shape[1], self.grid["gdept"].shape[2], 1),
            )

            # Don't select levels within 2 grid cells of bathy to remove partial steps
            ind = self.grid["gdept"] <= self.grid["mbathy"]
            ind[0, :-2, ...] = ind[0, 2:, ...]
            dep_mask = np.ma.masked_where(ind is False, self.grid["gdept"])
            sel = np.nonzero(np.ma.max(dep_mask) == dep_mask)
            dep_test2 = np.tile(
                dep_mask[sel[0][0], :, sel[2][0], sel[3][0]],
                (self.grid["gdept"].shape[1], self.grid["gdept"].shape[2], 1),
            )

            # Check if any level away from bathy is variable in depth
            dep_test3 = (
                np.ma.min(dep_mask[0, ...], axis=[1, 2])
                == np.ma.max(dep_mask[0, ...], axis=[1, 2])
            ).all()

            if (dep_test1 == self.grid["gdept"][0, ...]).all():
                # z-level
                self.grid_type = "z"
            elif (dep_test2[ind] == self.grid["gdept"][ind]).all():
                # z-partial-step
                self.grid_type = "zps"
            elif dep_test3 is False:
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

    for vi in missing:
        if "gdep" in vi:
            if vi == "gdepw":
                grid[vi] = calc_gdep()
            elif hgr_type == "A":
                grid[vi] = grid[vi[:-1] + "t"]
            elif hgr_type == "B":
                grid[vi] = calc_gdep(grid["gdept"], "f")
            elif hgr_type == "C":
                grid[vi] = calc_gdep(grid["gdept"], vi)

    for vi in missing:
        if "e" in vi[0]:
            grid[vi] = calc_e3(grid["gdepw"])


def calc_gdep(gdept, lev):
    """
    Calculate missing glam or gphi from glamt or gphit.

    Args:
    ----
            gdept (np.array)  : mesh variable gdep on t-grid
            lev (str)         : grid level type (gdep or gdep of u, v, w, f)

    Returns:
    -------
            mesh_out (dict)     : horizontal grid mesh data variable
    """
    if "_0" in lev:
        dep_out = np.zeros((gdept.shape))

    if "u" in lev:
        None
    elif "v" in lev:
        None
    elif "w" in lev:
        None
    else:
        raise Exception("Grid level type must be z, zps or s.")

    return dep_out


def calc_e3(gdepw):
    """
    Calculate missing scale factors e3 from gdep.

    Args:
    ----
            glam (np.array)  : mesh variable glam or gphi on t-grid
            gphi (np.array)  : grid mesh type (glam or gphi of u, v, f)
            axis (int)       : the direction of distance for e1 this is 1,
                               for e2 this is 2

    Returns:
    -------
            e (np.array)     : horizontal distance scale factor e
    """
    gdepw[1:] - gdepw[:-1]
