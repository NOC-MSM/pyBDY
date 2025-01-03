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

@author James Harle
@author Benjamin Barton
"""

# External imports
import pytest
import random
import numpy as np
import matplotlib.pyplot as plt

# Local imports
from src.pybdy import nemo_bdy_chunk as chunk
from src.pybdy import nemo_bdy_gen_c as gen_grid
from src.pybdy import nemo_bdy_setup as setup

    
def test_chunk_land_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0])).all()
    
    
def test_chunk_land_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0, 1, 2])).all()
    
    
def test_chunk_land_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0])).all()
    
    
def test_chunk_land_comp():
    bdy = gen_synth_bdy(4)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0])).all() 

    
def test_chunk_land_wrap():
    bdy = gen_synth_bdy(5)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    assert (np.unique(chunk_number) == np.array([0, 1])).all() 
    
    
def test_chunk_corner_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number, mid_split = chunk.chunk_corner(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw)
    print(np.unique(chunk_number))
    plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    plt.show()
    
    errors = []
    if not (np.unique(chunk_number) == np.array([0, 1, 2, 4])).all():
        errors.append("The chunk numbers are not correct.")
    if len(mid_split) > 0:
        errors.append("The middle split chunk is not correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

    
def test_chunk_corner_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number, mid_split = chunk.chunk_corner(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw)
    print(np.unique(chunk_number))
    plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    plt.show()
    errors = []
    if not (np.unique(chunk_number) == np.array([0, 1, 2, 3])).all():
        errors.append("The chunk numbers are not correct.")
    if len(mid_split) > 0:
        errors.append("The middle split chunk is not correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
    
    
def test_chunk_corner_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number, mid_split = chunk.chunk_corner(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw)
    print(np.unique(chunk_number), mid_split)
    plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    plt.show()
    errors = []
    if not (np.unique(chunk_number) == np.array([0])).all():
        errors.append("The chunk numbers are not correct.")
    if mid_split != 0:
        errors.append("The middle split chunk is not correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
    
    
def test_chunk_corner_comp():
    bdy = gen_synth_bdy(4)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number, mid_split = chunk.chunk_corner(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw)
    print(np.unique(chunk_number), mid_split)
    plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    plt.show()
    errors = []
    if not (np.unique(chunk_number) == np.array([0, 1])).all():
        errors.append("The chunk numbers are not correct.")
    if mid_split != 0:
        errors.append("The middle split chunk is not correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))    
    
    
def test_chunk_corner_wrap():
    bdy = gen_synth_bdy(5)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    chunk_number, mid_split = chunk.chunk_corner(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], bdy.bdy_r, chunk_number, rw)
    print(np.unique(chunk_number), mid_split)
    plt.scatter(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], c=chunk_number)
    plt.show()
    errors = []
    if not (np.unique(chunk_number) == np.array([0, 1, 2, 3])).all():
        errors.append("The chunk numbers are not correct.")
    if len(mid_split) > 0:
        errors.append("The middle split chunk is not correct.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
    
    
def test_chunk_mid_4():
    bdy = gen_synth_bdy(1)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    mid_split = []
    chunk_number = chunk.chunk_mid(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, mid_split)
    assert (np.unique(chunk_number) == np.array([0])).all()
    
    
def test_chunk_mid_3():
    bdy = gen_synth_bdy(2)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    mid_split = [0, 1, 2]
    chunk_number = chunk.chunk_mid(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, mid_split)
    assert (np.unique(chunk_number) == np.array([0, 1, 2, 3, 4, 5])).all()

    
def test_chunk_mid_diag():
    bdy = gen_synth_bdy(3)
    rw = bdy.settings["rimwidth"]
    chunk_number = np.zeros_like(bdy.bdy_r) -1
    
    chunk_number = chunk.chunk_land(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, rw)
    mid_split = [0]
    chunk_number = chunk.chunk_mid(bdy.bdy_i[:, 0], bdy.bdy_i[:, 1], chunk_number, mid_split)
    assert (np.unique(chunk_number) == np.array([0, 1])).all()
    
    
#def test_chunk_bdy():
    
    
# Synthetic test cases

def gen_synth_bdy(map=1):
    """
    Generate synthetic boundaries as test cases, a 2D array based 
    on the selected map type.

    Args:
        map (int): Map type (1, 2, 3, 4 or 5).

    Returns:
        numpy.ndarray: Generated 2D array.
    """

    lon_range = np.arange(-10, 10, 0.2)
    lat_range = np.arange(30, 50, 0.2)
    
    setup_filepath = './namelist_synthetic.bdy'
    Setup = setup.Setup(setup_filepath) 
    settings = Setup.settings
    
    if map == 1:
        # 4 open boundaries around an island
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) -1 # out of domain
        bdy_msk[10:90, 10:90] = 1 # water
        bdy_msk[40:60, 40:60] = 0 # land
    
    elif map == 2:
        # 3 open boundaries split by land in the corner and side
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1 # water
        bdy_msk[90:, :] = 0 # land
        bdy_msk[:10, :10] = 0 # land
        bdy_msk[:10, 50:60] = 0 # land
        
    elif map == 3:
        # a single diagonal boundary
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1 # water
        bdy_msk[90:, :] = 0 # land
        bdy_msk[:, 90:] = 0 # land
        for i in range(bdy_msk.shape[0]):
            bdy_msk[:100 - i, :i] = -1 # out of domain
            
    elif map == 4:
        # a complex diagonal boundaries
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) + 1 # water
        bdy_msk[90:, :] = 0 # land
        bdy_msk[:, 90:] = 0 # land
        bdy_msk[:10, :] = -1 # out of domain
        #bdy_msk[:, :10] = -1 # out of domain
        bdy_msk[:20, 80:] = -1 # out of domain
        for i in range(60):
            bdy_msk[:61 - i, :i] = -1 # out of domain
        for i in range(31):
            bdy_msk[i + 40:, :i] = -1 # out of domain
        
    elif map == 5:
        # a domain that crosses east-west around the southern ocean
        lon_range = np.arange(-180, 180, 3.6)
        lat_range = np.arange(-55, -75, -0.2)
    
        bdy_msk = np.zeros((len(lat_range), len(lon_range))) -1 # out of domain
        bdy_msk[:10, :] = 0 # land
        bdy_msk[10:50, :30] = 1 # water
        bdy_msk[10:50, -30:] = 1 # water
        
    else:
        raise ValueError("Invalid map type. Choose 1, 2, 3, 4 or 5.")
        
    bdy_ind = gen_grid.Boundary(bdy_msk, settings, "t")
    return bdy_ind
    

