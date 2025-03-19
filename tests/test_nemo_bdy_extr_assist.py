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
Created on Thu Dec 21 17:33:00 2024.

@author James Harle
@author Benjamin Barton
"""

# External imports
import logging

import numpy as np
import pytest

# Local imports
from src.pybdy import nemo_bdy_extr_assist as extr_assist
from tests import test_nemo_bdy_chunk as synth_ind
from tests.synth import synth_zgrid


def test_get_ind():
    # Generate synthetic lon and lat to test.
    lon_range_d = np.arange(-10, 10, 0.2)
    lat_range_d = np.arange(30, 50, 0.2)
    lon_grid, lat_grid = np.meshgrid(lon_range_d, lat_range_d)
    bdy = synth_ind.gen_synth_bdy(1)
    dst_lon = lon_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]
    dst_lat = lat_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]

    lon_range_s = np.arange(-10, 10, 0.3)
    lat_range_s = np.arange(30, 50, 0.5)
    lon_sc, lat_sc = np.meshgrid(lon_range_s, lat_range_s)

    imin, imax, jmin, jmax = extr_assist.get_ind(dst_lon, dst_lat, lon_sc, lat_sc)
    print(imin, imax, jmin, jmax)
    test_case = np.array([5, 62, 2, 38])
    assert (np.array([imin, imax, jmin, jmax]) == test_case).all()


def test_get_ind_out_of_bound():
    # Generate synthetic lon and lat to test.
    lon_range_d = np.arange(-100, -80, 0.2)
    lat_range_d = np.arange(30, 50, 0.2)
    lon_grid, lat_grid = np.meshgrid(lon_range_d, lat_range_d)
    bdy = synth_ind.gen_synth_bdy(1)
    dst_lon = lon_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]
    dst_lat = lat_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]

    lon_range_s = np.arange(-10, 10, 0.3)
    lat_range_s = np.arange(30, 50, 0.5)
    lon_sc, lat_sc = np.meshgrid(lon_range_s, lat_range_s)

    with pytest.raises(Exception, match="") as exc_info:
        imin, imax, jmin, jmax = extr_assist.get_ind(dst_lon, dst_lat, lon_sc, lat_sc)
    assert (
        exc_info.value.args[0]
        == "The destination grid lat, lon is not inside the source grid lat, lon."
    )


def test_get_vertical_weights_zco():
    # Test the get_vertical_weights function for zco
    max_depth = 100
    num_bdy = 3
    dst_len_z = 10
    gdept, _ = synth_zgrid.synth_zco(max_depth, dst_len_z)
    dst_dep = np.tile(gdept, (num_bdy, 1)).T
    dst_dep = np.ma.masked_array(dst_dep)
    sc_z_len = 15
    gdept, _ = synth_zgrid.synth_zco(max_depth, sc_z_len)
    sc_z = np.tile(gdept, (3, 5, 1)).T

    # Centre then clockwise from 12 then corners
    ind_g = np.array([[1, 2, 1, 0, 1, 2, 0, 0, 2], [1, 1, 2, 1, 0, 2, 2, 0, 0]])
    ind = np.zeros((num_bdy, 9), dtype=int)
    ind[0, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[1, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[2, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    zco = True

    # Run function
    z9_dist, z9_ind = extr_assist.get_vertical_weights(
        dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len, ind, zco
    )
    print(z9_dist.T)
    print(z9_ind.T)
    # Check results
    ind_test = np.array(
        [[0, 2, 3, 5, 6, 8, 10, 11, 13, 14], [1, 1, 4, 4, 7, 9, 9, 12, 12, 14]]
    ).T
    dist_test = np.array(
        [
            [
                0.72222,
                0.83333,
                0.61111,
                0.94444,
                0.5,
                0.94444,
                0.61111,
                0.83333,
                0.72222,
                0.5,
            ],
            [
                0.27777,
                0.16666,
                0.38888,
                0.05555,
                0.5,
                0.05555,
                0.38888,
                0.16666,
                0.27777,
                0.5,
            ],
        ]
    ).T

    errors = []
    if not (z9_ind[:dst_len_z, :] == ind_test).all():
        errors.append("Error with vertical index z9_ind.")
    elif not np.isclose(z9_dist.filled(-1)[:dst_len_z, :], dist_test, atol=1e-4).all():
        errors.append("Error with vertical weights z9_dist.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_get_vertical_weights_sco():
    # Test the get_vertical_weights function with sco
    num_bdy = 3
    dst_len_z = 10
    bdy_bathy = np.array([80.5, 100, 60])  # bathy
    dst_dep, dst_depw = synth_zgrid.synth_sco(bdy_bathy, dst_len_z)
    dst_dep = np.ma.masked_array(dst_dep)
    sc_z_len = 15
    sc_bathy = np.zeros((3, 5)) + 100
    sc_bathy[:, 0] = 80.5
    sc_bathy[:, -2:] = 60
    sc_z, sc_zw = synth_zgrid.synth_sco(sc_bathy, sc_z_len)

    # Centre then clockwise from 12 then corners
    ind_g = np.array([[1, 2, 1, 0, 1, 2, 0, 0, 2], [1, 1, 2, 1, 0, 2, 2, 0, 0]])
    ind = np.zeros((num_bdy, 9), dtype=int)
    ind[0, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[1, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[2, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    zco = False

    # Run function
    z9_dist, z9_ind = extr_assist.get_vertical_weights(
        dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len, ind, zco
    )

    # Check results
    ind_test = np.array(
        [[0, 2, 3, 4, 6, 7, 8, 9, 9, 10], [1, 1, 2, 5, 5, 6, 7, 8, 10, 9]]
    ).T
    dist_test = np.array(
        [
            [
                0.83656,
                0.50909,
                0.94349,
                0.68233,
                0.64876,
                0.85992,
                0.88376,
                0.68497,
                0.76830,
                0.68562,
            ],
            [
                0.16343,
                0.49090,
                0.05650,
                0.31766,
                0.35123,
                0.14007,
                0.11623,
                0.31502,
                0.23169,
                0.31437,
            ],
        ]
    ).T

    errors = []
    if not (z9_ind[:dst_len_z, :] == ind_test).all():
        errors.append("Error with vertical index z9_ind.")
    elif not np.isclose(z9_dist.filled(-1)[:dst_len_z, :], dist_test, atol=1e-4).all():
        errors.append("Error with vertical weights z9_dist.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_interp_vertical():
    # Test the interp_vertical function
    logger = logging.getLogger(__name__)
    max_depth = 100
    num_bdy = 3
    dst_len_z = 10
    bdy_bathy = np.array([80.5, 100, 60])
    gdept, _ = synth_zgrid.synth_zco(max_depth, dst_len_z)
    dst_dep = np.tile(gdept, (num_bdy, 1)).T
    dst_dep = np.ma.masked_array(dst_dep)
    sc_z_len = 15
    gdept, _ = synth_zgrid.synth_zco(max_depth, sc_z_len)
    sc_z = np.tile(gdept, (3, 5, 1)).T
    sc_bdy = np.tile(np.linspace(12, 5, num=sc_z_len), (3, 5, 1)).T  # Temperature data

    # Centre then clockwise from 12 then corners
    ind_g = np.array([[1, 2, 1, 0, 1, 2, 0, 0, 2], [1, 1, 2, 1, 0, 2, 2, 0, 0]])
    ind = np.zeros((num_bdy, 9), dtype=int)
    ind[0, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[1, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")
    ind_g[1, :] = ind_g[1, :] + 1
    ind[2, :] = np.ravel_multi_index(ind_g, (3, 5), order="F")

    sc_bdy = sc_bdy.reshape((sc_bdy.shape[0], sc_bdy.shape[1] * sc_bdy.shape[2]))[
        :, ind
    ]
    zco = True

    z_dist, z_ind = extr_assist.get_vertical_weights(
        dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len, ind, zco
    )
    data_ind, _ = extr_assist.valid_index(sc_bdy, logger)

    # Run function
    sc_bdy_lev = extr_assist.interp_vertical(
        sc_bdy, dst_dep, bdy_bathy, z_ind, z_dist, data_ind, num_bdy
    )
    sc_bdy_lev[np.isnan(sc_bdy_lev)] = -1

    # Check results
    lev_test = np.array(
        [
            11.86111,
            11.08333,
            10.30555,
            9.52777,
            8.75,
            7.97222,
            7.19444,
            -1.0,
            -1.0,
            -1.0,
        ]
    )

    errors = []
    if not (sc_bdy_lev.shape == (dst_len_z, num_bdy, 9)):
        errors.append("Error with output sc_bdy_lev shape.")
    elif not np.isclose(sc_bdy_lev[:, 0, 0], lev_test, atol=1e-4).all():
        errors.append("Error with sc_bdy_lev.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_distance_weights():
    # Tests the distance_weights function
    logger = logging.getLogger(__name__)
    r0 = 0.041666666
    sc_z_len = 1

    sc_bdy = np.zeros((1, 5, 9)) + 0.1
    sc_bdy[:, :, 0] = 0.225
    dist_tot = np.tile(np.linspace(0.05, 0.35, num=9), (5, 1))
    dist_wei, dist_fac = extr_assist.distance_weights(
        sc_bdy, dist_tot, sc_z_len, r0, logger
    )

    errors = []
    if not np.isclose(dist_wei[0, 0, 0], 4.66046529, atol=1e-5):
        errors.append("Error with dist_wei.")
    elif not np.isclose(dist_fac[0, 0], 5.82729953, atol=1e-5):
        errors.append("Error with dist_fac.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_valid_index():
    # Tests the valid_index function
    logger = logging.getLogger(__name__)
    sc_bdy = np.zeros((10, 5, 9)) + 0.1
    sc_bdy[:, 0:2, :] = np.nan
    sc_bdy[7:, -1, :] = np.nan

    data_ind, nan_ind = extr_assist.valid_index(sc_bdy, logger)

    errors = []
    if not (data_ind[:, 0] == np.array([0, 0, 9, 9, 6])).all():
        errors.append("Error with max depth index data_ind.")
    elif not (np.sum(nan_ind) == 23):
        errors.append("Error with land indices nan_ind.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_interp_horizontal():
    # Test the horizontal interpolation by weighted average
    logger = logging.getLogger(__name__)
    r0 = 0.041666666

    sc_bdy = np.zeros((1, 5, 9)) + 0.1
    sc_bdy[:, :, 0] = 0.225
    dist_tot = np.tile(np.linspace(0.05, 0.35, num=9), (1, 5, 1))
    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
        np.exp(-0.5 * np.power(dist_tot / r0, 2))
    )
    dist_fac = np.sum(dist_wei, 2)
    dst1 = extr_assist.interp_horizontal(sc_bdy, dist_wei, dist_fac, logger)

    sc_bdy = np.zeros((10, 5, 9)) + 0.1
    sc_bdy[:, :, 4] = 0.5
    dist_tot = np.tile(np.linspace(0.05, 0.35, num=9), (10, 5, 1))
    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
        np.exp(-0.5 * np.power(dist_tot / r0, 2))
    )
    dist_fac = np.sum(dist_wei, 2)
    dst2 = extr_assist.interp_horizontal(sc_bdy, dist_wei, dist_fac, logger)

    errors = []
    if not np.isclose(dst1, np.zeros((1, 5)) + 0.2, atol=1e-4).all():
        errors.append("Does not interp 1d correct.")
    elif not np.isclose(dst2, np.zeros((10, 5)) + 0.1, atol=1e-4).all():
        errors.append("Does not interp 2d correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
