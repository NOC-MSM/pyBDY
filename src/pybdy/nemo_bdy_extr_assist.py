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
    """Determine 3D depth vertical weights for the linear interpolation onto Dst grid.

    Selects 9 source points horizontally around a destination grid point.
    Calculated the distance from each source point to the destination to
    be used in weightings. The resulting arrays are [nz, nbdy, 9, 2].

    Parameters
    ----------
    dst_dep (np.array) : the depth of the destination grid chunk [nz, nbdy]
    dst_len_z (int)    : the length of depth axis of the destination grid
    num_bdy (int)      : number of boundary points in chunk
    sc_z (np.array)    : the depth of the source grid [k, j, i]
    sc_z_len (int)     : the length of depth axis of the source grid
    ind (np.array)     : indices of bdy points and 9 nearest neighbours

    Returns
    -------
    z9_dist (np.array) : the distance weights of the selected points
    z9_ind (np.array)  : the indices of the sc depth above and below bdy
    """
    # We need sc depth in the form [sc_z_len, nbdy_ch, 9]
    sc_z_rv = np.zeros((sc_z_len, sc_z.shape[1] * sc_z.shape[2]))
    for k in range(sc_z_len):
        sc_z_rv[k, :] = sc_z[k, :, :].flatten("F")

    sc_z9 = sc_z_rv[:, ind]  # [sc_z_len, nbdy_ch, 9]

    # We need vertical weight in the form [dst_z_len, nbdy_ch, 9, 2]
    # Tile dst_dep by 9 to get the same size as we want all 9 source points
    # on the same bdy depth before horizontal interpolation.
    # The 9 vertical weights won't nessicarily be equal.

    dst_dep9 = np.transpose(
        np.tile(dst_dep, (9, 1, 1)), axes=[1, 2, 0]
    )  # [dst_z_len, nbdy_ch, 9]
    dst_dep9 = dst_dep9.filled(np.nan)
    z9_ind = np.zeros((dst_len_z, num_bdy, 9, 2), dtype=np.int64)
    z9_dist = np.ma.zeros((dst_len_z, num_bdy, 9, 2))

    source_tree = None
    for i in range(num_bdy):
        for j in range(9):
            try:
                source_tree = sp.cKDTree(
                    list(zip(sc_z9[:, i, j])),
                    balanced_tree=False,
                    compact_nodes=False,
                )
            except TypeError:  # fix for scipy 0.16.0
                source_tree = sp.cKDTree(list(zip(sc_z9[:, i, j])))

            junk, nn_id = source_tree.query(list(zip(dst_dep9[:, i, j])), k=1)

            # WORKAROUND: the tree query returns out of range val when
            # dst_dep point is NaN, causing ref problems later.
            nn_id[nn_id == sc_z_len] = sc_z_len - 1

            # Find next adjacent point in the vertical
            z9_ind[:, i, j, 0] = nn_id
            z9_ind[sc_z9[nn_id, i, j] > dst_dep9[:, i, j], i, j, 1] = (
                nn_id[sc_z9[nn_id, i, j] > dst_dep9[:, i, j]] - 1
            )
            z9_ind[sc_z9[nn_id, i, j] <= dst_dep9[:, i, j], i, j, 1] = (
                nn_id[sc_z9[nn_id, i, j] <= dst_dep9[:, i, j]] + 1
            )

    # Adjust out of range values
    z9_ind[z9_ind == -1] = 0
    z9_ind[z9_ind == sc_z_len] = sc_z_len - 1

    for i in range(num_bdy):
        for j in range(9):
            # Create weightings array
            z9_dist[:, i, j, :] = np.abs(
                sc_z9[z9_ind[:, i, j, :], i, j] - np.tile(dst_dep9[:, i, j], (2, 1)).T
            )

    rat = np.ma.sum(z9_dist, axis=3)
    z9_dist = 1 - (z9_dist / np.tile(rat.T, (2, 1, 1, 1)).T)

    # Update z_ind for the dst array dims and vector indexing
    # Replicating this part of matlab is difficult without causing
    # a Memory Error. This workaround may be +/- brilliant
    # In theory it maximises memory efficiency

    # z9_ind[:, :, :, :] += np.arange(0, num_bdy * sc_z_len, sc_z_len)[
    #    np.arange(num_bdy).repeat(2 * dst_len_z)
    # ].reshape(z_ind.shape)

    return z9_dist, z9_ind


def get_vertical_weights_zco(dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len):
    """
    Determine vertical weights for the linear interpolation onto Dst grid.

    Calculated the vertical distance from each source point to the destination to
    be used in weightings. The resulting arrays are [nbdy * nz, 2].

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
    z_ind (np.array)  : the indices of the sc depth above and below bdy
    """
    # Note: z_dist and z_ind are [nbdy*nz, 2]
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
    z_ind[:, :] += np.arange(0, num_bdy * sc_z_len, sc_z_len)[
        np.arange(num_bdy).repeat(2 * dst_len_z)
    ].reshape(z_ind.shape)

    return z_dist, z_ind


