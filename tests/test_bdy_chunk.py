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
Created on Thu Dec 19 10:39:46 2024.

The main application script for the NRCT.

@author James Harle
@author John Kazimierz Farey
@author Srikanth Nagella
@author Benjamin Barton
"""

# External imports
import pytest
import random

# Local imports
from pybdy import nemo_bdy_chunk as chunk
from pybdy import nemo_bdy_gen_c as gen_grid

    
def test_chunk_land_4():
    bdy = gen_synth_4_open()
    rw = bdy.settings["rimwidth"]
    bdy_size = np.shape(bdy.bdy_i)

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size)
    assert np.unique(chunk_number) == np.array([0])
    
    
def test_chunk_land_3():
    bdy = gen_synth_3_parts()
    rw = bdy.settings["rimwidth"]
    bdy_size = np.shape(bdy.bdy_i)

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size)
    assert np.unique(chunk_number) == np.array([0, 1, 2])
    
    
def test_chunk_land_diag():
    bdy = gen_synth_diagonal()
    rw = bdy.settings["rimwidth"]
    bdy_size = np.shape(bdy.bdy_i)

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size)
    assert np.unique(chunk_number) == np.array([0])    
    

def test_chunk_east_west():
    bdy = gen_synth_east_west()
    rw = bdy.settings["rimwidth"]
    bdy_size = np.shape(bdy.bdy_i)

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size)
    assert np.unique(chunk_number) == np.array([0])
    
    
def test_chunk_corner():


def test_chunk_mid():
    
    
def test_chunk_bdy():
    
    
# Synthetic test cases

def gen_synth_4_open():
    # Generate synthetic boundaries as test cases
    setup_filepath = './namelist_synthetic.bdy'
    Setup = setup.Setup(setup_filepath) 
    settings = Setup.settings
    
    bdy_msk = np.zeros((100, 100)) -1 # out of domain
    bdy_msk[10:90, 10:90] = 1 # water
    bdy_msk[40:60, 40:60] = 0 # land
    
    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind
    
def gen_synth_3_parts():
    # Generate synthetic boundaries as test cases
    setup_filepath = './namelist_synthetic.bdy'
    Setup = setup.Setup(setup_filepath) 
    settings = Setup.settings
    
    bdy_msk = np.zeros((100, 100)) + 1 # water
    bdy_msk[90:, :] = 0 # land
    bdy_msk[:10, :10] = 0 # land
    bdy_msk[:10, 90:] = 0 # land
    
    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind

def gen_synth_diagonal():
    # Generate synthetic boundaries as test cases
    setup_filepath = './namelist_synthetic.bdy'
    Setup = setup.Setup(setup_filepath) 
    settings = Setup.settings
    
    bdy_msk = np.zeros((100, 100)) + 1 # water
    bdy_msk[90:, :] = 0 # land
    bdy_msk[:, 90:] = 0 # land
    for i in range(bdy_msk.shape[0]):
        bdy_msk[:100 - i, :i] = -1 # out of domain
    
    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind

def gen_synth_east_west():
    # Generate synthetic boundaries as test cases
    setup_filepath = './namelist_synthetic.bdy'
    Setup = setup.Setup(setup_filepath) 
    settings = Setup.settings
    
    bdy_msk = np.zeros((100, 100)) # land
    bdy_msk[10:90, 10:90] = 0 # water
    bdy_msk[10:90, :20] = -1 # out of domain
    
    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind
