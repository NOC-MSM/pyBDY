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

from src.pybdy import nemo_bdy_extr_assist as extr_assist

# Local imports
from tests import test_nemo_bdy_chunk as synth


def test_get_ind():
    # Generate synthetic lon and lat to test.
    lon_range_d = np.arange(-10, 10, 0.2)
    lat_range_d = np.arange(30, 50, 0.2)
    lon_grid, lat_grid = np.meshgrid(lon_range_d, lat_range_d)
    bdy = synth.gen_synth_bdy(1)
    dst_lon = lon_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]
    dst_lat = lat_grid[bdy.bdy_i[:, 0], bdy.bdy_i[:, 1]]

    lon_range_s = np.arange(-10, 10, 0.3)
    lat_range_s = np.arange(30, 50, 0.5)
    lon_sc, lat_sc = np.meshgrid(lon_range_s, lat_range_s)

    imin, imax, jmin, jmax = extr_assist.get_ind(dst_lon, dst_lat, lon_sc, lat_sc)
    print(imin, imax, jmin, jmax)
    test_case = np.array([5, 62, 2, 38])
    assert (np.array([imin, imax, jmin, jmax]) == test_case).all()


def test_interp_sc_to_dst():
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
    dst1 = extr_assist.interp_sc_to_dst(sc_bdy, dist_wei, dist_fac, logger)

    sc_bdy = np.zeros((10, 5, 9)) + 0.1
    sc_bdy[:, :, 4] = 0.5
    dist_tot = np.tile(np.linspace(0.05, 0.35, num=9), (10, 5, 1))
    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
        np.exp(-0.5 * np.power(dist_tot / r0, 2))
    )
    dist_fac = np.sum(dist_wei, 2)
    dst2 = extr_assist.interp_sc_to_dst(sc_bdy, dist_wei, dist_fac, logger)

    errors = []
    if not np.isclose(dst1, np.zeros((1, 5)) + 0.2, atol=1e-4).all():
        errors.append("Does not interp 1d correct.")
    elif not np.isclose(dst2, np.zeros((10, 5)) + 0.1, atol=1e-4).all():
        errors.append("Does not interp 2d correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
