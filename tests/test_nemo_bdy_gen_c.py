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

    return mock_bdy


@pytest.fixture(scope="session")
def expected_data_mock_boundary():
    """Get expected data for the MockBoundary class."""
    # Expected data for the MockBoundary class for the "t" grid
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

    bdy_i = np.array(
        [
            [
                2,
                3,
                4,
                5,
                6,
                2,
                3,
                4,
                5,
                6,
                2,
                2,
                2,
                2,
                2,
                6,
                6,
                6,
                6,
                6,
                2,
                3,
                4,
                5,
                6,
                2,
                3,
                4,
                5,
                6,
                3,
                3,
                3,
                3,
                3,
                5,
                5,
                5,
                5,
                5,
            ],
            [
                2,
                2,
                2,
                2,
                2,
                6,
                6,
                6,
                6,
                6,
                2,
                3,
                4,
                5,
                6,
                2,
                3,
                4,
                5,
                6,
                3,
                3,
                3,
                3,
                3,
                5,
                5,
                5,
                5,
                5,
                2,
                3,
                4,
                5,
                6,
                2,
                3,
                4,
                5,
                6,
            ],
        ]
    )

    bdy_r = np.array(
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
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
        ]
    )

    bdy_i_remove_duplicate_points = np.array(
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

    bdy_r_remove_duplicate_points = np.array(
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    )

    r_msk = np.array(
        [
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 1.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 2.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 1.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ]
    )

    r_msk_orig = np.array(
        [
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 1.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 2.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 1.0, 1.0, 1.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ]
    )

    bdy_i_remove_landpoints_open_ocean = bdy_i_remove_duplicate_points.copy()
    bdy_r_remove_landpoints_open_ocean = bdy_r_remove_duplicate_points.copy()

    bdy_i_assign_smoothed_boundary_index = np.array(
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

    bdy_r_assign_smoothed_boundary_index = np.array(
        [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    )

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
        "bdy_i": bdy_i,
        "bdy_r": bdy_r,
        "bdy_i_remove_duplicate_points": bdy_i_remove_duplicate_points,
        "bdy_r_remove_duplicate_points": bdy_r_remove_duplicate_points,
        "bdy_i_remove_landpoints_open_ocean": bdy_i_remove_landpoints_open_ocean,
        "bdy_r_remove_landpoints_open_ocean": bdy_r_remove_landpoints_open_ocean,
        "bdy_i_assign_smoothed_boundary_index": bdy_i_assign_smoothed_boundary_index,
        "bdy_r_assign_smoothed_boundary_index": bdy_r_assign_smoothed_boundary_index,
        "r_msk": r_msk,
        "r_msk_orig": r_msk_orig,
    }

    return data


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


@pytest.fixture(scope="session")
def expected_data_boundary():
    """Get expected data for the Boundary class."""
    # Expected data for the Boundary class for the "t" grid
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

    bdy_i = np.array(
        [
            [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
            ],
            [
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
            ],
        ]
    )

    bdy_r = np.array(
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
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
        ]
    )
    bdy_i_remove_duplicate_points = np.array(
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

    bdy_r_remove_duplicate_points = np.array(
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

    r_msk = np.array(
        [
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ],
            [np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, np.nan],
            [np.nan, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, np.nan],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ],
        ]
    )

    r_msk_orig = r_msk.copy()

    bdy_i_remove_landpoints_open_ocean = bdy_i_remove_duplicate_points.copy()
    bdy_r_remove_landpoints_open_ocean = bdy_r_remove_duplicate_points.copy()

    bdy_i_assign_smoothed_boundary_index = np.array(
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

    bdy_r_assign_smoothed_boundary_index = np.array(
        [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    )

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
        "bdy_i": bdy_i,
        "bdy_r": bdy_r,
        "bdy_i_remove_duplicate_points": bdy_i_remove_duplicate_points,
        "bdy_r_remove_duplicate_points": bdy_r_remove_duplicate_points,
        "bdy_i_remove_landpoints_open_ocean": bdy_i_remove_landpoints_open_ocean,
        "bdy_r_remove_landpoints_open_ocean": bdy_r_remove_landpoints_open_ocean,
        "bdy_i_assign_smoothed_boundary_index": bdy_i_assign_smoothed_boundary_index,
        "bdy_r_assign_smoothed_boundary_index": bdy_r_assign_smoothed_boundary_index,
        "r_msk": r_msk,
        "r_msk_orig": r_msk_orig,
    }

    return data


@pytest.fixture(scope="function")
def get_boundary_instance(
    get_mask_settings: Tuple[np.ndarray, dict]
) -> gen_grid.Boundary:
    """Get an instance of the Boundary refactored class and intermediate data."""
    bdy_msk, settings = get_mask_settings
    bdy = gen_grid.Boundary(bdy_msk, settings, "t")

    return bdy


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                                   Unit tests                                      #
#                                                                                   #
# --------------------------------------------------------------------------------- #
def test_create_boundary_mask(
    get_boundary_instance: gen_grid.Boundary,
    get_mock_boundary: MockBoundary,
) -> None:
    """Test the _create_boundary_mask method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

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
    bdy_mock = get_mock_boundary

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
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __create_i_j_indexes method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Create the i j indexes
    igrid, jgrid = bdy._Boundary__create_i_j_indexes()

    assert np.array_equal(
        igrid, expected_data_boundary["igrid"]
    ), "Reference igrid in not equal to the igrid calculated in the Boundary class"
    assert np.array_equal(
        jgrid, expected_data_boundary["jgrid"]
    ), "Reference jgrid in not equal to the grid calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Create the i j indexes
    igrid, jgrid = bdy_mock._Boundary__create_i_j_indexes()

    assert np.array_equal(
        expected_data_mock_boundary["igrid"], igrid
    ), "Reference igrid in not equal to the igrid calculated in the MockBoundary class"

    assert np.array_equal(
        expected_data_mock_boundary["jgrid"], jgrid
    ), "Reference jgrid in not equal to the grid calculated in the MockBoundary class"


def test_create_boundary_indexes(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __create_boundary_indexes method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Create the boundary indexes
    SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj = bdy._Boundary__create_boundary_indexes(
        expected_data_boundary["igrid"], expected_data_boundary["jgrid"]
    )

    # Check the results
    assert np.array_equal(
        expected_data_boundary["SBi"], SBi
    ), "Reference SBi is not equal to the SBi calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["SBj"], SBj
    ), "Reference SBj is not equal to the SBj calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["NBi"], NBi
    ), "Reference NBi is not equal to the NBi calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["NBj"], NBj
    ), "Reference NBj is not equal to the NBj calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["EBi"], EBi
    ), "Reference EBi is not equal to the EBi calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["EBj"], EBj
    ), "Reference EBj is not equal to the EBj calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["WBi"], WBi
    ), "Reference WBi is not equal to the WBi calculated in the Boundary class"
    assert np.array_equal(
        expected_data_boundary["WBj"], WBj
    ), "Reference WBj is not equal to the WBj calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

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
    ) = bdy_mock._Boundary__create_boundary_indexes(
        expected_data_mock_boundary["igrid"], expected_data_mock_boundary["jgrid"]
    )

    # Check the results
    assert np.array_equal(
        expected_data_mock_boundary["SBi"], SBi
    ), "Reference SBi is not equal to the SBi calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["SBj"], SBj
    ), "Reference SBj is not equal to the SBj calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["NBi"], NBi
    ), "Reference NBi is not equal to the NBi calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["NBj"], NBj
    ), "Reference NBj is not equal to the NBj calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["EBi"], EBi
    ), "Reference EBi is not equal to the EBi calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["EBj"], EBj
    ), "Reference EBj is not equal to the EBj calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["WBi"], WBi
    ), "Reference WBi is not equal to the WBi calculated in the MockBoundary class."

    assert np.array_equal(
        expected_data_mock_boundary["WBj"], WBj
    ), "Reference WBj is not equal to the WBj calculated in the MockBoundary class."


def test_formalise_boundaries(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __formalise_boundaries method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Formalise boundaries
    bdy_i, bdy_r = bdy._Boundary__formalise_boundaries(
        expected_data_boundary["SBi"],
        expected_data_boundary["SBj"],
        expected_data_boundary["NBi"],
        expected_data_boundary["NBj"],
        expected_data_boundary["EBi"],
        expected_data_boundary["EBj"],
        expected_data_boundary["WBi"],
        expected_data_boundary["WBj"],
    )

    assert np.array_equal(
        expected_data_boundary["bdy_i"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __formalise_boundaries method."

    assert np.array_equal(
        expected_data_boundary["bdy_r"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __formalise_boundaries method."

    # Get an instance of the MockBoundary class
    mock_bdy = get_mock_boundary

    # Get the boundary indexes
    # Formalise boundaries
    bdy_i, bdy_r = mock_bdy._Boundary__formalise_boundaries(
        expected_data_mock_boundary["SBi"],
        expected_data_mock_boundary["SBj"],
        expected_data_mock_boundary["NBi"],
        expected_data_mock_boundary["NBj"],
        expected_data_mock_boundary["EBi"],
        expected_data_mock_boundary["EBj"],
        expected_data_mock_boundary["WBi"],
        expected_data_mock_boundary["WBj"],
    )

    assert np.array_equal(
        expected_data_mock_boundary["bdy_i"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __formalise_boundaries method."

    assert np.array_equal(
        expected_data_mock_boundary["bdy_r"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __formalise_boundaries method."


def test_remove_duplicate_points(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __remove_duplicate_points method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Remove duplicate points
    bdy_i, bdy_r = bdy._Boundary__remove_duplicate_points(
        expected_data_boundary["bdy_i"], expected_data_boundary["bdy_r"]
    )

    assert np.array_equal(
        expected_data_boundary["bdy_i_remove_duplicate_points"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __remove_duplicate_points method."

    assert np.array_equal(
        expected_data_boundary["bdy_r_remove_duplicate_points"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __remove_duplicate_points method."

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Remove duplicate points
    bdy_i, bdy_r = bdy_mock._Boundary__remove_duplicate_points(
        expected_data_mock_boundary["bdy_i"], expected_data_mock_boundary["bdy_r"]
    )

    assert np.array_equal(
        expected_data_mock_boundary["bdy_i_remove_duplicate_points"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __remove_duplicate_points method."

    assert np.array_equal(
        expected_data_mock_boundary["bdy_r_remove_duplicate_points"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __remove_duplicate_points method."

    # Other tests for remove_duplicate_points
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


def test_remove_landpoints_open_ocean(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __remove_landpoints_open_ocean method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Remove duplicate points
    bdy_i, bdy_r, _ = bdy._Boundary__remove_landpoints_open_ocean(
        bdy.bdy_msk,
        expected_data_boundary["bdy_i_remove_duplicate_points"],
        expected_data_boundary["bdy_r_remove_duplicate_points"],
    )

    assert np.array_equal(
        expected_data_boundary["bdy_i_remove_landpoints_open_ocean"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __remove_duplicate_points method."

    assert np.array_equal(
        expected_data_boundary["bdy_r_remove_landpoints_open_ocean"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __remove_duplicate_points method."

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Remove duplicate points
    bdy_i, bdy_r, _ = bdy_mock._Boundary__remove_landpoints_open_ocean(
        bdy_mock.bdy_msk,
        expected_data_mock_boundary["bdy_i_remove_duplicate_points"],
        expected_data_mock_boundary["bdy_r_remove_duplicate_points"],
    )

    assert np.array_equal(
        expected_data_mock_boundary["bdy_i_remove_landpoints_open_ocean"], bdy_i
    ), "Reference bdy_i is not equal to the bdy_i calculated by the __remove_duplicate_points method."

    assert np.array_equal(
        expected_data_mock_boundary["bdy_r_remove_landpoints_open_ocean"], bdy_r
    ), "Reference bdy_r is not equal to the bdy_r calculated by the __remove_duplicate_points method."


def test_smooth_interior_relaxation_gradients(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __smooth_interior_relaxation_gradients method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Smooth interior relaxation gradients
    r_msk, r_msk_orig = bdy._Boundary__smooth_interior_relaxation_gradients(
        expected_data_boundary["bdy_i_remove_landpoints_open_ocean"],
        expected_data_boundary["bdy_r_remove_landpoints_open_ocean"],
    )

    assert np.array_equal(
        r_msk, expected_data_boundary["r_msk"], equal_nan=True
    ), "Reference r_msk is not equal to the r_msk calculated by the\
          __smooth_interior_relaxation_gradients method."

    assert np.array_equal(
        r_msk_orig, expected_data_boundary["r_msk_orig"], equal_nan=True
    ), "Reference r_msk_orig is not equal to the r_msk_orig calculated by the\
          __smooth_interior_relaxation_gradients method."

    # Get an instance of the MockBoundary class
    mock_bdy = get_mock_boundary

    # Smooth interior relaxation gradients
    r_msk, r_msk_orig = mock_bdy._Boundary__smooth_interior_relaxation_gradients(
        expected_data_mock_boundary["bdy_i_remove_landpoints_open_ocean"],
        expected_data_mock_boundary["bdy_r_remove_landpoints_open_ocean"],
    )

    assert np.array_equal(
        r_msk, expected_data_mock_boundary["r_msk"], equal_nan=True
    ), "Reference r_msk is not equal to the r_msk calculated by the\
        __smooth_interior_relaxation_gradients method."

    assert np.array_equal(
        r_msk_orig, expected_data_mock_boundary["r_msk_orig"], equal_nan=True
    ), "Reference r_msk_orig is not equal to the r_msk_orig calculated by the\
          __smooth_interior_relaxation_gradients method."


def test_assign_smoothed_boundary_index(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __assign_smoothed_boundary_index method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Assign smoothed boundary index
    bdy_i, bdy_r = bdy._Boundary__assign_smoothed_boundary_index(
        expected_data_boundary["bdy_i_remove_landpoints_open_ocean"],
        expected_data_boundary["bdy_r_remove_landpoints_open_ocean"],
        expected_data_boundary["r_msk"],
        expected_data_boundary["r_msk_orig"],
        expected_data_boundary["igrid"],
        expected_data_boundary["jgrid"],
    )

    assert np.array_equal(
        bdy_i, expected_data_boundary["bdy_i_assign_smoothed_boundary_index"]
    ), "Reference bdy_i is not equal to the bdy_i calculated by the\
          __assign_smoothed_boundary_index method."

    assert np.array_equal(
        bdy_r, expected_data_boundary["bdy_r_assign_smoothed_boundary_index"]
    ), "Reference bdy_r is not equal to the bdy_r calculated by the\
          __assign_smoothed_boundary_index method."

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Assign smoothed boundary index
    bdy_i, bdy_r = bdy_mock._Boundary__assign_smoothed_boundary_index(
        expected_data_mock_boundary["bdy_i_remove_landpoints_open_ocean"],
        expected_data_mock_boundary["bdy_r_remove_landpoints_open_ocean"],
        expected_data_mock_boundary["r_msk"],
        expected_data_mock_boundary["r_msk_orig"],
        expected_data_mock_boundary["igrid"],
        expected_data_mock_boundary["jgrid"],
    )

    assert np.array_equal(
        bdy_i, expected_data_mock_boundary["bdy_i_assign_smoothed_boundary_index"]
    ), "Reference bdy_i is not equal to the bdy_i calculated by the\
          __assign_smoothed_boundary_index method."

    assert np.array_equal(
        bdy_r, expected_data_mock_boundary["bdy_r_assign_smoothed_boundary_index"]
    ), "Reference bdy_r is not equal to the bdy_r calculated by the\
          __assign_smoothed_boundary_index method."


def test_sort_by_rimwidth(
    get_boundary_instance: gen_grid.Boundary,
) -> None:
    """Test the __sort_by_rimwidth method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

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


def test_unique_rows(get_boundary_instance: gen_grid.Boundary) -> None:
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
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __find_bdy method."""
    # Get an instance of the Boundary class
    bdy = get_boundary_instance

    # Mask index range for south
    brg_south = [1, -1, 1, -1, None, -2, 1, -1]

    # Expected indexes
    bdy_I_ref = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    bdy_J_ref = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])

    # Create the padded boundary mask
    msk = np.pad(bdy.bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy._Boundary__find_bdy(
        expected_data_boundary["igrid"], expected_data_boundary["jgrid"], msk, brg_south
    )

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the Boundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the Boundary class"

    # Get an instance of the MockBoundary class
    bdy_mock = get_mock_boundary

    # Expected indexes
    bdy_I_ref = np.array([2, 3, 4, 5, 6])
    bdy_J_ref = np.array([2, 2, 2, 2, 2])

    # Create the padded boundary mask
    msk = np.pad(bdy_mock.bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))

    # Create the boundary indexes references
    bdy_I, bdy_J = bdy_mock._Boundary__find_bdy(
        expected_data_mock_boundary["igrid"],
        expected_data_mock_boundary["jgrid"],
        msk,
        brg_south,
    )

    assert np.array_equal(
        bdy_I, bdy_I_ref
    ), "Reference bdy_I is not equal to the bdy_I calculated in the MockBoundary class"

    assert np.array_equal(
        bdy_J, bdy_J_ref
    ), "Reference bdy_J is not equal to the bdy_J calculated in the MockBoundary class"


def test_fill(
    get_boundary_instance: gen_grid.Boundary,
    expected_data_boundary: dict,
    get_mock_boundary: MockBoundary,
    expected_data_mock_boundary: dict,
) -> None:
    """Test the __fill method."""
    pass


# --------------------------------------------------------------------------------- #
#                                                                                   #
#                                Functional tests                                   #
#                                                                                   #
# --------------------------------------------------------------------------------- #
def test_grid_refactor(get_mask_settings: Tuple[np.ndarray, dict]) -> None:
    """Test the final results of the refactored Boundary class."""
    bdy_msk, settings = get_mask_settings

    for grd in ["t"]:
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
