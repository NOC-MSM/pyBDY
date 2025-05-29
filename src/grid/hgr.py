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
"""

# External imports
import json
import warnings

import numpy as np

# Internal imports
from pybdy.reader.factory import GetFile


class H_Grid:
    def __init__(self, hgr_file, name_map_file, logger, dst=1):
        """
        Master horizontal class.

        Args:
        ----
            hgr_file (str)           : string of file for loading hgr data
            name_map_file (str)      : string of file for mapping variable names
            logger (object)          : log error and messages
            dst (bool)               : flag for destination (true) or source (false)

        Returns:
        -------
            H_grid (object)          : horizontal grid object
        """
        # Set up variables
        self.file_path = hgr_file
        self.name_map = name_map_file
        self.logger = logger
        self.dst = dst
        self.grid_type = ""
        self.grid = {}  # grid variables

        # TODO: enable .ncml option for loading variables
        if ".ncml" in self.file_path:
            raise Exception("Use .nc file for hgr input not .ncml")

        nc = GetFile(self.file_path)
        self.var_list = nc.nc.variables.keys()
        nc.close()

        # Load what we can from grid file
        vars_want = [
            "nav_lon",
            "nav_lat",
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
        missing_vars = sorted(list(set(vars_want) - set(self.var_list)))
        self.grid = fill_hgrid_vars(self.grid_type, self.grid, missing_vars)
        self.var_list = list(self.grid.keys())

    def get_vars(self, vars_want):
        """
        Get the glam, gphi and e scale factors from file if possible.

        Args:
        ----
            vars_want (list)       : variables needed from file.
        """
        # find the variables that have been name mapped
        if self.dst:
            vm = "dst_"
        else:
            vm = "sc_"

        with open(self.name_map, "r") as j:
            nm = json.loads(j.read())[vm + "variable_map"]

        name_map_k = list(nm.keys())
        name_map_v = list(nm.values())
        nm_var_list = []
        for i in range(len(name_map_v)):
            if name_map_v[i] in self.var_list:
                nm_var_list.append(name_map_k[i])

        # get variables from file
        nc = GetFile(self.file_path)
        for vi in vars_want:
            if vi in nm_var_list:
                grid_tmp = nc.nc[nm[vi]][:]  # [t, y, x]
                if len(grid_tmp.shape) == 3:
                    self.grid[vi] = grid_tmp
                elif len(grid_tmp.shape) == 2:
                    self.grid[vi] = grid_tmp[np.newaxis, :, :]
                else:
                    warnings.warn(
                        nm[vi]
                        + " shape "
                        + grid_tmp.shape
                        + " does not match required dimensions [t, y, x]"
                    )
                    # We can calculate the var later if the wrong size
                    continue
        nc.close()
        self.var_list = list(self.grid.keys())

    def find_hgrid_type(self):
        """Find out what type of hoizontal grid is provided A, B or C."""
        if (
            ("glamt" in self.var_list)
            & ("glamu" in self.var_list)
            & ("glamv" in self.var_list)
        ):
            diff_lon1 = self.grid["glamt"] - self.grid["glamu"]
            diff_lat1 = self.grid["gphit"] - self.grid["gphiu"]
            if (diff_lon1 == 0).all() & (diff_lat1 == 0).all():
                self.grid_type = "A"
            else:
                self.grid_type = "C"

            if "glamf" in self.var_list:
                diff_lon2 = self.grid["glamu"] - self.grid["glamf"]
                diff_lat2 = self.grid["gphiu"] - self.grid["gphif"]
                if (diff_lon2 == 0).all() & (diff_lat2 == 0).all():
                    self.grid_type = "B"

        elif "nav_lon" in self.var_list:
            self.logger.info(
                "Warning: glam is not present in the grid file.\n"
                + "We are assuming everything is provide on the T-points."
            )
            self.grid["glamt"] = self.grid["nav_lon"]
            self.grid["gphit"] = self.grid["nav_lat"]
            self.grid_type = "A"
        else:
            raise Exception("No nav_lon present in hgr file.")

        if "nav_lon" in self.var_list:
            del self.grid["nav_lon"]
        if "nav_lat" in self.var_list:
            del self.grid["nav_lat"]
        self.var_list = list(self.grid.keys())
        self.logger.info("Horizonal grid is type: " + self.grid_type)


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
        grid["glamf"] = calc_grid_from_t(grid["glamt"], "glamf")
        grid["gphif"] = calc_grid_from_t(grid["gphit"], "gphif")
        missing = sorted(list(set(missing) - set(["glamf", "gphif"])))

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
                grid[vi] = calc_grid_from_t(grid[vi[:-1] + "t"], vi)

    for vi in missing:
        if "e" in vi[0]:
            grid[vi] = calc_e1_e2(
                grid["glam" + vi[-1]], grid["gphi" + vi[-1]], int(vi[1])
            )
    return grid


def calc_grid_from_t(t_mesh, mesh):
    """
    Calculate missing glam, gphi or gdep from t-grid.

    Args:
    ----
            t_mesh (np.array)  : mesh variable glam or gphi on t-grid
            mesh (str)         : grid mesh type (glam, gphi, or gdep of u, v, f)

    Returns:
    -------
            mesh_out (dict)     : horizontal grid mesh data variable
    """
    mesh_out = np.zeros((t_mesh.shape))

    if "v" in mesh:
        mesh_out[..., :-1, :] = (t_mesh[..., :-1, :] + t_mesh[..., 1:, :]) / 2
        diff = np.abs(mesh_out[..., -2, :] - t_mesh[..., -1, :])
        mesh_out[..., -1, :] = t_mesh[..., -1, :] + diff
    elif "u" in mesh:
        mesh_out[..., :, :-1] = (t_mesh[..., :, :-1] + t_mesh[..., :, 1:]) / 2
        diff = np.abs(mesh_out[..., :, -2] - t_mesh[..., :, -1])
        mesh_out[..., :, -1] = t_mesh[..., :, -1] + diff
    elif "f" in mesh:
        mesh_out[..., :-1, :-1] = (
            t_mesh[..., :-1, :-1]
            + t_mesh[..., 1:, 1:]
            + t_mesh[..., 1:, :-1]
            + t_mesh[..., :-1, 1:]
        ) / 4
        diff = np.abs(mesh_out[..., -2, :] - t_mesh[..., -1, :])
        mesh_out[..., -1, :] = t_mesh[..., -1, :] + diff
        diff = np.abs(mesh_out[..., :, -2] - t_mesh[..., :, -1])
        mesh_out[..., :, -1] = t_mesh[..., :, -1] + diff
    else:
        raise Exception("Grid mesh type must be u, v or f.")

    return mesh_out


def calc_e1_e2(glam, gphi, ij):
    """
    Calculate missing scale factor e1 and e2 from glam or gphi.

    Args:
    ----
            glam (np.array)  : mesh variable glam (lon) [time, j, i]
            gphi (np.array)  : mesh variable gphi (lat) [time, j, i]
            ij (int)         : ij direction 1 (i or x direction) or 2 (j or y direction)

    Returns:
    -------
            e (np.array)     : horizontal distance scale factor e
    """
    if ij == 1:
        axis = 2
    elif ij == 2:
        axis = 1
    else:
        raise Exception("ij must to be 1 or 2.")

    ra = 6371229  # Radius of earth in meters from NEMO phycst.F90
    glam = glam * (np.pi / 180)
    gphi = gphi * (np.pi / 180)

    e_lam_term = (np.gradient(glam, axis=axis) * np.cos(gphi)) ** 2
    e_phi_term = np.gradient(gphi, axis=axis) ** 2
    e = ra * ((e_lam_term + e_phi_term) ** 0.5)

    # Correction for outer edges
    if axis == 2:
        e[..., 0] = e[..., 1] - (e[..., 2] - e[..., 1])
        e[..., -1] = e[..., -2] - (e[..., -3] - e[..., -2])
    else:
        e[..., 0, :] = e[..., 1, :] - (e[..., 2, :] - e[..., 1, :])
        e[..., -1, :] = e[..., -2, :] - (e[..., -3, :] - e[..., -2, :])

    return e
