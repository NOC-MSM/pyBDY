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
Created on Thu Dec 22 16:33:00 2024.

@author James Harle
@author Benjamin Barton
"""

# External imports
import numpy as np

# Internal imports


def calc_vel_correction(vel_sc, vel_dst, e3t_sc, e3t_dst, dist_wei, dist_fac, logger):
    """
    Calculate the scale factor correction term needed to correct velocity.

    The correction term is calculated as the barotropic stream function
    on the source grid. This is then interpolated to the destination
    grid. The stream function is then differentiated on the
    child grid to get the barotropic velocity. The same is done on the child
    grid and the difference is calculated to give the correction term.

    Args:
    ----
        vel_sc (numpy.array)      : velocity u or v
        vel_dst (numpy.array)     : grid cell size in i direction
        e3t_sc (numpy.array)      : source grid cell size in z direction
        e3t_dst (numpy.array)     : destination grid cell size in z direction
        dist_wei (numpy.array)    : weightings for interpolation
        dist_fac (numpy.array)    : sum of weightings
        logger                    : log of statements

    Returns:
    -------
        vel_out (numpy.array)   : velocity u and v corrected
    """
    # integrate velocity vertically
    vel_baro_sc = integrate_vel_dz(vel_sc, e3t_sc)[np.newaxis, :, :]
    vel_baro_dst = integrate_vel_dz(vel_dst, e3t_dst)

    # interp on to dst
    vel_baro_on_bdy = interp_sc_to_dst(
        vel_baro_sc, dist_wei[:1, :, :], dist_fac[:1, :], logger
    )
    baro_term = vel_baro_on_bdy / vel_baro_dst
    vel_out = vel_dst * baro_term
    return vel_out


def integrate_vel_dz(vel, e3t, dz_axis=0):
    """
    Integrate the velocity vertically to give barotropic velocity.

    Args:
    ----
        vel (numpy.array) : velocity u or v
        e3t (numpy.array) : grid cell size in z direction
        dz_axis (int)     : axis to integrate over

    Returns:
    -------
        barotropic (numpy.array)  : barotropic velocity u or v
    """
    # Check vel and e3t sizes match
    if vel.shape != e3t.shape:
        raise Exception("Shape of velcocity field does not match e3t.")
    vel_z = vel * e3t
    barotropic = np.sum(vel_z, axis=dz_axis)
    return barotropic


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
    # TODO move this to assist and use in extr

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
