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


def valid_index(sc_bdy, num_bdy_ch, sc_z_len, logger):
    """
    Find an array of valid indicies.

    Args:
    ----
        sc_bdy (numpy.array)      : source data
        num_bdy_ch (int)          : number of bdy points in the chunk
        sc_z_len (int)            : the number of depth levels
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
    data_ind = np.sum(nan_ind == 0, 0) - 1

    # set land val to level 1 otherwise indexing problems
    # may occur- should not affect later results because
    # land is masked in weightings array
    data_ind[data_ind == -1] = 0

    # transform depth levels at each bdy pt to vector
    # index that can be used to speed up calcs
    data_ind += np.arange(0, sc_z_len * num_bdy_ch, sc_z_len)

    return data_ind, nan_ind


def interp_sc_to_dst(sc_bdy, dist_wei, dist_fac, logger):
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
