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
Created on Wed Sep 12 08:02:46 2012.

The main application script for the NRCT.

@author James Harle
@author John Kazimierz Farey
@author Srikanth Nagella
"""

# External imports
import datetime as dt
import logging
import time

import numpy as np
from grid import hgr, zgr
from PyQt5.QtWidgets import QMessageBox

# Local imports
from pybdy import nemo_bdy_chunk as chunk_func
from pybdy import nemo_bdy_dst_coord as dst_coord
from pybdy import nemo_bdy_extr_tm3 as extract
from pybdy import nemo_bdy_gen_c as gen_grid
from pybdy import nemo_bdy_ncpop as ncpop
from pybdy import nemo_bdy_setup as setup
from pybdy import nemo_bdy_source_coord as source_coord
from pybdy import nemo_bdy_zgrv2 as zgrv
from pybdy import nemo_coord_gen_pop as coord
from pybdy import pybdy_settings_editor
from pybdy.gui.nemo_bdy_mask import Mask as Mask_File
from pybdy.reader import factory
from pybdy.tide import nemo_bdy_tide3 as tide
from pybdy.tide import nemo_bdy_tide_ncgen
from pybdy.utils import Constants


class Grid(object):
    """A Grid object that stores bdy grid information."""

    def __init__(self):
        self.bdy_i = None  # bdy indices
        self.bdy_r = None  # associated rimwidth values
        self.grid_type = None  # this can be T/U/V
        self.fname_2 = None  # 2nd file for vector rotation
        self.max_i = None  # length of i-axis in fname_2
        self.max_j = None  # length of j-axis in fname_2
        self.source_time = None  # netcdftime information from parent files


logger = logging.getLogger(__name__)
logging.basicConfig(filename="nrct.log", level=logging.INFO)


def process_bdy(setup_filepath=0, mask_gui=False):
    """
    Handle all the calls to generate open boundary conditions for a given regional domain.

    Notes
    -----
    This is main entry for processing BDY lateral boundary conditions.
    This is the main script that handles all the calls to generate open
    boundary conditions for a given regional domain. Input options are handled
    in a NEMO style namelist (namelist.bdy). There is an optional GUI allowing
    the user to create a mask that defines the extent of the regional model.

    Parameters
    ----------
        setup_filepath (str) : file path to find namelist.bdy
        mask_gui       (bool): whether use of the GUI is required

    Returns
    -------
        None          : bdy data is written out to NetCDF file

    """
    # Start Logger
    logger.info("Start NRCT Logging: " + time.asctime())
    logger.info("============================================")

    SourceCoord = source_coord.SourceCoord()
    DstCoord = dst_coord.DstCoord()

    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings

    logger.info("Reading setup completed")

    bdy_msk = _get_mask(Setup, mask_gui)
    DstCoord.bdy_msk = bdy_msk == 1
    logger.info("Reading mask completed")

    DstCoord.hgr = hgr.H_Grid(settings["dst_hgr"], settings["nme_map"], logger, dst=1)
    DstCoord.zgr = zgr.Z_Grid(
        settings["dst_zgr"],
        settings["nme_map"],
        DstCoord.hgr.grid_type,
        DstCoord.hgr.grid,
        logger,
        dst=1,
    )
    logger.info("Reading dst grid completed")

    bdy_ind = {}  # define a dictionary to hold the grid information

    for grd in ["t", "u", "v"]:
        bdy_ind[grd] = gen_grid.Boundary(bdy_msk, settings, grd)
        logger.info("Generated BDY %s information", grd)
        logger.info("Grid %s has shape %s", grd, bdy_ind[grd].bdy_i.shape)

        # function to split the bdy into several boundary chunks
        bdy_ind[grd].chunk_number = chunk_func.chunk_bdy(bdy_ind[grd])

    if Setup.bool_settings["coords_file"]:
        # Write out grid information to coordinates.bdy.nc
        co_set = coord.Coord(
            settings["dst_dir"] + "/" + settings["coords_file"], bdy_ind
        )
        co_set.populate(DstCoord.hgr)
        logger.info("File: coordinates.bdy.nc generated and populated")

    # Idenitify number of boundary points
    nbdy = {}

    for grd in ["t", "u", "v"]:
        nbdy[grd] = len(bdy_ind[grd].bdy_i[:, 0])

    # Assign horizontal grid data

    DstCoord.lonlat = {"t": {}, "u": {}, "v": {}}
    for grd in ["t", "u", "v"]:
        DstCoord.lonlat[grd]["lon"] = DstCoord.hgr.grid["glam" + grd][0, :, :]
        DstCoord.lonlat[grd]["lat"] = DstCoord.hgr.grid["gphi" + grd][0, :, :]

    logger.info("Grid coordinates defined")

    # Identify lons/lats of the BDY points

    DstCoord.bdy_lonlat = {"t": {}, "u": {}, "v": {}}

    for grd in ["t", "u", "v"]:
        for geo_crd in ["lon", "lat"]:
            DstCoord.bdy_lonlat[grd][geo_crd] = np.zeros(nbdy[grd])

    for grd in ["t", "u", "v"]:
        for i in range(nbdy[grd]):
            x = bdy_ind[grd].bdy_i[i, 1]
            y = bdy_ind[grd].bdy_i[i, 0]
            DstCoord.bdy_lonlat[grd]["lon"][i] = DstCoord.lonlat[grd]["lon"][x, y]
            DstCoord.bdy_lonlat[grd]["lat"][i] = DstCoord.lonlat[grd]["lat"][x, y]

        DstCoord.lonlat[grd]["lon"][DstCoord.lonlat[grd]["lon"] > 180] -= 360

    logger.info("BDY lons/lats identified from %s", settings["dst_hgr"])

    # Gather grid information

    logger.info("Gathering src grid information")
    SourceCoord.hgr = hgr.H_Grid(
        settings["src_hgr"], settings["nme_map"], logger, dst=0
    )
    SourceCoord.zgr = zgr.Z_Grid(
        settings["src_zgr"],
        settings["nme_map"],
        SourceCoord.hgr.grid_type,
        SourceCoord.hgr.grid,
        logger,
        dst=0,
    )

    # Fill horizontal grid information

    try:  # if they are masked array convert them to normal arrays
        SourceCoord.hgr.grid["glamt"] = SourceCoord.hgr.grid["glamt"].filled()  # lon
    except Exception:
        logger.debug("Not a masked array.")
    try:
        SourceCoord.hgr.grid["gphit"] = SourceCoord.hgr.grid["gphit"].filled()  # lat
    except Exception:
        logger.debug("Not a masked array.")

    # Define z at t/u/v points

    DstCoord.depths = {"t": {}, "u": {}, "v": {}}

    if (SourceCoord.zgr.grid_type != "zco") & (settings["zinterp"] is False):
        # Override use zinterp flag if vertical grid type is not zco
        logger.warning("Setting zinterp to True because vertical grid is not zco")
        settings["zinterp"] = True

    if settings["zinterp"] is True:
        # Condition to interp data on destiantion grid levels
        for grd in ["t", "u", "v"]:
            tmp_tz, tmp_wz, tmp_e3 = zgrv.get_bdy_depths(
                DstCoord, bdy_ind[grd].bdy_i, grd
            )
            DstCoord.depths[grd]["bdy_H"] = np.ma.max(tmp_wz, axis=0)
            DstCoord.depths[grd]["bdy_dz"] = tmp_e3
            DstCoord.depths[grd]["bdy_z"] = tmp_tz
        logger.info("Depths defined on destination grid levels")
    else:
        # Condition to keep data on parent grid levels
        for grd in ["t", "u", "v"]:
            # These are just set to the nearest neighbour in source grid
            tmp_tz, tmp_wz, tmp_e3 = zgrv.get_bdy_sc_depths(SourceCoord, DstCoord, grd)
            DstCoord.depths[grd]["bdy_H"] = np.ma.max(tmp_wz, axis=0)
            DstCoord.depths[grd]["bdy_dz"] = tmp_e3
            DstCoord.depths[grd]["bdy_z"] = tmp_tz
        logger.info("Depths defined with destination equal to source levels")

    # Set up time information

    t_adj = settings["src_time_adj"]  # any time adjutments?
    reader = factory.GetReader(settings["src_dir"], t_adj)
    for grd in ["t", "u", "v"]:
        bdy_ind[grd].source_time = reader[grd]

    unit_origin = settings["date_origin"] + " 00:00:00"

    # Extract source data on dst grid

    if settings["tide"]:
        if (
            (settings["tide_model"].lower() == "tpxo7p2")
            or (settings["tide_model"].lower() == "tpxo9v5")
            or (settings["tide_model"].lower() == "fes2014")
        ):
            cons = tide.nemo_bdy_tide_rot(
                Setup,
                DstCoord,
                bdy_ind["t"],
                bdy_ind["u"],
                bdy_ind["v"],
                settings["clname"],
            )
        else:
            logger.error("Tidal model: %s, not recognised", settings["tide_model"])
            return

        write_tidal_data(Setup, DstCoord, bdy_ind, settings["clname"], cons)

    logger.info("Tidal constituents written to file")

    # Set the year and month range

    st_d = dt.datetime.strptime(settings["date_start"], "%Y-%m-%d")
    en_d = dt.datetime.strptime(settings["date_end"], "%Y-%m-%d")

    if st_d.year > en_d.year:
        logging.error(
            "Please check the nn_year_000 and nn_year_end " + "values in input bdy file"
        )
        return

    yrs = list(range(st_d.year, en_d.year + 1))

    if en_d.year - st_d.year >= 1:
        if en_d.month - st_d.month < 12:
            logger.info(
                "Warning: All months will be extracted as the number "
                + "of years is greater than 1"
            )
        mns = list(range(1, 13))
    else:
        if en_d.month > 12 or st_d.month < 1:
            logging.error(
                "Please check the nn_date_start and nn_date_end "
                + "month values in input bdy file"
            )
            return
        if en_d.day == 1:
            mns = list(range(st_d.month, en_d.month))
        else:
            mns = list(range(st_d.month, en_d.month + 1))

    # Enter the loop for each year and month extraction

    logger.info("Entering extraction loop")

    ln_dyn2d = settings["dyn2d"]
    ln_dyn3d = settings["dyn3d"]  # are total or bc velocities required
    ln_tra = settings["tra"]
    ln_ice = settings["ice"]

    # Define mapping of variables to grids with a dictionary

    emap = {}
    grd = ["t", "u", "v"]
    pair = [None, "uv", "uv"]  # TODO: devolve this to the namelist?

    # TODO: The following is a temporary stop gap to assign variables. In
    # future we need a slicker way of determining the variables to extract.
    # Perhaps by scraping the .ncml file - this way biogeochemical tracers
    # can be included in the ln_tra = .true. option without having to
    # explicitly declaring them.

    var_in = {}
    for g in range(len(grd)):
        var_in[grd[g]] = []

    if ln_tra:
        var_in["t"].extend(["votemper", "vosaline"])

    if ln_dyn2d or ln_dyn3d:
        var_in["u"].extend(["vozocrtx", "vomecrty"])
        var_in["v"].extend(["vozocrtx", "vomecrty"])

    if ln_dyn2d:
        var_in["t"].extend(["sossheig"])

    if ln_ice:
        var_in["t"].extend(["ice1", "ice2", "ice3"])

    # As variables are associated with grd there must be a filename attached
    # to each variable

    for g in range(len(grd)):
        if len(var_in[grd[g]]) > 0:
            emap[grd[g]] = {"variables": var_in[grd[g]], "pair": pair[g]}

    extract_obj = {}

    # Initialise the mapping indices for each grid

    for key, val in list(emap.items()):
        extract_obj[key] = extract.Extract(
            Setup.settings,
            SourceCoord,
            DstCoord,
            bdy_ind,
            val["variables"],
            key,
            val["pair"],
        )

    # TODO: Write the nearest neighbour parent grid point to each bdy point
    #       possibly to the coordinates.bdy.nc file to help with comparison
    #       plots later.

    for year in yrs:
        for month in mns:
            if (dt.datetime(year, month, 1) < dt.datetime(st_d.year, st_d.month, 1)) | (
                dt.datetime(year, month, 1) > dt.datetime(en_d.year, en_d.month, 1)
            ):
                continue
            for key, val in list(emap.items()):
                # Extract the data for a given month and year
                extract_obj[key].extract_month(year, month)

                # Interpolate/stretch in time if time frequecy is not a factor
                # of a month and/or parent:child calendars differ
                if settings.get("time_interpolation", True):
                    logger.info("Applying temporal interpolation from parent to child.")
                    extract_obj[key].time_interp(year, month)
                else:
                    logger.info("Temporal interpolation not applied.")

                # Finally write to file
                extract_obj[key].write_out(year, month, bdy_ind[key], unit_origin)

    logger.info("End NRCT Logging: " + time.asctime())
    logger.info("==========================================")


def write_tidal_data(setup_var, dst_coord_var, grid, tide_cons, cons):
    """
    Write the tidal data to a NetCDF file.

    Parameters
    ----------
        setup_var     (list): Description of arg1
        dst_coord_var (obj) : Description of arg1
        grid          (dict): Description of arg1
        tide_cons     (list): Description of arg1
        cons          (data): cosz, sinz, cosu, sinu, cosv, sinv

    Returns
    -------
        None    : tidal data is written to NetCDF file
    """
    # Mapping of variable names to grid types

    tmap = {}
    grd = ["t", "u", "v"]
    var = ["z", "u", "v"]
    des = [
        "tidal elevation components for:",
        "tidal east velocity components for:",
        "tidal north velocity components for:",
    ]

    for g in range(len(grd)):
        bdy_r = grid[grd[g]].bdy_r
        tmap[grd[g]] = {
            "nam": var[g],
            "des": des[g],
            "ind": np.where(bdy_r == 0),
            "nx": len(grid[grd[g]].bdy_i[bdy_r == 0, 0]),
        }

    # Write constituents to file

    for tide_con in tide_cons:  # iterates over the constituent numbers {1,..} as str
        const_name = setup_var.settings["clname"][tide_con]
        const_name = const_name.replace("'", "").upper()

        for key, val in list(tmap.items()):
            fout_tide = (
                setup_var.settings["dst_dir"]
                + setup_var.settings["fn"]
                + "_bdytide_"
                + setup_var.settings["tide_model"]
                + "_"
                + const_name
                + "_grd_"
                + val["nam"].upper()
                + ".nc"
            )

            nemo_bdy_tide_ncgen.CreateBDYTideNetcdfFile(
                fout_tide,
                val["nx"],
                dst_coord_var.lonlat[key]["lon"].shape[1],
                # "key" is the grd value
                dst_coord_var.lonlat[key]["lon"].shape[0],
                val["des"] + tide_con,
                setup_var.settings["fv"],
                key.upper(),
            )

            # Set the index for the con(stituent) to save
            if val["nam"] == "z":
                indx = 0
                # bdy_msk is only defined on the t-grid (not u/v-points)
                ncpop.write_data_to_file(fout_tide, "bdy_msk", dst_coord_var.bdy_msk)
            elif val["nam"] == "u":
                indx = 2
            elif val["nam"] == "v":
                indx = 4
            else:
                logging.error("profiler: Ooo, that should not have happened")

            ncpop.write_data_to_file(
                fout_tide, val["nam"] + "1", cons[indx][int(tide_con) - 1]
            )  # "cos[var][constituent index]"
            ncpop.write_data_to_file(
                fout_tide, val["nam"] + "2", cons[indx + 1][int(tide_con) - 1]
            )  # "sin[var][constituent index]"
            ncpop.write_data_to_file(
                fout_tide, "nav_lon", dst_coord_var.lonlat[key]["lon"]
            )  # "key" is the grd value
            ncpop.write_data_to_file(
                fout_tide, "nav_lat", dst_coord_var.lonlat[key]["lat"]
            )  # "key" is the grd value
            ncpop.write_data_to_file(
                fout_tide, "nbidta", grid[key].bdy_i[val["ind"], 0] + 1
            )
            ncpop.write_data_to_file(
                fout_tide, "nbjdta", grid[key].bdy_i[val["ind"], 1] + 1
            )
            ncpop.write_data_to_file(
                fout_tide, "nbrdta", grid[key].bdy_r[val["ind"]] + 1
            )


def _get_mask(Setup, mask_gui):
    """
    Read mask information from file or open GUI.

    This method reads the mask information from the netcdf file or opens a gui
    to create a mask depending on the mask_gui input. The default mask data
    uses the bathymetry and applies a 1pt halo.

    Args:
    ----
        Setup    (list): settings for bdy
        mask_gui (bool): whether use of the GUI is required

    Returns:
    -------
        bdy_msk (numpy.array) : a mask array of the regional domain
    """
    # Initialise bdy_msk array

    bdy_msk = None

    if mask_gui:  # Do we activate the GUI
        # TODO: I do not like the use of _ for a dummy variable - better way?

        _, mask = pybdy_settings_editor.open_settings_dialog(Setup)
        bdy_msk = mask.data
        Setup.refresh()
        logger.info("Using GUI defined mask")
    else:  # Try an read mask from file
        try:
            if (
                Setup.bool_settings["mask_file"]
                and Setup.settings["mask_file"] is not None
            ):
                mask = Mask_File(Setup.settings["bathy"], Setup.settings["mask_file"])
                bdy_msk = mask.data
                logger.info("Using input mask file")
            elif Setup.bool_settings["mask_file"]:
                logger.error("Mask file is not given")
                return
            else:  # No mask file specified then use default 1px halo mask
                logger.warning("Using default mask with bathymetry!!!!")
                mask = Mask_File(Setup.settings["bathy"])
                mask.apply_border_mask(Constants.DEFAULT_MASK_PIXELS)
                bdy_msk = mask.data
        except Exception:
            return

    if np.amin(bdy_msk) == 0:  # Mask is not set, so set border to 1px
        logger.warning("Setting the mask to with a 1 grid point border")
        if mask_gui:
            QMessageBox.warning(
                None, "NRCT", "Mask is not set, setting a 1 grid " + "point border mask"
            )

        if bdy_msk is not None and 1 < bdy_msk.shape[0] and 1 < bdy_msk.shape[1]:
            tmp = np.ones(bdy_msk.shape, dtype=bool)
            tmp[1:-1, 1:-1] = False
            bdy_msk[tmp] = -1

    return bdy_msk
