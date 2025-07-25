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
Created on Thu Dec 19 10:39:46 2024.

@author James Harle
@author Benjamin Barton
"""

# External imports
import numpy as np

# Local imports
from src.pybdy import nemo_bdy_chunk as chunk
from src.pybdy import nemo_bdy_gen_c as gen_grid


def test_chunk_land_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0])).all()


def test_chunk_land_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0, 1, 2])).all()


def test_chunk_land_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0])).all()


def test_chunk_land_comp():
    bdy = gen_synth_bdy(4)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0, 1])).all()


"""
def test_chunk_land_wrap():
    bdy = gen_synth_bdy(5)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0, 1])).all()
"""


def test_chunk_corner_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_corner(
        bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw
    )

    # plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    # plt.show()

    errors = []
    if len(np.unique(chunk_number)) != 4:
        errors.append("The quantity of chunks is not correct.")
    elif not (np.unique(chunk_number) == np.array([0, 1, 2, 3])).all():
        errors.append(
            "The chunk numbers are not correct."
            + np.array2string(np.unique(chunk_number))
        )
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_chunk_corner_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_corner(
        bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw
    )

    # plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    # plt.show()

    errors = []
    if len(np.unique(chunk_number)) != 4:
        errors.append("The quantity of chunks is not correct.")
    elif not (np.unique(chunk_number) == np.array([0, 1, 2, 3])).all():
        errors.append(
            "The chunk numbers are not correct."
            + np.array2string(np.unique(chunk_number))
        )
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_chunk_corner_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_corner(
        bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw
    )

    # plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    # plt.show()

    errors = []
    if len(np.unique(chunk_number)) != 1:
        errors.append("The quantity of chunks is not correct.")
    elif not (np.unique(chunk_number) == np.array([0])).all():
        errors.append(
            "The chunk numbers are not correct."
            + np.array2string(np.unique(chunk_number))
        )
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_chunk_corner_comp():
    bdy = gen_synth_bdy(4)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_corner(
        bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw
    )

    # plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    # plt.show()

    errors = []
    if len(np.unique(chunk_number)) != 7:
        errors.append("The quantity of chunks is not correct.")
    elif not (np.unique(chunk_number) == np.array([0, 1, 2, 3, 4, 5, 6])).all():
        errors.append(
            "The chunk numbers are not correct."
            + np.array2string(np.unique(chunk_number))
        )
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


"""
def test_chunk_corner_wrap():
    bdy = gen_synth_bdy(5)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_corner(
        bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw
    )

    #plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    #plt.show()

    errors = []
    if len(np.unique(chunk_number)) != 4:
        errors.append("The quantity of chunks is not correct.")
    elif not (np.unique(chunk_number) == np.array([0, 1, 2, 3])).all():
        errors.append(
            "The chunk numbers are not correct."
            + np.array2string(np.unique(chunk_number))
        )
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
"""


def test_chunk_large_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_large(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number)
    assert (np.unique(chunk_number) == np.array([0])).all()


def test_chunk_large_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_large(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number)
    assert (np.unique(chunk_number) == np.array([0, 1, 2])).all()


def test_chunk_large_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number = chunk.chunk_large(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number)
    assert (np.unique(chunk_number) == np.array([0, 1, 2, 3, 4])).all()


# Synthetic test cases


def gen_synth_bdy(map=1):
    """Generate synthetic boundaries as test cases.

    Generates a 2D array based on the selected map type.

    Args:
    ----
        map (int): Map type (1, 2, 3, 4 or 5).

    Returns:
    -------
        numpy.ndarray: Generated 2D array.
    """
    lon_range = np.arange(-10, 10, 0.2)
    lat_range = np.arange(30, 50, 0.2)

    settings = {}
    settings["rimwidth"] = 9

    if map == 1:
        # 4 open boundaries around an island
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) - 1  # out of domain
        bdy_msk[10:90, 10:90] = 1  # water
        bdy_msk[40:60, 40:60] = 0  # land

    elif map == 2:
        # 3 open boundaries split by land in the corner and side
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1  # water
        bdy_msk[90:, :] = 0  # land
        bdy_msk[:10, :10] = 0  # land
        bdy_msk[:10, 50:60] = 0  # land

    elif map == 3:
        # a single diagonal boundary
        lon_range = np.arange(-10, 10, 0.02)
        lat_range = np.arange(30, 50, 0.02)
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1  # water
        bdy_msk[(bdy_msk.shape[0] - 10) :, :] = 0  # land
        bdy_msk[:, (bdy_msk.shape[0] - 10) :] = 0  # land
        for i in range(bdy_msk.shape[0]):
            bdy_msk[: bdy_msk.shape[0] - i, :i] = -1  # out of domain

    elif map == 4:
        # complex diagonal boundaries
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1  # water
        bdy_msk[90:, :] = 0  # land
        bdy_msk[:, 90:] = 0  # land
        bdy_msk[:10, :] = -1  # out of domain
        bdy_msk[:20, 80:] = -1  # out of domain
        for i in range(60):
            bdy_msk[: 61 - i, :i] = -1  # out of domain
        for i in range(31):
            bdy_msk[i + 40 :, :i] = -1  # out of domain
        for i in range(10):
            bdy_msk[-i - 10 :, -30 + (i * 3) :] = -1  # out of domain

    elif map == 5:
        # a domain that crosses east-west around the southern ocean
        lon_range = np.arange(-180, 180, 3.6)
        lat_range = np.arange(-55, -75, -0.2)

        bdy_msk = np.zeros((len(lat_range), len(lon_range))) - 1  # out of domain
        bdy_msk[:10, :] = 0  # land
        bdy_msk[10:50, :30] = 1  # water
        bdy_msk[10:50, -30:] = 1  # water

    else:
        raise ValueError("Invalid map type. Choose 1, 2, 3, 4 or 5.")

    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind
