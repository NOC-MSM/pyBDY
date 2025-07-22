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


"""
Create a Tide netcdf file ready for population.

@author: Mr. Srikanth Nagella
"""

import datetime
import logging

from netCDF4 import Dataset


def CreateBDYTideNetcdfFile(filename, xb_len, x_len, y_len, h, fv, grd):
    # Additional dimension lengths Lengths
    yb_len = 1

    # Enter define mode
    ncid = Dataset(filename, "w", clobber=True, format="NETCDF4")

    # define dimensions
    ncid.createDimension("xb", xb_len)
    ncid.createDimension("yb", yb_len)
    ncid.createDimension("x", x_len)
    ncid.createDimension("y", y_len)

    # define variable
    varlonID = ncid.createVariable(
        "nav_lon",
        "f4",
        (
            "y",
            "x",
        ),
    )
    varlatID = ncid.createVariable(
        "nav_lat",
        "f4",
        (
            "y",
            "x",
        ),
    )

    if grd == "T":
        varmskID = ncid.createVariable(
            "bdy_msk",
            "f4",
            (
                "y",
                "x",
            ),
            fill_value=fv,
        )
        varz1ID = ncid.createVariable(
            "z1",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varz2ID = ncid.createVariable(
            "z2",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    elif grd == "U":
        varu1ID = ncid.createVariable(
            "u1",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varu2ID = ncid.createVariable(
            "u2",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    elif grd == "V":
        varv1ID = ncid.createVariable(
            "v1",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varv2ID = ncid.createVariable(
            "v2",
            "f4",
            (
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    else:
        logging.error("Unknown Grid input")

    varnbiID = ncid.createVariable(
        "nbidta",
        "i4",
        (
            "yb",
            "xb",
        ),
    )
    varnbjID = ncid.createVariable(
        "nbjdta",
        "i4",
        (
            "yb",
            "xb",
        ),
    )
    varnbrID = ncid.createVariable(
        "nbrdta",
        "i4",
        (
            "yb",
            "xb",
        ),
    )
    # Global Attributes
    ncid.file_name = filename
    ncid.creation_date = str(datetime.datetime.now())
    ncid.history = h
    ncid.institution = "National Oceanography Centre, Liverpool, U.K."

    # Longitude axis attributes
    varlonID.axis = "Longitude"
    varlonID.short_name = "nav_lon"
    varlonID.units = "degrees_east"
    varlonID.long_name = "Longitude"

    # Latitude axis attributes
    varlatID.axis = "Latitude"
    varlatID.short_name = "nav_lat"
    varlatID.units = "degrees_east"
    varlatID.long_name = "Latitude"

    # nbidta attributes
    varnbiID.short_name = "nbidta"
    varnbiID.units = "unitless"
    varnbiID.long_name = "Bdy i indices"

    # nbjdta attributes
    varnbjID.short_name = "nbjdta"
    varnbjID.units = "unitless"
    varnbjID.long_name = "Bdy j indices"

    # nbrdta attributes
    varnbrID.short_name = "nbrdta"
    varnbrID.units = "unitless"
    varnbrID.long_name = "Bdy discrete distance"
    if grd == "T":
        varmskID.short_name = "bdy_msk"
        varmskID.units = "unitless"
        varmskID.long_name = "Structured boundary mask"

        varz1ID.units = "m"
        varz1ID.short_name = "z1"
        varz1ID.long_name = "tidal elevation: cosine"
        varz1ID.grid = "bdyT"

        varz2ID.units = "m"
        varz2ID.short_name = "z2"
        varz2ID.long_name = "tidal elevation: sine"
        varz2ID.grid = "bdyT"

    elif grd == "U":
        varu1ID.units = "m/s"
        varu1ID.short_name = "u1"
        varu1ID.long_name = "tidal east velocity: cosine"
        varu1ID.grid = "bdyU"

        varu2ID.units = "m/s"
        varu2ID.short_name = "u2"
        varu2ID.long_name = "tidal east velocity: sine"
        varu2ID.grid = "bdyU"

    elif grd == "V":
        varv1ID.units = "m/s"
        varv1ID.short_name = "v1"
        varv1ID.long_name = "tidal north velocity: cosine"
        varv1ID.grid = "bdyV"

        varv2ID.units = "m/s"
        varv2ID.short_name = "v2"
        varv2ID.long_name = "tidal north velocity: sine"
        varv2ID.grid = "bdyV"

    else:
        logging.error("Unknown Grid")

    ncid.close()
