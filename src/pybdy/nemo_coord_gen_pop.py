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
    _grid = ["t", "u", "v"]

    # Init with nc fname and dictionary of bdy inds
    def __init__(self, fname, bdy_ind):
        self.bdy_ind = bdy_ind
        self.logger = logging.getLogger(__name__)
        self.logger.debug(fname)
        if not fname:
            print("need some error handling in here or is this redundant?")  # TODO

        # Enter define mode
        self.ncid = Dataset(fname, "w", clobber=True, format="NETCDF4")

        # Define Dimensions
        self.dim_id = self._create_dims()

        # Create tidy dictionaries to hold all our pretty variables
        self.var_nb_ij_id = self._build_dict(["i", "j"], ["nb", "i4", "unitless", 0])
        self.var_nb_r_id = self._build_dict(["r"], ["nb", "i4", "unitless", 0])
        self.var_g_lamphi_id = self._build_dict(
            ["lam", "phi"], ["g", "f4", "degrees_east", "longitude"]
        )
        self.var_e_12_id = self._build_dict(
            ["1", "2"], ["e", "f4", "metres", "scale factor"]
        )

        # Assign Global Attributes
        self.ncid.file_name = fname
        self.ncid.creation_date = str(datetime.now())
        self.ncid.institution = "National Oceanography Centre, Liverpool, U.K."

        # Leave Define Mode

    # # # # # # # # #
    # # Functions # #
    # # # # # # # # #

    def closeme(self):
        self.ncid.close()

    # Creates dims and returns a dictionary of them
    def _create_dims(self):
        ret = {"xb": {}}
        ret["xb"]["t"] = self.ncid.createDimension("xbT", len(self.bdy_ind["t"].bdy_i))
        ret["xb"]["u"] = self.ncid.createDimension("xbU", len(self.bdy_ind["u"].bdy_i))
        ret["xb"]["v"] = self.ncid.createDimension("xbV", len(self.bdy_ind["v"].bdy_i))
        ret["yb"] = self.ncid.createDimension("yb", 1)

        return ret

    # Sets up a grid dictionary
    def _build_dict(self, dim, units):
        ret = {}
        for g in self._grid:
            ret[g] = {}
            for d in dim:
                ret[g][d] = self._add_vars(d, g, units)

        return ret

    # creates a var w/ attributes
    def _add_vars(self, dim, grd, unt):
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

    def populate(self, ncfname):
        self.set_lenvar(self.var_nb_ij_id)
        self.set_lenvar(self.var_nb_r_id)

        ncid2 = Dataset(ncfname, "r")
        self.set_lenvar(self.var_g_lamphi_id, ncid2, "g")
        self.set_lenvar(self.var_e_12_id, ncid2, "e")
        ncid2.close()

        self.closeme()

    # sets the len var of each array in the var dictionary fed
    # specifying nc and unt pulls data from a secondary file
    # Otherwise pull it from the class dict
    def set_lenvar(self, vardic, nc=None, unt=None):
        for ind in vardic:
            x = 0
            data = None
            for dim in vardic[ind]:
                if nc is not None:
                    data = nc.variables["%s%s%s" % (unt, dim, ind)][:]
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
