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
Created on Thu Dec 21 17:34:00 2024.

@author James Harle
@author Benjamin Barton
"""

# External imports
import numpy as np


def get_ind(dst_lon, dst_lat, sc_lon, sc_lat):
    """
    Calculate indicies of max and min for data extraction.

    Parameters
    ----------
    dst_lon -- the longitude of the destination grid
    dst_lat -- the latitude of the destination grid
    sc_lon -- the longitude of the source grid
    sc_lat -- the latitude of the source grid

    Returns
    -------
    imin -- minimum i index
    imax -- maximum i index
    jmin -- minimum j index
    jmax -- maximum j index
    """
    ind_e = sc_lon < np.amax(dst_lon)
    ind_w = sc_lon > np.amin(dst_lon)
    ind_ew = np.logical_and(ind_e, ind_w)
    ind_s = sc_lat > np.amin(dst_lat)
    ind_n = sc_lat < np.amax(dst_lat)
    ind_sn = np.logical_and(ind_s, ind_n)

    ind = np.where(np.logical_and(ind_ew, ind_sn) != 0)
    ind_s = np.argsort(ind[1])

    sub_j = ind[0][ind_s]
    sub_i = ind[1][ind_s]

    # Find I/J range

    imin = np.maximum(np.amin(sub_i) - 2, 0)
    imax = np.minimum(np.amax(sub_i) + 2, len(sc_lon[0, :]) - 1) + 1
    jmin = np.maximum(np.amin(sub_j) - 2, 0)
    jmax = np.minimum(np.amax(sub_j) + 2, len(sc_lon[:, 0]) - 1) + 1

    return imin, imax, jmin, jmax
