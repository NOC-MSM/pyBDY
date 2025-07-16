# ===================================================================
# Copyright 2025 National Oceanography Centre
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================

########################################################
# Creates Nemo bdy indices for t, u, v points          #
##                                                    ##
# Written by John Kazimierz Farey, started 30 Aug 2012 #
# Port of Matlab code by James Harle                   #
########################################################

"""
Module that combines matlab coord gen and pop.

Initialise with netcdf file name and dictionary containing all bdy grids (objects).
"""

import logging
from datetime import datetime

from netCDF4 import Dataset


class Coord:
    """Class for writing boundayr coordinate data to netcdf file."""

    def __init__(self, fname, bdy_ind):
        """
        Create Nemo bdy indices for t, u, v points.

        Parameters
        ----------
        fname           (str) : file name of coords file for output
        bdy_ind (numpy.array) : indicies of bdy points

        Returns
        -------
        None   : object
        """
        self._grid = ["t", "u", "v"]
        self.bdy_ind = bdy_ind
        self.logger = logging.getLogger(__name__)
        self.logger.debug(fname)
        if not fname:
            print("need some error handling in here or is this redundant?")  # TODO

        # Enter define mode
        self.ncid = Dataset(fname, "w", clobber=True, format="NETCDF4")

        # Define Dimensions
        self.dim_id = self.create_dims()

        # Create tidy dictionaries to hold all our pretty variables
        self.var_nb_ij_id = self.build_dict(["i", "j"], ["nb", "i4", "unitless", 0])
        self.var_nb_r_id = self.build_dict(["r"], ["nb", "i4", "unitless", 0])
        self.var_g_lamphi_id = self.build_dict(
            ["lam", "phi"], ["g", "f4", "degrees_east", "longitude"]
        )
        self.var_e_12_id = self.build_dict(
            ["1", "2"], ["e", "f4", "metres", "scale factor"]
        )

        # Assign Global Attributes
        self.ncid.file_name = fname
        self.ncid.creation_date = str(datetime.now())
        self.ncid.institution = "National Oceanography Centre, Liverpool, U.K."

        # Leave Define Mode

    def closeme(self):
        self.ncid.close()

    def create_dims(self):
        """Create dims and returns a dictionary of them."""
        ret = {"xb": {}}
        ret["xb"]["t"] = self.ncid.createDimension("xbT", len(self.bdy_ind["t"].bdy_i))
        ret["xb"]["u"] = self.ncid.createDimension("xbU", len(self.bdy_ind["u"].bdy_i))
        ret["xb"]["v"] = self.ncid.createDimension("xbV", len(self.bdy_ind["v"].bdy_i))
        ret["yb"] = self.ncid.createDimension("yb", 1)

        return ret

    def build_dict(self, dim, units):
        """Set up a grid dictionary."""
        ret = {}
        for g in self._grid:
            ret[g] = {}
            for d in dim:
                ret[g][d] = self.add_vars(d, g, units)

        return ret

    def add_vars(self, dim, grd, unt):
        """Create a var w/ attributes."""
        dat = unt[2]
        lname = unt[3]
        if dim == "phi":
            dat = "degrees_north"
            lname = "latitude"
        elif lname == 0:
            lname = "Bdy %s indices" % dim
        lname = lname + " (%s)" % grd.upper()
        # print '%s%s%s'%(unt[0],dim,grd)
        # print unt[1]
        var = self.ncid.createVariable(
            "%s%s%s" % (unt[0], dim, grd), unt[1], ("yb", "xb" + grd.upper())
        )
        var.short_name = "%s%s%s" % (unt[0], dim, grd)
        var.units = dat
        var.long_name = lname

        return var

    def populate(self, hgr):
        """Populate the file with indices, lat, lon, and e dimensions."""
        self.set_lenvar(self.var_nb_ij_id)
        self.set_lenvar(self.var_nb_r_id)

        self.set_lenvar(self.var_g_lamphi_id, hgr, "g")
        self.set_lenvar(self.var_e_12_id, hgr, "e")

        self.closeme()

    def set_lenvar(self, vardic, hgr=None, unt=None):
        """
        Set the len var of each array in the var dictionary.

        Use by specifying hgr and unt which pulls data from loaded grid data.
        Otherwise pull it from the class dict.
        """
        for ind in vardic:
            x = 0
            data = None
            for dim in vardic[ind]:
                if hgr is not None:
                    data = hgr.grid["%s%s%s" % (unt, dim, ind)][:]
                    self.logger.debug(
                        "%s %s %s %s %s %s",
                        ind,
                        self.bdy_ind[ind].bdy_i[:, 1],
                        data.shape,
                        dim,
                        unt,
                        ind,
                    )
                    data = data.squeeze()
                    self.logger.debug(
                        "%s %s %s", ind, self.bdy_ind[ind].bdy_i[:, 1], data.shape
                    )
                    data = data[
                        (self.bdy_ind[ind].bdy_i[:, 1]), (self.bdy_ind[ind].bdy_i[:, 0])
                    ]
                elif len(vardic[ind]) == 1:
                    data = self.bdy_ind[ind].bdy_r[:]
                else:
                    data = self.bdy_ind[ind].bdy_i[:, x]
                    x = 1

                getattr(vardic[ind][dim], "long_name")
                # print 'Just about to add 1 to ', attData
                # add 1 to all indices as they're going to be used in
                # a Fortran environment
                # This is commented because data generated doesn't match
                # with output generated from matlab
                data = data + 1

                vardic[ind][dim][:] = data
