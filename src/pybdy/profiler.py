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
Created on Wed Sep 12 08:02:46 2012.

The main application script for the NRCT.

@author James Harle
@author John Kazimierz Farey
@author Srikanth Nagella
$Last commit on:$
"""

# External imports
import logging
import time

import numpy as np
from PyQt5.QtWidgets import QMessageBox

from pybdy import nemo_bdy_dst_coord as dst_coord
from pybdy import nemo_bdy_extr_tm3 as extract
from pybdy import nemo_bdy_gen_c as gen_grid
from pybdy import nemo_bdy_ncpop as ncpop
from pybdy import nemo_bdy_setup as setup
from pybdy import nemo_bdy_source_coord as source_coord
from pybdy import nemo_bdy_zgrv2 as zgrv
from pybdy import nemo_coord_gen_pop as coord

# Local imports
from pybdy import pybdy_settings_editor
from pybdy.gui.nemo_bdy_mask import Mask as Mask_File
from pybdy.reader import factory
from pybdy.reader.factory import GetFile
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

    """
    # Start Logger

    logger.info("Start NRCT Logging: " + time.asctime())
    logger.info("============================================")

    SourceCoord = source_coord.SourceCoord()
    DstCoord = dst_coord.DstCoord()

    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings

    logger.info("Reading grid completed")

    bdy_msk = _get_mask(Setup, mask_gui)
    DstCoord.bdy_msk = bdy_msk == 1

    logger.info("Reading mask completed")
    
    bdy_ind = {}  # define a dictionary to hold the grid information

    for grd in ["t", "u", "v"]:
        bdy_ind[grd] = gen_grid.Boundary(bdy_msk, settings, grd)
        logger.info("Generated BDY %s information", grd)
        logger.info("Grid %s has shape %s", grd, bdy_ind[grd].bdy_i.shape)

        # TODO: Write in option to seperate out disconnected LBCs
        # Add a function to split the bdy into several boundary chunks
        bdy_msk_chunks = _chunk_bdy(bdy_ind[grd])
    
    # Write out grid information to coordinates.bdy.nc

    co_set = coord.Coord(settings["dst_dir"] + "/coordinates.bdy.nc", bdy_ind)
    co_set.populate(settings["dst_hgr"])
    logger.info("File: coordinates.bdy.nc generated and populated")

    # Idenitify number of boundary points

    nbdy = {}

    for grd in ["t", "u", "v"]:
        nbdy[grd] = len(bdy_ind[grd].bdy_i[:, 0])

    # Gather grid information

    # TODO: insert some logic here to account for 2D or 3D src_zgr

    logger.info("Gathering grid information")
    nc = GetFile(settings["src_zgr"])
    SourceCoord.zt = np.squeeze(nc["gdept_0"][:])
    nc.close()

    # Define z at t/u/v points

    z = zgrv.Depth(bdy_ind["t"].bdy_i, bdy_ind["u"].bdy_i, bdy_ind["v"].bdy_i, settings)

    # TODO: put conditional here as we may want to keep data on parent
    #       vertical grid

    DstCoord.depths = {"t": {}, "u": {}, "v": {}}

    for grd in ["t", "u", "v"]:
        DstCoord.depths[grd]["bdy_H"] = np.nanmax(z.zpoints["w" + grd], axis=0)
        DstCoord.depths[grd]["bdy_dz"] = np.diff(z.zpoints["w" + grd], axis=0)
        DstCoord.depths[grd]["bdy_dz"] = np.vstack(
            [DstCoord.depths[grd]["bdy_dz"], np.zeros((1, nbdy[grd]))]
        )
        DstCoord.depths[grd]["bdy_z"] = z.zpoints[grd]
    logger.info("Depths defined")

    # Gather horizontal grid information

    nc = GetFile(settings["src_hgr"])
    SourceCoord.lon = nc["glamt"][:, :]
    SourceCoord.lat = nc["gphit"][:, :]

    try:  # if they are masked array convert them to normal arrays
        SourceCoord.lon = SourceCoord.lon.filled()
    except Exception:
        logger.debug("Not a masked array.")
    try:
        SourceCoord.lat = SourceCoord.lat.filled()
    except Exception:
        logger.debug("Not a masked array.")

    nc.close()

    DstCoord.lonlat = {"t": {}, "u": {}, "v": {}}

    nc = GetFile(settings["dst_hgr"])

    # Read and assign horizontal grid data

    for grd in ["t", "u", "v"]:
        DstCoord.lonlat[grd]["lon"] = nc["glam" + grd][0, :, :]
        DstCoord.lonlat[grd]["lat"] = nc["gphi" + grd][0, :, :]

    nc.close()

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

    # Set up time information

    t_adj = settings["src_time_adj"]  # any time adjutments?
    reader = factory.GetReader(settings["src_dir"], t_adj)
    for grd in ["t", "u", "v"]:
        bdy_ind[grd].source_time = reader[grd]

    unit_origin = "%d-01-01 00:00:00" % settings["base_year"]

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

    yr_000 = settings["year_000"]
    yr_end = settings["year_end"]
    mn_000 = settings["month_000"]
    mn_end = settings["month_end"]

    if yr_000 > yr_end:
        logging.error(
            "Please check the nn_year_000 and nn_year_end " + "values in input bdy file"
        )
        return

    yrs = list(range(yr_000, yr_end + 1))

    if yr_end - yr_000 >= 1:
        if mn_end - mn_000 < 12:
            logger.info(
                "Warning: All months will be extracted as the number "
                + "of years is greater than 1"
            )
        mns = list(range(1, 13))
    else:
        mn_000 = settings["month_000"]
        mn_end = settings["month_end"]
        if mn_end > 12 or mn_000 < 1:
            logging.error(
                "Please check the nn_month_000 and nn_month_end "
                + "values in input bdy file"
            )
            return
        mns = list(range(mn_000, mn_end + 1))

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
        numpy.array     : a mask array of the regional domain
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
        QMessageBox.warning(
            None, "NRCT", "Mask is not set, setting a 1 grid " + "point border mask"
        )
        if bdy_msk is not None and 1 < bdy_msk.shape[0] and 1 < bdy_msk.shape[1]:
            tmp = np.ones(bdy_msk.shape, dtype=bool)
            tmp[1:-1, 1:-1] = False
            bdy_msk[tmp] = -1

    return bdy_msk

