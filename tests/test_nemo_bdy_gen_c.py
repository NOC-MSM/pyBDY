import pytest
from pybdy import nemo_bdy_setup as setup
from pybdy.profiler import _get_mask


@pytest.fixture(scope="function")
def handle_temp_dir():
    setup_filepath = ""

    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings

    bdy_msk = _get_mask(Setup, False)

    return bdy_msk, settings


# Tests for different grid types
def test_t_grid():
    # for grd in ["t", "u", "v"]:
    # bdy_ind[grd] = gen_grid.Boundary(bdy_msk, settings, grd)
    # logger.info("Generated BDY %s information", grd)
    # logger.info("Grid %s has shape %s", grd, bdy_ind[grd].bdy_i.shape).

    pass


def test_u_grid():
    pass


def test_v_grid():
    pass
