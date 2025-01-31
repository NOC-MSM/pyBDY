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
from pybdy import nemo_bdy_extr_assist as extr_assist


def baro_vel_correction(vel_sc, vel_dst, e3t_sc, e3t_dst, dist_wei, dist_fac, logger):
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
    # Integrate velocity vertically
    vel_sc = np.ma.masked_where(np.isnan(vel_sc), vel_sc)
    vel_dst = np.ma.masked_where(np.isnan(vel_dst), vel_dst)
    e3t_sc = np.ma.masked_where(np.isnan(e3t_sc), e3t_sc)
    e3t_dst = np.ma.masked_where(np.isnan(e3t_dst), e3t_dst)

    vel_baro_sc = integrate_vel_dz(vel_sc, e3t_sc)[np.newaxis, :, :].filled(np.nan)
    vel_baro_dst = integrate_vel_dz(vel_dst, e3t_dst).filled(np.nan)

    # Interp on to dst
    vel_baro_on_bdy = extr_assist.interp_sc_to_dst(
        vel_baro_sc, dist_wei[:1, :, :], dist_fac[:1, :], logger
    )

    baro_term = np.tile((vel_baro_on_bdy / vel_baro_dst), (vel_dst.shape[0], 1))

    # Put some reasonable safeguards on for very large or small baro_term multiplier.
    # Double the velocity seems enough.
    too_big = 2
    too_small = -2
    baro_term[baro_term > too_big] = too_big
    baro_term[baro_term < too_small] = too_small

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
    barotropic = np.ma.sum(vel_z, axis=dz_axis)
    return barotropic
