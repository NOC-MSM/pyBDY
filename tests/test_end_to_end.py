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
Created on Thu Feb 13 18:03:00 2025.

@author James Harle
@author Benjamin Barton
"""

# External imports
import os

import numpy as np

# Internal imports
from tests import synth_bathymetry, synth_zgrid


def test_all():
    path1 = generate_test_case1()
    path2 = generate_test_case2()
    os.remove(path1)
    os.remove(path2)

    assert False


def generate_test_case1():
    # Generate a synthetic test case
    path1 = "./tests/synth_test_full.nc"

    lon_t = np.arange(-20, 1, 1)
    lat_t = np.arange(40, 53, 0.5)
    ppe1 = np.zeros((len(lon_t))) + 1
    ppe2 = np.zeros((len(lat_t))) + 0.5
    synth = synth_bathymetry.Bathymetry(ppe1, ppe2, ppglam0=lon_t[0], ppgphi0=lat_t[0])
    synth = synth.sea_mount(depth=1000, stiff=1000)

    n_zlevel = 20
    gdept, gdepw = synth_zgrid.synth_sco(synth["Bathymetry"], n_zlevel)

    synth.to_netcdf(path1)
    return path1


def generate_test_case2():
    # Generate a synthetic test case
    path2 = "./tests/synth_test_sub.nc"

    lon_t = np.arange(-20, 1, 1)
    lat_t = np.arange(40, 53, 0.5)
    ppe1 = np.zeros((len(lon_t))) + 1
    ppe2 = np.zeros((len(lat_t))) + 0.5
    synth = synth_bathymetry.Bathymetry(ppe1, ppe2, ppglam0=lon_t[0], ppgphi0=lat_t[0])
    synth = synth.sea_mount(depth=1000, stiff=1000)

    synth.to_netcdf(path2)
    return path2
