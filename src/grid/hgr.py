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
"""

# External imports
import numpy as np

# Internal imports
from pybdy.reader.factory import GetFile


class H_grid:
    def __init__(self, SC, DC, settings, logger):
        """
        Master horizontal class.

        Args:
        ----
            SC (Source object)       : object with source grid info
            DC (Destination object)  : object with destination grid info
            settings (dict)          : dictionary of settings for loading data
            logger                   : log error and messages

        Returns:
        -------
            H_grid (object)          : horizontal grid object
        """
        # Set up variables
        self.settings = settings
        self.grid_type = ""
        self.grid = {}  # grid variables

        nc = GetFile(self.settings["src_hgr"])
        self.var_list = nc.variables.keys()
        nc.close()

        # Load what we can from grid file
        vars_want = [
            "glamt",
            "gphit",
            "glamf",
            "gphif",
            "glamu",
            "gphiu",
            "glamv",
            "gphiv",
            "e1t",
            "e2t",
            "e1f",
            "e2f",
            "e1u",
            "e2u",
            "e1v",
            "e2v",
        ]
        self.get_vars(vars_want)

        # Work out what sort of source grid we have
        self.find_hgrid_type()

        # Fill in missing variables we need for the grid type
        missing_vars = set(self.var_list) - set(vars_want)
        self.grid = fill_hgrid_vars(self.grid_type, self.grid, missing_vars)

        return self.grid

    def get_vars(self, vars_want):
        """
        Get the glam, gphi and e scale factors from file if possible.

        Args:
        ----
            vars_want (list)       : variables needed from file.
        """
        nc = GetFile(self.settings["src_hgr"])
        for vi in vars_want:
            if vi in self.var_list:
                self.grid[vi] = nc[vi][:]
        nc.close()

    def find_hgrid_type(self):
        """Find out what type of hoizontal grid is provided A, B or C."""
        if "glamt" in self.var_list:
            diff_lon = self.grid["glamu"] - self.grid["glamf"]
            diff_lat = self.grid["gphiu"] - self.grid["gphif"]
            if (diff_lon == 0).all() & (diff_lat == 0).all():
                self.grid_type = "B"
            else:
                self.grid_type = "C"
        elif "nav_lon" in self.var_list:
            self.logger.info(
                "Warning: glamt is not present in the grid file.\n"
                + "We are assuming everything is provide on the T-points."
            )
            nc = GetFile(self.settings["src_hgr"])
            self.grid["glamt"] = nc["nav_lon"][:, :]
            self.grid["gphit"] = nc["nav_lat"][:, :]
            nc.close()
            self.grid_type = "A"
        else:
            raise Exception("No nav_lon present in hgr file.")

        self.logger.info("Horizonal grid is type: " + self.sc_grid_type)


def fill_hgrid_vars(grid_type, grid, missing):
    """
    Calculate the missing horizontal grid variables and add them to grid.

    Args:
    ----
            grid_type (str)     : type of horizontal grid (A, B or C)
            grid (dict)         : dictionary of grid data variable
            missing (list)      : list of missing variables to calculate

    Returns:
    -------
            grid (dict)          : horizontal grid data dictionary
    """
    f_done = not (any(("glamf" in sub) | ("gphif" in sub) for sub in missing))
    if (f_done is False) & (grid_type == "B"):
        grid["glamf"] = calc_glam_gphi(grid["glamt"], "glamf")
        grid["gphif"] = calc_glam_gphi(grid["gphit"], "gphif")

    for vi in missing:
        if ("glam" in vi) | ("gphi" in vi):
            if grid_type == "A":
                grid[vi] = grid[vi[:-1] + "t"]
            elif grid_type == "B":
                if "f" not in vi:
                    grid[vi] = grid[vi[:-1] + "f"]
                else:
                    continue
            elif grid_type == "C":
                grid[vi] = calc_glam_gphi(grid[vi[:-1] + "t"], vi)

    for vi in missing:
        if "e" in vi[0]:
            grid[vi] = calc_e1_e2(
                grid["glam" + vi[-1]], grid["gphi" + vi[-1]], int(vi[1])
            )


def calc_glam_gphi(t_mesh, mesh):
    """
    Calculate missing glam or gphi from glamt or gphit.

    Args:
    ----
            t_mesh (np.array)  : mesh variable glam or gphi on t-grid
            mesh (str)         : grid mesh type (glam or gphi of u, v, f)

    Returns:
    -------
            mesh_out (dict)     : horizontal grid mesh data variable
    """
    mesh_out = np.zeros((t_mesh.shape))

    if "u" in mesh:
        mesh_out[:-1, :] = (t_mesh[:-1, :] + t_mesh[1:, :]) / 2
        diff = np.abs(mesh_out[-2, :] - t_mesh[-1, :])
        mesh_out[-1, :] = t_mesh[-1, :] + diff
    elif "v" in mesh:
        mesh_out[:, :-1] = (t_mesh[:, :-1] + t_mesh[:, 1:]) / 2
        diff = np.abs(mesh_out[:, -2] - t_mesh[:, -1])
        mesh_out[:, -1] = t_mesh[:, -1] + diff
    elif "f" in mesh:
        mesh_out[:-1, :-1] = (
            t_mesh[:-1, :-1] + t_mesh[1:, 1:] + t_mesh[1:, :-1] + t_mesh[:-1, 1:]
        ) / 4
        diff = np.abs(mesh_out[-2, :] - t_mesh[-1, :])
        mesh_out[-1, :] = t_mesh[-1, :] + diff
        diff = np.abs(mesh_out[:, -2] - t_mesh[:, -1])
        mesh_out[:, -1] = t_mesh[:, -1] + diff
    else:
        raise Exception("Grid mesh type must be u, v or f.")

    return mesh_out


def calc_e1_e2(glam, gphi, axis):
    """
    Calculate missing scale factor e1 and e2 from glam or gphi.

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
    ij = axis - 1
    ra = 6371  # Average radius of earth in kilometers
    e_lam_term = (np.gradient(glam, axis=ij) * np.cos(gphi)) ** 2
    e_phi_term = np.gradient(gphi, axis=ij) ** 2
    e = ra * ((e_lam_term + e_phi_term) ** 0.5)

    # e1 = (ra * ((((glam[1:, :] - glam[:-1. :]) * np.cos(gphi)) ** 2)
    #      + ((gphi[1:, :] - gphi[:1, :]) ** 2)) ** 0.5)

    # e2 = (ra * (((np.gradient(glam, axis=1) * np.cos(gphi)) ** 2)
    #      + (np.gradient(gphi, axis=1) ** 2)) ** 0.5)
    return e