def _chunk_bdy(bdy):
    """
    Takes the boundary indicies and turns them into a list of boundary chunks.
    The boundary is first split at natural breaks like land or the east-west wrap.
    The chunks are then split near corners.
    The chunks are then optionally split in the middle if they're above a certain size.
    
        Args:
    ----
        Boundary object     : object with indices of the boundary organised as 
                              bdy.bdy_i[bdy point, i/j grid]
                              and rim width number
                              bdy.bdy_r[bdy_point]

    Returns:
    -------
        List of Boundary objects     : list of objects with indices of the boundary
    """
    import matplotlib.pyplot as plt
    
    rw = bdy.settings["rimwidth"]
    mid_split = False #bdy.settings["midsplit"] # True/False
    bdy_size = np.shape(bdy.bdy_i)
    chunk_bdy = []
    
    # Find natural breaks in the boundary looking for gaps in i and j 
    
    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    chk = 0
    
    for i in range(bdy_size[0]):
        # Subtract i and j index of point from the rest and test abs value
        i_abs = np.abs(ibdy - ibdy[i])
        j_abs = np.abs(jbdy - jbdy[i])
        closeness_test = (i_abs <= 1) & (j_abs <= 1)
        
        # Check if any of these points already has a chunk number
        chk_true = (chunk_number[closeness_test] != -1)
        if any(chk_true):
            lowest_chk = np.min(chunk_number[closeness_test][chk_true])
            other_chk = np.unique(chunk_number[closeness_test][chk_true])
            chunk_number[closeness_test] = lowest_chk
            for c in range(len(other_chk)):
                chunk_number[chunk_number == other_chk[c]] = lowest_chk
        else:
            lowest_chk = chk * 1
            chk = chk + 1
            chunk_number[closeness_test] = lowest_chk
        
    # Rectify the chunk numbers
    all_chunk = np.unique(chunk_number)
    max_chunk = np.max(chunk_number)
    chunk_number_s = np.zeros_like(bdy.bdy_r) -1
    c = 0
    for i in range(len(all_chunk)):
        chunk_number_s[chunk_number == all_chunk[i]] = c
        c = c + 1        
    chunk_number = chunk_number_s * 1

    plt.scatter(ibdy, jbdy, c=chunk_number)
    plt.show()
    
    
    # Find corners and split beyond the rim width
    
    
    
    # Find midpoint of chunks
    if mid_split:
        None
    
    return chunk_bdy
