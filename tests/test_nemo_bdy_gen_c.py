import os
from typing import Tuple

import numpy as np
import pytest
from pybdy import nemo_bdy_gen_c as gen_grid_orig
from pybdy import nemo_bdy_gen_c_refactor as gen_grid_refactor
from pybdy import nemo_bdy_setup as setup
from pybdy.profiler import _get_mask


# Mock boundary class
class MockBoundary(gen_grid_refactor.Boundary):
    """Mock Boundary class that inherits all methods from the Boundary class."""

    def __init__(
        self,
        bdy_msk: np.ndarray = np.array(
            [
                [0, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 0],
            ]
        ),
        rw: int = 2,
        grid: str = "t",
    ) -> None:
        self.bdy_msk = bdy_msk

        # Rim variables
        self.rw = rw
        self.rm = self.rw - 1

        # Grid
        self.grid = grid


@pytest.fixture(scope="function")
def get_mock_boundary() -> MockBoundary:
    """Get a MockBoundary instance."""
    mock_bdy = MockBoundary()
    return mock_bdy


@pytest.fixture(scope="function")
def get_mask_settings() -> Tuple[np.ndarray, dict]:
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
def get_boundary_instance(
    get_mask_settings: Tuple[np.ndarray, dict]
) -> gen_grid_refactor.Boundary:
    """Get an instance of the Boundary refactored class."""
    bdy_msk, settings = get_mask_settings
    bdy = gen_grid_refactor.Boundary(bdy_msk, settings, "t")

    return bdy


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                                   Unit tests                                      #
#                                                                                   #
# --------------------------------------------------------------------------------- #
def test_create_i_j_indexes(
    get_boundary_instance: gen_grid_refactor.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __create_i_j_indexes method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Generate the reference arrays
    igrid_ref = np.array(
        [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        ]
    )

    jgrid_ref = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
            [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
            [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
            [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        ]
    )

    # Create the i j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid_ref, igrid
    ), "Reference igrid in not equal to the igrid calculated in the Boundary class"
    assert np.array_equal(
        jgrid_ref, jgrid
    ), "Reference jgrid in not equal to the grid calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Generate the reference arrays
    igrid_ref = np.array(
        [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]
    )

    jgrid_ref = np.array(
        [[0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]]
    )

    # Create the i j indexes
    igrid, jgrid = bdy_mock._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid_ref, igrid
    ), "Reference igrid in not equal to the igrid calculated in the Boundary class"

    assert np.array_equal(
        jgrid_ref, jgrid
    ), "Reference jgrid in not equal to the grid calculated in the Boundary class"


def test_unique_rows(get_boundary_instance: gen_grid_refactor.Boundary) -> None:
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


def test_find_bdy(
    get_boundary_instance: gen_grid_refactor.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __find_bdy method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Create the i and j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    # Mask index range for south
    brg_south = [1, -1, 1, -1, None, -2, 1, -1]

    # Expected indexes
    bdy_I_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    bdy_J_ref = np.array([1, 1, 1, 1, 1, 1, 1, 1])

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy._Boundary__find_bdy(igrid, jgrid, bdy.bdy_msk, brg_south)

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the Boundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Create the i and j indexes
    igrid, jgrid = bdy_mock._Boundary__create_i_j_indexes()

    # Expected indexes
    bdy_I_ref = np.array([1, 2, 3])
    bdy_J_ref = np.array([0, 0, 0])

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy_mock._Boundary__find_bdy(
        igrid, jgrid, bdy_mock.bdy_msk, brg_south
    )

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the MockBoundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the MockBoundary class"


def test_create_boundary_indexes(
    get_boundary_instance: gen_grid_refactor.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __create_boundary_indexes method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Create the i and j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    # Create the boundary indexes references
    SBi_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    SBj_ref = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])
    NBi_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    NBj_ref = np.array([9, 9, 9, 9, 9, 9, 9, 9, 9])
    EBi_ref = np.array([9, 9, 9, 9, 9, 9, 9, 9, 9])
    EBj_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    WBi_ref = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])
    WBj_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Create the boundary indexes
    SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj = bdy._Boundary__create_boundary_indexes(
        igrid, jgrid
    )

    # Check the results
    assert np.array_equal(
        SBi_ref, SBi
    ), "Reference SBi is not equal to the SBi calculated in the Boundary class"
    assert np.array_equal(
        SBj_ref, SBj
    ), "Reference SBj is not equal to the SBj calculated in the Boundary class"
    assert np.array_equal(
        NBi_ref, NBi
    ), "Reference NBi is not equal to the NBi calculated in the Boundary class"
    assert np.array_equal(
        NBj_ref, NBj
    ), "Reference NBj is not equal to the NBj calculated in the Boundary class"
    assert np.array_equal(
        EBi_ref, EBi
    ), "Reference EBi is not equal to the EBi calculated in the Boundary class"
    assert np.array_equal(
        EBj_ref, EBj
    ), "Reference EBj is not equal to the EBj calculated in the Boundary class"
    assert np.array_equal(
        WBi_ref, WBi
    ), "Reference WBi is not equal to the WBi calculated in the Boundary class"
    assert np.array_equal(
        WBj_ref, WBj
    ), "Reference WBj is not equal to the WBj calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Create the boundary indexes references
    SBi_ref = np.array([1, 2, 3])
    SBj_ref = np.array([0, 0, 0])
    NBi_ref = np.array([1, 2, 4])
    NBj_ref = np.array([3, 3, 3])
    EBi_ref = np.array([])
    EBj_ref = np.array([])
    WBi_ref = np.array([])
    WBj_ref = np.array([])

    # Create the i and j indexes
    igrid, jgrid = bdy_mock._Boundary__create_i_j_indexes()

    # Create the boundary indexes
    (
        SBi,
        SBj,
        NBi,
        NBj,
        EBi,
        EBj,
        WBi,
        WBj,
    ) = bdy_mock._Boundary__create_boundary_indexes(igrid, jgrid)

    # Check the results
    assert np.array_equal(
        SBi_ref, SBi
    ), "Reference SBi is not equal to the SBi calculated in the MockBoundary class."

    assert np.array_equal(
        SBj_ref, SBj
    ), "Reference SBj is not equal to the SBj calculated in the MockBoundary class."

    assert np.array_equal(
        NBi_ref, NBi
    ), "Reference NBi is not equal to the NBi calculated in the MockBoundary class."

    assert np.array_equal(
        NBj_ref, NBj
    ), "Reference NBj is not equal to the NBj calculated in the MockBoundary class."

    assert np.array_equal(
        EBi_ref, EBi
    ), "Reference EBi is not equal to the EBi calculated in the MockBoundary class."

    assert np.array_equal(
        EBj_ref, EBj
    ), "Reference EBj is not equal to the EBj calculated in the MockBoundary class."

    assert np.array_equal(
        WBi_ref, WBi
    ), "Reference WBi is not equal to the WBi calculated in the MockBoundary class."

    assert np.array_equal(
        WBj_ref, WBj
    ), "Reference WBj is not equal to the WBj calculated in the MockBoundary class."


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                                Functional tests                                   #
#                                                                                   #
# --------------------------------------------------------------------------------- #
def test_grid_refactor(get_mask_settings: Tuple[np.ndarray, dict]) -> None:
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
