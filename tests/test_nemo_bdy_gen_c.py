import os
from typing import Tuple

import numpy as np
import pytest
from pybdy import nemo_bdy_gen_c as gen_grid
from pybdy import nemo_bdy_gen_c_old as gen_grid_old
from pybdy import nemo_bdy_setup as setup
from pybdy.profiler import _get_mask


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                             Mock classes and fixtures                             #
#                                                                                   #
# --------------------------------------------------------------------------------- #
class MockBoundary(gen_grid.Boundary):
    """Mock Boundary class that inherits all methods from the Boundary class."""

    def __init__(
        self,
        bdy_msk: np.ndarray = np.array(
            [
                [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, 1, 1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, 1, 1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            ]
        ),
        rw: int = 2,
        grid: str = "t",
    ) -> None:
        # Boundary mask
        self.bdy_msk = bdy_msk

        # Rim variables
        self.rw = rw
        self.rm = self.rw - 1

        # Grid
        self.grid = grid
        self.grid_type = grid.lower()


@pytest.fixture(scope="function")
def get_mock_boundary() -> MockBoundary:
    """Get a MockBoundary instance and intermediate data."""
    mock_bdy = MockBoundary()

    # Define intermediate variables calculated in the MockBoundary class for the "t" grid
    igrid = np.array(
        [
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
        ]
    )

    jgrid = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4, 4, 4, 4, 4],
            [5, 5, 5, 5, 5, 5, 5, 5, 5],
            [6, 6, 6, 6, 6, 6, 6, 6, 6],
            [7, 7, 7, 7, 7, 7, 7, 7, 7],
            [8, 8, 8, 8, 8, 8, 8, 8, 8],
        ]
    )

    SBi = np.array([2, 3, 4, 5, 6])
    SBj = np.array([2, 2, 2, 2, 2])
    NBi = np.array([2, 3, 4, 5, 6])
    NBj = np.array([6, 6, 6, 6, 6])
    EBi = np.array([6, 6, 6, 6, 6])
    EBj = np.array([2, 3, 4, 5, 6])
    WBi = np.array([2, 2, 2, 2, 2])
    WBj = np.array([2, 3, 4, 5, 6])

    data = {
        "igrid": igrid,
        "jgrid": jgrid,
        "SBi": SBi,
        "SBj": SBj,
        "NBi": NBi,
        "NBj": NBj,
        "EBi": EBi,
        "EBj": EBj,
        "WBi": WBi,
        "WBj": WBj,
    }

    return mock_bdy, data


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
) -> gen_grid.Boundary:
    """Get an instance of the Boundary refactored class and intermediate data."""
    bdy_msk, settings = get_mask_settings
    bdy = gen_grid.Boundary(bdy_msk, settings, "t")

    # Define intermediate variables calculated in the Boundary class for the "t" grid
    igrid = np.array(
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

    jgrid = np.array(
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

    SBi = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    SBj = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])
    NBi = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    NBj = np.array([9, 9, 9, 9, 9, 9, 9, 9, 9])
    EBi = np.array([9, 9, 9, 9, 9, 9, 9, 9, 9])
    EBj = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    WBi = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])
    WBj = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])

    data = {
        "igrid": igrid,
        "jgrid": jgrid,
        "SBi": SBi,
        "SBj": SBj,
        "NBi": NBi,
        "NBj": NBj,
        "EBi": EBi,
        "EBj": EBj,
        "WBi": WBi,
        "WBj": WBj,
    }

    return bdy, data


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                                   Unit tests                                      #
#                                                                                   #
# --------------------------------------------------------------------------------- #
def test_create_boundary_mask(
    get_boundary_instance: gen_grid.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the _create_boundary_mask method."""
    # Get an instance of the Boundary class
    bdy, _ = get_boundary_instance

    # Create the reference boundary masks
    t_bdy_msk_ref = bdy.bdy_msk.copy()
    u_bdy_msk_ref = np.array(
        [
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
        ]
    )
    f_bdy_msk_ref = np.array(
        [
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
        ]
    )

    v_bdy_msk_ref = np.array(
        [
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
            [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0],
        ]
    )

    ref_bdy_msks = {
        "t": t_bdy_msk_ref,
        "u": u_bdy_msk_ref,
        "v": v_bdy_msk_ref,
        "f": f_bdy_msk_ref,
    }

    for grid, ref_bdy_msk in ref_bdy_msks.items():
        # Set the original "t" boundary mask
        bdy.bdy_msk = t_bdy_msk_ref
        # Set the grid type
        bdy.grid_type = grid
        # Create the boundary mask and compare
        bdy._create_boundary_mask()
        assert np.array_equal(
            ref_bdy_msk, bdy.bdy_msk
        ), f"Reference bdy mask differs from the bdy mask calculated for the '{grid}' grid."

    # Get an instance of the MockBoundary class
    bdy_mock, _ = get_mock_boundary

    # Create the reference boundary masks
    t_bdy_msk_ref = bdy_mock.bdy_msk.copy()

    u_bdy_msk_ref = np.array(
        [
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
        ]
    )

    v_bdy_msk_ref = np.array(
        [
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
        ]
    )

    f_bdy_msk_ref = np.array(
        [
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1],
        ]
    )

    ref_bdy_msks = {
        "t": t_bdy_msk_ref,
        "u": u_bdy_msk_ref,
        "v": v_bdy_msk_ref,
        "f": f_bdy_msk_ref,
    }

    for grid, ref_bdy_msk in ref_bdy_msks.items():
        # Set the original "t" boundary mask
        bdy_mock.bdy_msk = t_bdy_msk_ref
        # Set the grid type
        bdy_mock.grid_type = grid
        # Create the boundary mask and compare
        bdy_mock._create_boundary_mask()
        assert np.array_equal(
            ref_bdy_msk, bdy_mock.bdy_msk
        ), f"Reference bdy mask differs from the bdy mask calculated for the '{grid}' grid."


def test_create_i_j_indexes(
    get_boundary_instance: gen_grid.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __create_i_j_indexes method."""
    # Get an instance of the Boundary class
    bdy, data = get_boundary_instance

    # Generate the reference arrays
    igrid_ref = data["igrid"]
    jgrid_ref = data["jgrid"]

    # Create the i j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid_ref, igrid
    ), "Reference igrid in not equal to the igrid calculated in the Boundary class"
    assert np.array_equal(
        jgrid_ref, jgrid
    ), "Reference jgrid in not equal to the grid calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock, data_mock = get_mock_boundary

    # Generate the reference arrays
    igrid_ref = data_mock["igrid"]
    jgrid_ref = data_mock["jgrid"]

    # Create the i j indexes
    igrid, jgrid = bdy_mock._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid_ref, igrid
    ), "Reference igrid in not equal to the igrid calculated in the MockBoundary class"

    assert np.array_equal(
        jgrid_ref, jgrid
    ), "Reference jgrid in not equal to the grid calculated in the MockBoundary class"


