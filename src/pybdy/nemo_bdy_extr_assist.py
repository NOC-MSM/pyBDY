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
import scipy.spatial as sp


def get_ind(dst_lon, dst_lat, sc_lon, sc_lat):
    """
    Calculate indicies of max and min for data extraction.

    Parameters
    ----------
    dst_lon (np.array) : the longitude of the destination grid
    dst_lat (np.array) : the latitude of the destination grid
    sc_lon (np.array)  : the longitude of the source grid
    sc_lat (np.array)  : the latitude of the source grid

    Returns
    -------
    imin (int) : minimum i index
    imax (int) : maximum i index
    jmin (int) : minimum j index
    jmax (int) : maximum j index
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


def get_vertical_weights_3D(dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len, ind):
    """Determine 3D depth vertical weights for the linear interpolation onto Dst grid."""
    # We need sc depth in the form [sc_z_len, nbdy_ch, 9]
    sc_z_rv = np.zeros((sc_z_len, sc_z.shape[1] * sc_z.shape[2]))
    for k in range(sc_z_len):
        sc_z_rv[k, :] = sc_z[k, :, :].flatten("F")
    # sc_z_rv = sc_z.reshape(sc_z_len, -1)
    sc_z9 = sc_z_rv[:, ind]  # [sc_z_len, nbdy_ch, 9]

    # We need vertical weight in the form [dst_z_len, nbdy_ch, 9, 2]
    # Tile dst_dep by 9 to get the same size as we want all 9 source points
    # on the same bdy depth before horizontal interpolation.
    # The 9 vertical weights won't nessicarily be equal.

    dst_dep9 = np.transpose(np.tile(dst_dep, (9, 1, 1)), axes=[1, 2, 0])
    dst_dep9_rv = dst_dep9.ravel(order="F").filled(np.nan)
    z9_ind = np.zeros((dst_len_z, num_bdy, 9, 2), dtype=np.int64)

    source_tree = None
    try:
        source_tree = sp.cKDTree(
            list(zip(sc_z9.ravel(order="F"))),
            balanced_tree=False,
            compact_nodes=False,
        )
    except TypeError:  # fix for scipy 0.16.0
        source_tree = sp.cKDTree(list(zip(sc_z9.ravel(order="F"))))

    junk, nn_id = source_tree.query(list(zip(dst_dep9_rv)), k=1)

    z9_weight = 0

    return z9_weight, z9_ind


def get_vertical_weights_zco(dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len):
    """
    Determine vertical weights for the linear interpolation onto Dst grid.

    Selects 9 source points horizontally around a destination grid point.
    Calculated the distance from each source point to the destination to
    be used in weightings. The resulting arrays are [nbdy, nz, 9].

    Parameters
    ----------
    dst_dep (np.array) : the depth of the destination grid chunk [nz, nbdy]
    dst_len_z (int)    : the length of depth axis of the destination grid
    num_bdy (int)      : number of boundary points in chunk
    sc_z (np.array)    : the depth of the source grid [k, j, i]
    sc_z_len (int)     : the length of depth axis of the source grid

    Returns
    -------
    z_dist (np.array) : the distance weights of the selected points
    z_ind (np.array)  : the indices of the surrounding 9 points
    """
    # Note: At the moment z_dist and z_ind are [nbdy*nz, 2]
    # where [:, 0] is the nearest vertical index
    # and [:, 1] is the index above or below
    # i.e. the vertical index -1 for sc_z > dst_z
    # and vertical index +1 for sc_z <= dst_z

    # Allocate vertical index array
    sc_z = sc_z[:, 0, 0]
    dst_dep_rv = dst_dep.ravel(order="F").filled(np.nan)
    z_ind = np.zeros((num_bdy * dst_len_z, 2), dtype=np.int64)
    source_tree = None
    try:
        source_tree = sp.cKDTree(
            list(zip(sc_z.ravel(order="F"))),
            balanced_tree=False,
            compact_nodes=False,
        )
    except TypeError:  # fix for scipy 0.16.0
        source_tree = sp.cKDTree(list(zip(sc_z.ravel(order="F"))))

    junk, nn_id = source_tree.query(list(zip(dst_dep_rv)), k=1)

    # WORKAROUND: the tree query returns out of range val when
    # dst_dep point is NaN, causing ref problems later.
    nn_id[nn_id == sc_z_len] = sc_z_len - 1

    # Find next adjacent point in the vertical
    z_ind[:, 0] = nn_id
    z_ind[sc_z[nn_id] > dst_dep_rv[:], 1] = nn_id[sc_z[nn_id] > dst_dep_rv[:]] - 1
    z_ind[sc_z[nn_id] <= dst_dep_rv[:], 1] = nn_id[sc_z[nn_id] <= dst_dep_rv[:]] + 1
    # Adjust out of range values
    z_ind[z_ind == -1] = 0
    z_ind[z_ind == sc_z_len] = sc_z_len - 1

    # Create weightings array
    z_dist = np.abs(sc_z[z_ind] - dst_dep.T.repeat(2).reshape(len(dst_dep_rv), 2))
    rat = np.ma.sum(z_dist, axis=1)
    z_dist = 1 - (z_dist / rat.repeat(2).reshape(len(rat), 2))

    # Update z_ind for the dst array dims and vector indexing
    # Replicating this part of matlab is difficult without causing
    # a Memory Error. This workaround may be +/- brilliant
    # In theory it maximises memory efficiency
    z_ind[:, :] += np.arange(0, (num_bdy) * sc_z_len, sc_z_len)[
        np.arange(num_bdy).repeat(2 * dst_len_z)
    ].reshape(z_ind.shape)

    return z_dist, z_ind
