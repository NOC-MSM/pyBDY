import os

import numpy as np
import pytest
from pybdy import nemo_bdy_gen_c as gen_grid_orig
from pybdy import nemo_bdy_gen_c_refactor as gen_grid_refactor
from pybdy import nemo_bdy_setup as setup
from pybdy.profiler import _get_mask


@pytest.fixture(scope="function")
def get_mask_settings():
    """Get mask and settings."""
    # File path for the setup
    setup_filepath = os.path.join("tests", "namelists", "namelist_test_001.bdy")

    # Setup settings
    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings

    # Get mask information
    bdy_msk = _get_mask(Setup, False)

    return bdy_msk, settings


@pytest.fixture(scope="function")
def get_boundary_instance(get_mask_settings):
    """Get an instance of the Boundary refactored class."""
    bdy_msk, settings = get_mask_settings
    bdy = gen_grid_refactor.Boundary(bdy_msk, settings, "t")

    return bdy


# Functional tests
def test_grid_refactor(get_mask_settings):
    """Test the final results of the refactored Boundary class."""
    bdy_msk, settings = get_mask_settings

    for grd in ["t", "u", "v"]:
        # Refactored class
        bdy_refactor = gen_grid_refactor.Boundary(bdy_msk, settings, grd)
        bdy_refactor.create_boundary()

        # Original class
        bdy_orig = gen_grid_orig.Boundary(bdy_msk, settings, grd)

        assert np.array_equal(
            bdy_refactor.bdy_i, bdy_orig.bdy_i
        ), "bdy_i in refactored Boundary class is not equal to bdy_i in original Boundary class"
        assert np.array_equal(
            bdy_refactor.bdy_r, bdy_orig.bdy_r
        ), "bdy_r in refactored Boundary class is not equal to bdy_r in original Boundary class"


# Unit tests
def test_create_i_j_indexes(get_boundary_instance):
    """Test the __create_i_j_indexes method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Generate the reference arrays
    igrid_ref = np.tile(np.arange(bdy.bdy_msk.shape[1]), (bdy.bdy_msk.shape[0], 1))
    jgrid_ref = np.tile(np.arange(bdy.bdy_msk.shape[0]), (bdy.bdy_msk.shape[1], 1)).T

    # Create the i j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid_ref, igrid
    ), "Reference igrid in not equal to the igrid calculated in the Boundary class"
    assert np.array_equal(
        jgrid_ref, jgrid
    ), "Reference jgrid in not equal to the grid calculated in the Boundary class"


def test_unique_rows(get_boundary_instance):
    """Test the __unique_rows method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Generate test 2d array with unique rows with indexes 0, 1 and 4
    test_array = np.ones((5, 5))
    test_array[0, 0] = 0
    test_array[4, 1] = 0

    unique_rows = bdy._Boundary__unique_rows(test_array)
    assert np.array_equal(
        unique_rows, [0, 4, 1]
    ), "Unique rows is not equal to [0, 4, 1]"

    # Generate test 2d array with all rows equal
    test_array = np.ones((5, 5))
    unique_rows = bdy._Boundary__unique_rows(test_array)
    assert np.array_equal(unique_rows, [0]), "Unique rows is not equal to [0]"
