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
    def __init__(self, SC, DC, settings, logger):
        """
        Master depth class.

        Args:
        ----
            SC (Source object)       : object with source grid info
            DC (Destination object)  : object with destination grid info
            settings (dict)          : dictionary of settings for loading data
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
        set(self.var_list) - set(vars_want)
        # self.grid = fill_zgrid_vars(self.grid_type, self.grid, missing_vars)

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
            raise Exception("No gdept or gdept_0 variable present.")
        elif "gdept" not in self.var_list:
            self.grid_type = "z"
        else:
            # Could still be z, z-partial-step or sigma
            dep_test = np.tile(
                self.gdept[0, 0, 0, :], (self.gdept.shape[1], self.gdept.shape[2], 1)
            )
            if (dep_test == self.gdept[0, :, :, :]).all():
                self.grid_type = "z"
            # elif
