"""
Subset of pynemo for Robinson.

It should be able to read a mask file and produce a coordinates.bdy.nc file.

author: jdha@noc.ac.uk
"""
# External imports
import importlib
import logging
from time import clock

import numpy as np
from pynemo import nemo_bdy_dst_coord as dst_coord
from pynemo import nemo_bdy_gen_c as gen_grid
from pynemo import nemo_bdy_ice, pynemo_settings_editor

# local imports
from pynemo import nemo_bdy_setup as setup
from pynemo import nemo_bdy_source_coord as source_coord
from pynemo import nemo_coord_gen_pop as coord
from pynemo.gui.nemo_bdy_mask import Mask as Mask_File
from pynemo.utils import Constants
from PyQt5.QtWidgets import QMessageBox

# import pickle


logger = logging.getLogger(__name__)


def process_bdy(setup_filepath=0, mask_gui=False):
    """
    Run main entry to the processing of the bdy.

    Parameters
    ----------
    setup_filepath -- file path to bdy file
    mask_gui -- whether gui to select the mask file needs to be poped up.
    """
    # Logger
    logger.info("START")
    start = clock()
    source_coord.SourceCoord()
    DstCoord = dst_coord.DstCoord()

    logger.info(clock() - start)
    start = clock()
    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings

    logger.info(clock() - start)
    ice = settings["ice"]
    logger.info("ice = %s", ice)

    logger.info("Done Setup")
    # default file, region settingas

    start = clock()
    bdy_msk = _get_mask(Setup, mask_gui)
    logger.info(clock() - start)
    logger.info("Done Mask")

    DstCoord.bdy_msk = bdy_msk == 1
    importlib.reload(gen_grid)
    start = clock()
    logger.info("start bdy_t")
    grid_t = gen_grid.Boundary(bdy_msk, settings, "t")

    logger.info(clock() - start)
    start = clock()
    logger.info("start bdy_u")
    grid_u = gen_grid.Boundary(bdy_msk, settings, "u")
    logger.info("start bdy_v")

    logger.info(clock() - start)
    start = clock()
    grid_v = gen_grid.Boundary(bdy_msk, settings, "v")
    logger.info("start bdy_f")

    logger.info(clock() - start)
    start = clock()

    grid_f = gen_grid.Boundary(bdy_msk, settings, "f")
    logger.info("done  bdy t,u,v,f")

    logger.info(clock() - start)
    start = clock()
    if ice:
        grid_ice = nemo_bdy_ice.BoundaryIce()
        grid_ice.grid_type = "t"
        grid_ice.bdy_r = grid_t.bdy_r

    bdy_ind = {"t": grid_t, "u": grid_u, "v": grid_v, "f": grid_f}

    for k in list(bdy_ind.keys()):
        logger.info(
            "bdy_ind %s %s %s", k, bdy_ind[k].bdy_i.shape, bdy_ind[k].bdy_r.shape
        )

    start = clock()
    co_set = coord.Coord(settings["dst_dir"] + "/coordinates.bdy.nc", bdy_ind)
    logger.info("done coord gen")
    logger.info(clock() - start)
    start = clock()
    logger.info(settings["dst_hgr"])
    co_set.populate(settings["dst_hgr"])
    logger.info("done coord pop")

    logger.info(clock() - start)

    # may need to rethink grid info
    # tracer 3d frs over rw
    # tracer 2d frs over rw (i.e. ice)
    # dyn 2d over 1st rim of T grid (i.e. ssh)
    # dyn 2d over 1st rim
    # dyn 2d frs over rw
    # dyn 3d over 1st rim
    # dyn 3d frs over rw


def _get_mask(Setup, mask_gui):
    """
    Read the mask info from the netcdf file or open a gui to create a mask depending on the mask_gui input.

    Notes
    -----
    The default mask data is using bathymetry and applying a 1px halo

    Parameters
    ----------
    Setup -- settings for bdy
    mask_gui -- boolean to open mask gui.

    Returns
    -------
    bdy_msk
        Mask data.
    """
    bdy_msk = None
    if mask_gui:
        # Open the gui to create a mask
        _, mask = pynemo_settings_editor.open_settings_dialog(Setup)
        bdy_msk = mask.data
        Setup.refresh()
    else:
        try:
            # mask filename and mask file flag is set
            if (
                Setup.bool_settings["mask_file"]
                and Setup.settings["mask_file"] is not None
            ):
                mask = Mask_File(mask_file=Setup.settings["mask_file"])
                bdy_msk = mask.data
            elif Setup.bool_settings["mask_file"]:
                logger.error("Mask file is not given")
                return
            else:  # no mask file specified then use default 1px halo mask
                logger.warning("Using default mask with bathymetry!!!!")
                mask = Mask_File(Setup.settings["bathy"])
                mask.apply_border_mask(Constants.DEFAULT_MASK_PIXELS)
                bdy_msk = mask.data
        except (
            ValueError
        ):  # why is this except here? as there is an else: statement TODO
            print("something wrong?")
            return
    if np.amin(bdy_msk) == 0:
        # Mask is not set throw a warning message and set border to 1px.
        logger.warning("Setting the mask to 1px border")
        QMessageBox.warning(
            None, "pyNEMO", "Mask is not set, setting a 1 pixel border mask"
        )
        if bdy_msk is not None and 1 < bdy_msk.shape[0] and 1 < bdy_msk.shape[1]:
            tmp = np.ones(bdy_msk.shape, dtype=bool)
            tmp[1:-1, 1:-1] = False
            bdy_msk[tmp] = -1

    return bdy_msk