def interp_vertical(sc_bdy, dst_dep, bdy_z, z_ind, z_dist, data_ind, sc_z_len, num_bdy):
    """
    Interpolate source data onto destination vertical levels.

    Parameters
    ----------
    sc_bdy (np.array)   : souce data [nz_sc, nbdy, 9]
    dst_dep (np.array)  : the depth of the destination grid chunk [nz, nbdy]
    bdy_z (np.array)    : the length of depth axis of the destination grid
    z_ind (np.array)    : the indices of the sc depth above and below bdy
    z_dist (np.array)   : the distance weights of the selected points
    data_ind (np.array) : bool points above bathymetry that are valid
    sc_z_len (int)      : the length of depth axis of the source grid
    num_bdy (int)       : number of boundary points in chunk

    Returns
    -------
    data_out (np.array) : source data on destination depth levels
    """
    # If all else fails fill down using deepest pt

    # sc_bdy = sc_bdy[:, :, 0].flatten("F")
    # print(sc_bdy.shape, data_ind.shape)
    # sc_bdy += (sc_bdy == 0) * sc_bdy[data_ind].repeat(sc_z_len)

    sc_bdy_lev = np.ma.zeros((dst_dep.shape[0], sc_bdy.shape[1], sc_bdy.shape[2]))
    for i in range(num_bdy):
        for j in range(9):
            # If all else fails fill down using deepest pt
            sc_bdy[np.isnan(sc_bdy[:, i, j]), i, j] = sc_bdy[data_ind[i, j], i, j]
            # Weighted averaged on new vertical grid
            sc_bdy_lev[:, i, j] = (
                sc_bdy[z_ind[:, i, j, 0], i, j] * z_dist[:, i, j, 0]
                + sc_bdy[z_ind[:, i, j, 1], i, j] * z_dist[:, i, j, 1]
            )

    # If z-level replace data below bed
    ind_z = np.transpose(np.tile(bdy_z, (len(dst_dep), 9, 1)), axes=(0, 2, 1))
    dst_dep9 = np.transpose(np.tile(dst_dep, (9, 1, 1)), axes=[1, 2, 0])
    ind_z -= dst_dep9
    ind_z = ind_z < 0
    sc_bdy_lev[ind_z] = np.nan
    sc_bdy_lev.filled(np.nan)

    return sc_bdy_lev


def distance_weights(sc_bdy, dist_tot, sc_z_len, r0, logger):
    """
    Find the distance weightings for averaging source data to destination.

    Args:
    ----
        sc_bdy (numpy.array)    : source data
        dist_tot (numpy.array)  : distance from dst point to 9 nearest sc points
        sc_z_len (int)          : the number of depth levels
        r0 (float)              : correlation distance
        logger                  : log of statements

    Returns:
    -------
        dist_wei (numpy.array)  : weightings for averaging
        dist_fac (numpy.array)  : total weighting factor
    """
    # identify valid pts
    data_ind = np.invert(np.isnan(sc_bdy))

    # dist_tot is currently 2D so extend along depth
    # axis to allow single array calc later, also remove
    # any invalid pts using our eldritch data_ind
    logger.info(
        "DIST TOT ZEROS BEFORE %s",
        np.sum(dist_tot == 0),
    )
    dist_tot = (
        np.repeat(dist_tot, sc_z_len).reshape(
            dist_tot.shape[0],
            dist_tot.shape[1],
            sc_z_len,
        )
    ).transpose(2, 0, 1)
    dist_tot *= data_ind

    logger.info("DIST TOT ZEROS %s", np.sum(dist_tot == 0))
    logger.info("DIST IND ZEROS %s", np.sum(data_ind == 0))

    # Identify problem pts due to grid discontinuities
    # using dists >  lat
    over_dist = np.sum(dist_tot[:] > 4)
    if over_dist > 0:
        raise RuntimeError(
            """Distance between source location
                              and new boundary points is greater
                              than 4 degrees of lon/lat"""
        )

    # Calculate guassian weighting with correlation dist
    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
        np.exp(-0.5 * np.power(dist_tot / r0, 2))
    )
    # Calculate sum of weightings
    dist_fac = np.sum(dist_wei * data_ind, 2)

    return dist_wei, dist_fac


def valid_index(sc_bdy, logger):
    """
    Find an array of valid indicies.

    Args:
    ----
        sc_bdy (numpy.array)      : source data
        logger                    : log of statements

    Returns:
    -------
        data_ind (numpy.array)    : indicies of valid data
        nan_ind (numpy.array)     : indicies where source is land
    """
    # identify valid pts
    data_ind = np.invert(np.isnan(sc_bdy))

    # identify loc where all sc pts are land
    nan_ind = np.sum(data_ind, 2) == 0
    logger.info("NAN IND : %s ", np.sum(nan_ind))

    # Calc max zlevel to which data available on sc grid
    data_ind = np.sum(data_ind == 0, 0) - 1

    # set land val to level 1 otherwise indexing problems
    # may occur- should not affect later results because
    # land is masked in weightings array
    data_ind[data_ind == -1] = 0

    # transform depth levels at each bdy pt to vector
    # index that can be used to speed up calcs
    # data_ind += np.arange(0, sc_z_len * num_bdy_ch, sc_z_len)

    return data_ind, nan_ind


def interp_horizontal(sc_bdy, dist_wei, dist_fac, logger):
    """
    Interpolate the source data to the destination grid using weighted average.

    Args:
    ----
        sc_bdy (numpy.array)      : source data
        dist_wei (numpy.array)    : weightings for interpolation
        dist_fac (numpy.array)    : sum of weightings
        logger                    : log of statements

    Returns:
    -------
        dst_bdy (numpy.array)     : destination bdy points with data from source grid
    """
    logger.info(" sc_bdy %s %s", np.nanmin(sc_bdy), np.nanmax(sc_bdy))
    dst_bdy = np.zeros_like(dist_fac) * np.nan
    ind_valid = dist_fac > 0.0

    dst_bdy[ind_valid] = (
        np.nansum(sc_bdy[:, :, :] * dist_wei, 2)[ind_valid] / dist_fac[ind_valid]
    )
    logger.info(" dst_bdy %s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy))
    # Quick check to see we have not got bad values
    if np.sum(dst_bdy == np.inf) > 0:
        raise RuntimeError("""Bad values found after weighted averaging""")
    return dst_bdy
