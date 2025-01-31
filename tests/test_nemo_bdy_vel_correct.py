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
import logging

import numpy as np

# Internal imports
from src.pybdy import nemo_bdy_vel_correct as vel_correct


def test_integrate_vel_dz():
    # Test the vertical integration function
    vel = np.zeros((10)) + 0.1
    e3t = np.zeros((10)) + 1
    baro1 = vel_correct.integrate_vel_dz(vel, e3t, 0)

    vel = np.zeros((10, 5)) + 0.2
    e3t = np.tile(np.arange(0, 1, 0.1) + 1, (5, 1)).T
    baro2 = vel_correct.integrate_vel_dz(vel, e3t, 0)

    errors = []
    if baro1 != 1:
        errors.append("Does not integrate 1d correct.")
    elif not (baro2 == np.zeros((5)) + 2.9).all():
        errors.append("Does not integrate 2d correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_baro_vel_correction():
    # Test the barotropic velocity correction function
    logger = logging.getLogger(__name__)
    r0 = 0.041666666
    vel_sc = np.zeros((10, 5, 9)) + 0.1
    e3t_sc = np.tile(np.arange(0, 1, 0.1) + 1, (9, 5, 1)).T
    vel_dst = np.zeros((12, 5)) + 0.1
    e3t_dst = np.tile(np.arange(0, 1.2, 0.1) + 1, (5, 1)).T

    dist_tot = np.tile(np.linspace(0.05, 0.35, num=9), (1, 5, 1))
    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
        np.exp(-0.5 * np.power(dist_tot / r0, 2))
    )
    dist_fac = np.sum(dist_wei, 2)
    new_vel1 = vel_correct.baro_vel_correction(
        vel_sc, vel_dst, e3t_sc, e3t_dst, dist_wei, dist_fac, logger
    )

    # Test the safeguard on large scaling in shallow areas is working
    vel_dst = np.zeros((3, 5)) + 0.1
    e3t_dst = np.tile(np.arange(0, 0.3, 0.1) + 1, (5, 1)).T
    new_vel2 = vel_correct.baro_vel_correction(
        vel_sc, vel_dst, e3t_sc, e3t_dst, dist_wei, dist_fac, logger
    )

    errors = []
    if not np.isclose(new_vel1, np.zeros((12, 5)) + 0.077957, atol=1e-4).all():
        errors.append("Velocity correction is not correct.")
    elif not (new_vel2 == (np.zeros((3, 5)) + 0.2)).all():
        errors.append("Does not interp 2d correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
