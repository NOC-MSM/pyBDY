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