def test_unique_rows(get_boundary_instance: gen_grid.Boundary) -> None:
    """Test the __unique_rows method."""
    # Get an instance of the Boundary class
    bdy, _ = get_boundary_instance

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
    get_boundary_instance: gen_grid.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __find_bdy method."""
    # Get an instance of the Boundary class
    bdy, data = get_boundary_instance

    # Get the i and j indexes
    igrid = data["igrid"]
    jgrid = data["jgrid"]

    # Mask index range for south
    brg_south = [1, -1, 1, -1, None, -2, 1, -1]

    # Expected indexes
    bdy_I_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    bdy_J_ref = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])

    # Create the padded boundary mask
    msk = np.pad(bdy.bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy._Boundary__find_bdy(igrid, jgrid, msk, brg_south)

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the Boundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock, data_mock = get_mock_boundary

    # Get the i and j indexes
    igrid = data_mock["igrid"]
    jgrid = data_mock["jgrid"]

    # Expected indexes
    bdy_I_ref = np.array([2, 3, 4, 5, 6])
    bdy_J_ref = np.array([2, 2, 2, 2, 2])

    # Create the padded boundary mask
    msk = np.pad(bdy_mock.bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy_mock._Boundary__find_bdy(igrid, jgrid, msk, brg_south)

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the MockBoundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the MockBoundary class"


def test_create_boundary_indexes(
    get_boundary_instance: gen_grid.Boundary, get_mock_boundary: MockBoundary
) -> None:
    """Test the __create_boundary_indexes method."""
    # Get an instance of the Boundary class
    bdy, data = get_boundary_instance

    # Get the i and j indexes
    igrid = data["igrid"]
    jgrid = data["jgrid"]

    # Get the boundary indexes references
    SBi_ref = data["SBi"]
    SBj_ref = data["SBj"]
    NBi_ref = data["NBi"]
    NBj_ref = data["NBj"]
    EBi_ref = data["EBi"]
    EBj_ref = data["EBj"]
    WBi_ref = data["WBi"]
    WBj_ref = data["WBj"]

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
    bdy_mock, data_mock = get_mock_boundary

    # Get the i and j indexes
    igrid = data_mock["igrid"]
    jgrid = data_mock["jgrid"]

    # Get the boundary indexes references
    SBi_ref = data_mock["SBi"]
    SBj_ref = data_mock["SBj"]
    NBi_ref = data_mock["NBi"]
    NBj_ref = data_mock["NBj"]
    EBi_ref = data_mock["EBi"]
    EBj_ref = data_mock["EBj"]
    WBi_ref = data_mock["WBi"]
    WBj_ref = data_mock["WBj"]

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


def test_remove_duplicate_points(
    get_boundary_instance: gen_grid.Boundary,
) -> None:
    """Test the __remove_duplicate_points method."""
    # Get an instance of the Boundary class
    bdy, _ = get_boundary_instance

    # Create mock bdy_i and bdy_r with one repeated point
    mock_bdy_i = np.array([[1, 1, 1, 1, 1], [1, 1, 3, 4, 5]])
    mock_bdy_r = np.array([0, 0, 0, 1, 1])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = np.array([[1, 1], [1, 3], [1, 4], [1, 5]])
    bdy_r_ref = np.array([0, 0, 1, 1])

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__remove_duplicate_points(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
    Boundary class after removing duplicate points."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after removing duplicate points."""

    # Create mock bdy_i and bdy_r with no repeated points
    mock_bdy_i = np.array([[1, 1, 1, 1, 1], [1, 2, 3, 4, 5]])
    mock_bdy_r = np.array([0, 0, 0, 1, 1])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = mock_bdy_i.T
    bdy_r_ref = mock_bdy_r

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__remove_duplicate_points(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
      Boundary class after removing duplicate points."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after removing duplicate points."""

    # Create mock bdy_i and bdy_r with all repeated points
    mock_bdy_i = np.array([[1, 1, 1, 1, 1], [2, 2, 2, 2, 2]])
    mock_bdy_r = np.array([1, 1, 1, 1, 1])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = mock_bdy_i.T[:1]
    bdy_r_ref = mock_bdy_r[:1]

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__remove_duplicate_points(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
      Boundary class after removing duplicate points."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after removing duplicate points."""


def test_sort_by_rimwidth(
    get_boundary_instance: gen_grid.Boundary,
) -> None:
    """Test the __sort_by_rimwidth method."""
    # Get an instance of the Boundary class
    bdy, _ = get_boundary_instance

    # Create mock bdy_i and bdy_r unsorted
    mock_bdy_i = np.array([[1, 1], [1, 2], [1, 3], [1, 4], [1, 5]])
    mock_bdy_r = np.array([1, 0, 1, 0, 0])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = np.array([[1, 2], [1, 4], [1, 5], [1, 1], [1, 3]])
    bdy_r_ref = np.array([0, 0, 0, 1, 1])

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__sort_by_rimwidth(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
    Boundary class after sorting by rimwidth."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after sorting by rimwidth."""

    # Create mock bdy_i and bdy_r sorted
    mock_bdy_i = np.array([[1, 1], [1, 2], [1, 3], [1, 4], [1, 5]])
    mock_bdy_r = np.array([0, 0, 0, 1, 1])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = mock_bdy_i
    bdy_r_ref = mock_bdy_r

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__sort_by_rimwidth(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
    Boundary class after sorting by rimwidth."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after sorting by rimwidth."""

    # Create mock bdy_i and bdy_r sorted
    mock_bdy_i = np.array([[1, 1], [1, 2], [1, 3], [1, 4], [1, 5]])
    mock_bdy_r = np.array([5, 4, 3, 2, 1])

    # Create the references bdy_i and bdy_r after removing duplicate points
    bdy_i_ref = mock_bdy_i[::-1, :]
    bdy_r_ref = mock_bdy_r[::-1]

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__sort_by_rimwidth(mock_bdy_i, mock_bdy_r)

    assert np.array_equal(
        bdy_i_ref, bdy_i
    ), """Reference bdy_i is not equal to the bdy_i calculated in the
    Boundary class after sorting by rimwidth."""

    assert np.array_equal(
        bdy_r_ref, bdy_r
    ), """Reference bdy_r is not equal to the bdy_r calculated in the
      Boundary class after sorting by rimwidth."""


def test_formalise_boundaries(
    get_boundary_instance: gen_grid.Boundary, get_mock_boundary
) -> None:
    """Test the __formalise_boundaries method."""
    # Get an instance of the Boundary class
    bdy, data = get_boundary_instance

    # Get the boundary indexes
    SBi = data["SBi"]
    SBj = data["SBj"]
    NBi = data["NBi"]
    NBj = data["NBj"]
    EBi = data["EBi"]
    EBj = data["EBj"]
    WBi = data["WBi"]
    WBj = data["WBj"]

    bdy_i, bdy_r = bdy._Boundary__formalise_boundaries(
        SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj
    )

    ref_bdy_i = np.array(
        [
            [1, 1],
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],
            [1, 6],
            [1, 7],
            [1, 8],
            [1, 9],
            [2, 1],
            [2, 2],
            [2, 3],
            [2, 4],
            [2, 5],
            [2, 6],
            [2, 7],
            [2, 8],
            [2, 9],
            [3, 1],
            [3, 2],
            [3, 8],
            [3, 9],
            [4, 1],
            [4, 2],
            [4, 8],
            [4, 9],
            [5, 1],
            [5, 2],
            [5, 8],
            [5, 9],
            [6, 1],
            [6, 2],
            [6, 8],
            [6, 9],
            [7, 1],
            [7, 2],
            [7, 8],
            [7, 9],
            [8, 1],
            [8, 2],
            [8, 3],
            [8, 4],
            [8, 5],
            [8, 6],
            [8, 7],
            [8, 8],
            [8, 9],
            [9, 1],
            [9, 2],
            [9, 3],
            [9, 4],
            [9, 5],
            [9, 6],
            [9, 7],
            [9, 8],
            [9, 9],
        ]
    )

    ref_bdy_r = np.array(
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    assert np.array_equal(
        ref_bdy_i, bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __formalise_boundaries method."

    assert np.array_equal(
        ref_bdy_r, bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __formalise_boundaries method."

    # Get an instance of the MockBoundary class
    mock_bdy, data_mock = get_mock_boundary

    # Get the boundary indexes
    SBi = data_mock["SBi"]
    SBj = data_mock["SBj"]
    NBi = data_mock["NBi"]
    NBj = data_mock["NBj"]
    EBi = data_mock["EBi"]
    EBj = data_mock["EBj"]
    WBi = data_mock["WBi"]
    WBj = data_mock["WBj"]

    bdy_i, bdy_r = bdy._Boundary__formalise_boundaries(
        SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj
    )

    ref_bdy_i = np.array(
        [
            [2, 2],
            [2, 3],
            [2, 4],
            [2, 5],
            [2, 6],
            [3, 2],
            [3, 3],
            [3, 4],
            [3, 5],
            [3, 6],
            [4, 2],
            [4, 3],
            [4, 5],
            [4, 6],
            [5, 2],
            [5, 3],
            [5, 4],
            [5, 5],
            [5, 6],
            [6, 2],
            [6, 3],
            [6, 4],
            [6, 5],
            [6, 6],
        ]
    )

    ref_bdy_r = np.array(
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    )

    assert np.array_equal(
        ref_bdy_i, bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __formalise_boundaries method."

    assert np.array_equal(
        ref_bdy_r, bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __formalise_boundaries method."


def test_smooth_interior_relaxation_gradients() -> None:
    """Test the __smooth_interior_relaxation_gradients method."""
    pass


def test_assign_smoothed_boundary_index() -> None:
    """Test the __assign_smoothed_boundary_index method."""
    pass


def test_fill() -> None:
    """Test the __fill method."""
    pass


def test_remove_landpoints_open_ocean() -> None:
    """Test the __remove_landpoints_open_ocean method."""
    pass


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
        bdy_refactor = gen_grid.Boundary(bdy_msk, settings, grd)
        bdy_refactor.create_boundary()

        # Original class
        bdy_orig = gen_grid_old.Boundary(bdy_msk, settings, grd)

        assert np.array_equal(
            bdy_refactor.bdy_i, bdy_orig.bdy_i
        ), "bdy_i in refactored Boundary class is not equal to bdy_i in original Boundary class"
        assert np.array_equal(
            bdy_refactor.bdy_r, bdy_orig.bdy_r
        ), "bdy_r in refactored Boundary class is not equal to bdy_r in original Boundary class"
