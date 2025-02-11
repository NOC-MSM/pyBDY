"""
Create a Nemo Bdy netCDF file ready for population.

Written by John Kazimierz Farey, started August 30, 2012
Port of Matlab code of James Harle
"""
import datetime
import logging

from netCDF4 import Dataset


def CreateBDYNetcdfFile(
    filename, xb_len, x_len, y_len, depth_len, rw, h, orig, fv, calendar, grd
):
    """Create a template of bdy netcdf files. A common for T, I, U, V, E grid types."""
    gridNames = ["T", "I", "U", "V", "E", "Z"]  # All possible grids

    # Additional dimension lengths
    yb_len = 1

    # Enter define mode
    ncid = Dataset(filename, "w", clobber=True, format="NETCDF4")

    # define dimensions
    if grd in gridNames and grd != "Z":  # i.e grid NOT barotropic (Z)
        ncid.createDimension("z", depth_len)
    else:
        logging.error("Grid tpye not known")
    ncid.createDimension("xb", xb_len)
    ncid.createDimension("yb", yb_len)
    ncid.createDimension("x", x_len)
    ncid.createDimension("y", y_len)
    ncid.createDimension("time_counter", None)

    # define variable
    vartcID = ncid.createVariable("time_counter", "f8", ("time_counter",))
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

    if grd in ["E"]:
        varztID = ncid.createVariable(
            "gdept",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varmskID = ncid.createVariable(
            "bdy_msk",
            "f4",
            (
                "y",
                "x",
            ),
            fill_value=fv,
        )
        varN1pID = ncid.createVariable(
            "N1p",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varN3nID = ncid.createVariable(
            "N3n",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varN5sID = ncid.createVariable(
            "N5s",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    elif grd in ["T", "I"]:
        varztID = ncid.createVariable(
            "gdept",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        vardzID = ncid.createVariable(
            "e3t",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varmskID = ncid.createVariable(
            "bdy_msk",
            "f4",
            (
                "y",
                "x",
            ),
            fill_value=fv,
        )
        vartmpID = ncid.createVariable(
            "votemper",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varsalID = ncid.createVariable(
            "vosaline",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varsshID = ncid.createVariable(
            "sossheig",
            "f4",
            (
                "time_counter",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        if grd == "I":
            varildID = ncid.createVariable(
                "ileadfra",
                "f4",
                (
                    "time_counter",
                    "yb",
                    "xb",
                ),
                fill_value=fv,
            )
            variicID = ncid.createVariable(
                "iicethic",
                "f4",
                (
                    "time_counter",
                    "yb",
                    "xb",
                ),
                fill_value=fv,
            )
            varisnID = ncid.createVariable(
                "isnowthi",
                "f4",
                (
                    "time_counter",
                    "yb",
                    "xb",
                ),
                fill_value=fv,
            )
    elif grd == "U":
        varztID = ncid.createVariable(
            "gdepu",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        vardzID = ncid.createVariable(
            "e3u",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varbtuID = ncid.createVariable(
            "vobtcrtx",
            "f4",
            (
                "time_counter",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        vartouID = ncid.createVariable(
            "vozocrtx",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    elif grd == "V":
        varztID = ncid.createVariable(
            "gdepv",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        vardzID = ncid.createVariable(
            "e3v",
            "f4",
            (
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varbtvID = ncid.createVariable(
            "vobtcrty",
            "f4",
            (
                "time_counter",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        vartovID = ncid.createVariable(
            "vomecrty",
            "f4",
            (
                "time_counter",
                "z",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
    elif grd == "Z":
        varsshID = ncid.createVariable(
            "sossheig",
            "f4",
            (
                "time_counter",
                "yb",
                "xb",
            ),
            fill_value=fv,
        )
        varmskID = ncid.createVariable(
            "bdy_msk",
            "f4",
            (
                "y",
                "x",
            ),
            fill_value=fv,
        )
    else:
        logging.error("Unknow Grid input")

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
    ncid.rim_width = rw
    ncid.history = h
    ncid.institution = "National Oceanography Centre, Liverpool, U.K."

    # Time axis attributes
    vartcID.axis = "T"
    vartcID.standard_name = "time"
    vartcID.units = "seconds since " + orig
    vartcID.title = "Time"
    vartcID.long_name = "Time axis"
    vartcID.time_origin = orig
    vartcID.calendar = calendar

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
    if grd == "E":
        varztID.axis = "Depth"
        varztID.short_name = "gdept"
        varztID.units = "m"
        varztID.long_name = "Depth"

        vardzID.axis = "Depth"
        vardzID.short_name = "e3t"
        vardzID.units = "m"
        vardzID.long_name = "Cell Thickness"

        varmskID.short_name = "bdy_msk"
        varmskID.units = "unitless"
        varmskID.long_name = "Structured boundary mask"

        varN1pID.units = "mmol/m^3"
        varN1pID.short_name = "N1p"
        varN1pID.long_name = "Phosphate"
        varN1pID.grid = "bdyT"

        varN3nID.units = "mmol/m^3"
        varN3nID.short_name = "N3n"
        varN3nID.long_name = "Nitrate"
        varN3nID.grid = "bdyT"

        varN5sID.units = "mmol/m^3"
        varN5sID.short_name = "N5s"
        varN5sID.long_name = "Silicate"
        varN5sID.grid = "bdyT"

    if grd in ["T", "I"]:
        varztID.axis = "Depth"
        varztID.short_name = "gdept"
        varztID.units = "m"
        varztID.long_name = "Depth"

        vardzID.axis = "Depth"
        vardzID.short_name = "e3t"
        vardzID.units = "m"
        vardzID.long_name = "Cell Thickness"

        varmskID.short_name = "bdy_msk"
        varmskID.units = "unitless"
        varmskID.long_name = "Structured boundary mask"

        vartmpID.units = "C"
        vartmpID.short_name = "votemper"
        vartmpID.long_name = "Temperature"
        vartmpID.grid = "bdyT"

        varsalID.units = "PSU"
        varsalID.short_name = "vosaline"
        varsalID.long_name = "Salinity"
        varsalID.grid = "bdyT"

        if grd == "I":
            varildID.units = "%"
            varildID.short_name = "ildsconc"
            varildID.long_name = "Ice lead fraction"
            varildID.grid = "bdyT"

            variicID.units = "m"
            variicID.short_name = "iicethic"
            variicID.long_name = "Ice thickness"
            variicID.grid = "bdyT"

            varisnID.units = "m"
            varisnID.short_name = "isnowthi"
            varisnID.long_name = "Snow thickness"
            varisnID.grid = "bdyT"
    elif grd == "U":
        varztID.axis = "Depth"
        varztID.short_name = "gdepu"
        varztID.units = "m"
        varztID.long_name = "Depth"

        vardzID.axis = "Depth"
        vardzID.short_name = "e3u"
        vardzID.units = "m"
        vardzID.long_name = "Cell Thickness"

        varbtuID.units = "m/s"
        varbtuID.short_name = "vobtcrtx"
        varbtuID.long_name = "Thickness-weighted depth-averaged zonal Current"
        varbtuID.grid = "bdyU"

        vartouID.units = "m/s"
        vartouID.short_name = "vozocrtx"
        vartouID.long_name = "Zonal Current"
        vartouID.grid = "bdyU"

    elif grd == "V":
        varztID.axis = "Depth"
        varztID.short_name = "gdepv"
        varztID.units = "m"
        varztID.long_name = "Depth"

        vardzID.axis = "Depth"
        vardzID.short_name = "e3v"
        vardzID.units = "m"
        vardzID.long_name = "Cell Thickness"

        varbtvID.units = "m/s"
        varbtvID.short_name = "vobtcrty"
        varbtvID.long_name = "Thickness-weighted depth-averaged meridional Current"
        varbtvID.grid = "bdyV"

        vartovID.units = "m/s"
        vartovID.short_name = "vomecrty"
        vartovID.long_name = "Meridional Current"
        vartovID.grid = "bdyV"

    elif grd == "Z":
        varsshID.units = "m"
        varsshID.short_name = "sossheig"
        varsshID.long_name = "Sea Surface Height"
        varsshID.grid = "bdyT"

        varmskID.short_name = "bdy_msk"
        varmskID.units = "unitless"
        varmskID.long_name = "Structured boundary mask"

    else:
        logging.error("Unknown Grid")

    ncid.close()
