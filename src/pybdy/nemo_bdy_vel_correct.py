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


def calc_vel_correction(vel_in, e1t, e2t, e3t):
    """
    Calculate the correction term needed to correct velocity.

    The correction term is calculated as the  barotropic stream function
    on the parent (source) grid. This is then interpolated to the child
    (destination) grid. The stream function is then differentiated on the
    child grid to get the barotropic velocity. The same is done on the child
    grid and the difference is calculated to give the correction term.

    Args:
    ----
        vel_in (numpy.array)    : velocity u and v
        e1t (numpy.array)       : grid cell size in i direction
        e2t (numpy.array)       : grid cell size in j direction
        e3t (numpy.array)       : grid cell size in z direction

    Returns:
    -------
        baro_term (numpy.array) : array of correction terms
    """
    baro_term = np.array([1])
    return baro_term


def apply_vel_correction(baro_term, vel_in):
    """
    Apply the velocity correction to the child (destintion) velocities.

    Args:
    ----
        vel_in (numpy.array)    : velocity u and v
        baro_term (numpy.array) : array of correction terms

    Returns:
    -------
        vel_out (numpy.array)   : velocity u and v corrected
    """
    vel_out = vel_in * baro_term
    return vel_out
