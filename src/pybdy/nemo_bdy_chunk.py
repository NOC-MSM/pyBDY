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
$Last commit on:$
"""

# External imports
import numpy as np
import matplotlib.pyplot as plt


def chunk_bdy(bdy):
    """
    Master chunking function.
    Takes the boundary indicies and turns them into a list of boundary chunks.
    The boundary is first split at natural breaks like land or the east-west wrap.
    The chunks are then split near corners.
    The chunks are then optionally split in the middle if they're above a certain size
    after attempting to split at corners.
    
    Args:
    ----
        bdy (Boundary object)   : object with indices of the boundary organised as 
                                  bdy.bdy_i[bdy point, i/j grid]
                                  and rim width number
                                  bdy.bdy_r[bdy_point]

    Returns:
    -------
        numpy.array             : array of chunk numbers
    """
    
    rw = bdy.settings["rimwidth"]
    bdy_size = np.shape(bdy.bdy_i)

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) -1

    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size)
    chunk_number, mid_split = chunk_corner(ibdy, jbdy, chunk_number, rw)
    chunk_number = chunk_mid(ibdy, jbdy, chunk_number, mid_split)

    plt.scatter(ibdy, jbdy, c=chunk_number)
    plt.show()  


def chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size):
    """
    Find natural breaks in the boundary looking for gaps in i and j 
    # TODO: check if it also splits over east-west line
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        ibdy (numpy.array)         : index in i direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth
        bdy_size (tuple)           : dimensions of ibdy


    Returns:
    -------
        numpy.array          : array of chunk numbers
    """
    
    chk = 0
    
    for i in range(bdy_size[0]):
        # Subtract i and j index of point from the rest and test abs value
        i_abs = np.abs(ibdy - ibdy[i])
        j_abs = np.abs(jbdy - jbdy[i])
        closeness_test = (i_abs <= 1) & (j_abs <= 1)
        
        # Check if any of these points already has a chunk number
        chk_true = (chunk_number[closeness_test] != -1)
        if any(chk_true):
            lowest_chk = np.min(chunk_number[closeness_test][chk_true])
            other_chk = np.unique(chunk_number[closeness_test][chk_true])
            chunk_number[closeness_test] = lowest_chk
            for c in range(len(other_chk)):
                chunk_number[chunk_number == other_chk[c]] = lowest_chk
        else:
            lowest_chk = chk * 1
            chk = chk + 1
            chunk_number[closeness_test] = lowest_chk
        
    # Rectify the chunk numbers
    all_chunk = np.unique(chunk_number)
    max_chunk = np.max(chunk_number)
    chunk_number_s = np.zeros_like(chunk_number) -1
    c = 0
    for i in range(len(all_chunk)):
        chunk_number_s[chunk_number == all_chunk[i]] = c
        c = c + 1        
    chunk_number = chunk_number_s * 1

    plt.scatter(ibdy, jbdy, c=chunk_number)
    plt.show()
    
    return chunk_number
    

def chunk_corner(ibdy, jbdy, chunk_number, rw):
    """ 
    Find corners and split beyond the rim width.
    To do this we try spliting near a corner and see if it 
    makes more closely clustered chunks.
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        ibdy (numpy.array)         : index in i direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth

    Returns:
    -------
        numpy.array          : array of chunk numbers
    """
    
    all_chunk = np.unique(chunk_number)
    chk = np.max(all_chunk) + 1
    mid_split = [] # list of chunks to split in the middle

    for i in range(len(all_chunk)):
        i_chk = ibdy[chunk_number == all_chunk[i]]
        j_chk = jbdy[chunk_number == all_chunk[i]]
        i_range1 = np.max(i_chk) - np.min(i_chk)
        j_range1 = np.max(j_chk) - np.min(j_chk)

        # check if we need a corner split
        if (i_range1 > (rw + 10)) & (j_range1 > (rw + 10)):
            
            # work out which corner
            i_split1 = np.min(i_chk) + rw + 1
            i_split2 = np.max(i_chk) - rw - 1

            # check which directional cut makes more closely clustered chunks
            i_range2 = np.max(i_chk[i_chk >= i_split1]) - np.min(i_chk[i_chk >= i_split1])
            i_range3 = np.max(i_chk[i_chk >= i_split2]) - np.min(i_chk[i_chk >= i_split2])
            
            if ((i_range1 - i_range2) > (rw + 10)) & ((i_range1 - i_range3) > (rw + 10)):
                # The boundary is probably diagonal and so we need to split in middle instead
                mid_split.append(all_chunk[i])
            if (i_range1 - i_range2) > (i_range1 - i_range3):
                chunk_number[(chunk_number == all_chunk[i]) & (ibdy >= i_split2)] = chk
            else:
                chunk_number[(chunk_number == all_chunk[i]) & (ibdy >= i_split1)] = chk
            chk = chk + 1
            
    return chunk_number, mid_split
    

def chunk_mid(ibdy, jbdy, chunk_number, mid_split):
    """
    Find midpoint of chunks if splitting at corners didn't make the chunk smaller.
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        ibdy (numpy.array)         : index in i direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        mid_split (list)           : list of chunk numbers that need splitting

    Returns:
    -------
        numpy.array          : array of chunk numbers
    """
    
    if len(mid_split):
        
        # Find average i and j for a chunk and orient a slice
        all_chunk = np.unique(chunk_number)
        chk = np.max(all_chunk) + 1
        
        for c in mid_split:
            i_chk = ibdy[chunk_number == c]
            j_chk = jbdy[chunk_number == c]
            i_split = np.mean(i_chk)
            j_split = np.mean(j_chk)

            # check which directional cut makes more closely clustered chunks
            i_range1 = np.max(i_chk) - np.min(i_chk)
            j_range1 = np.max(j_chk) - np.min(j_chk)
            i_range2 = np.max(i_chk[i_chk >= i_split]) - np.min(i_chk[i_chk >= i_split])
            j_range2 = np.max(j_chk[j_chk >= j_split]) - np.min(j_chk[j_chk >= j_split])
            if (i_range1 - i_range2) > (j_range1 - j_range2):
                chunk_number[(chunk_number == c) & (ibdy >= i_split)] = chk
            else:
                chunk_number[(chunk_number == c) & (jbdy >= j_split)] = chk
            chk = chk + 1 
    
    return chunk_number
