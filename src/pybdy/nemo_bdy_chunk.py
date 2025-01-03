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
        logger                  : log error and messages

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
    chunk_number, mid_split = chunk_corner(ibdy, jbdy, bdy.bdy_r, chunk_number, rw)
    chunk_number = chunk_mid(ibdy, jbdy, chunk_number, mid_split)

    plt.scatter(ibdy, jbdy, c=chunk_number)
    plt.show()  


def chunk_land(ibdy, jbdy, chunk_number, rw, bdy_size):
    """
    Find natural breaks in the boundary looking for gaps in i and j 
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
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
        
        # Sanity check if the point is alone
        if np.sum(closeness_test) == 1:
            raise Exception('One of the boundary chunks has only one grid point.')
        
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

    #plt.scatter(ibdy, jbdy, c=chunk_number)
    #plt.show()
    
    return chunk_number
    
def chunk_corner_old(ibdy, jbdy, chunk_number, rw, mid_split=[]):
    """ 
    Find corners and split beyond the rim width.
    To do this we try spliting near a corner and see if it 
    makes more closely clustered chunks.
    Do this recusively.
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth
        change (bool)              : on the last iteration was there a change in the number of chunks
        mid_split (list)           : list of chunk numbers that need splitting

    Returns:
    -------
        numpy.array          : array of chunk numbers
    """

    change = False
    all_chunk = np.unique(chunk_number)
    chk = np.max(all_chunk) + 1

    for i in range(len(all_chunk)):
        i_chk = ibdy[chunk_number == all_chunk[i]]
        j_chk = jbdy[chunk_number == all_chunk[i]]
        i_range1 = np.max(i_chk) - np.min(i_chk)
        j_range1 = np.max(j_chk) - np.min(j_chk)

        # check if we need a corner split
        if (i_range1 > (rw + 10)) & (j_range1 > (rw + 10)):

            # work out which corner
            i_split1 = np.min(i_chk) + rw
            i_split2 = np.max(i_chk) - rw
            j_split1 = np.min(j_chk) + rw
            j_split2 = np.max(j_chk) - rw
            
            # check which directional cut makes more closely clustered chunks
            i_range2 = np.max(i_chk[j_chk >= j_split1]) - np.min(i_chk[j_chk >= j_split1])
            i_range3 = np.max(i_chk[j_chk >= j_split2]) - np.min(i_chk[j_chk >= j_split2])
            j_range2 = np.max(j_chk[i_chk >= i_split1]) - np.min(j_chk[i_chk >= i_split1])
            j_range3 = np.max(j_chk[i_chk >= i_split2]) - np.min(j_chk[i_chk >= i_split2])

            if (((i_range1 - i_range2) > (rw + 10)) & ((i_range1 - i_range3) > (rw + 10))
                & ((j_range1 - j_range2) > (rw + 10)) & ((j_range1 - j_range3) > (rw + 10))):
                # The boundary is probably diagonal and so we need to split in middle instead
                mid_split.append(all_chunk[i])
                continue
                
            if (j_range1 - j_range2) > (j_range1 - j_range3):
                chunk_number[(chunk_number == all_chunk[i]) & (ibdy >= i_split2)] = chk
                change = True
            elif (j_range1 - j_range2) < (j_range1 - j_range3):
                chunk_number[(chunk_number == all_chunk[i]) & (ibdy >= i_split1)] = chk
                change = True
            elif (i_range1 - i_range2) >= (i_range1 - i_range3):
                chunk_number[(chunk_number == all_chunk[i]) & (jbdy >= j_split2)] = chk
                change = True
            else:
                chunk_number[(chunk_number == all_chunk[i]) & (jbdy >= j_split1)] = chk
                change = True
            chk = chk + 1
            
    if change:
        # Recusion to look for more corners
        chunk_number, mid_split = chunk_corner(ibdy, jbdy, chunk_number, rw, mid_split)
    return chunk_number, mid_split


def chunk_corner(ibdy, jbdy, rbdy, chunk_number, rw, mid_split=[]):
    """ 
    Find corners and split along the change in direction.
    To do this we look for a change in direction along each rim.
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
        rbdy (numpy.array)         : rim index
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth
        mid_split (list)           : list of chunk numbers that need splitting

    Returns:
    -------
        numpy.array          : array of chunk numbers
    """

    change = False
    all_chunk = np.unique(chunk_number)
    chk = np.max(all_chunk) + 1
    corner = np.zeros_like(ibdy)

    line_shape = np.zeros((3, 3))
    diag_shape = np.zeros_like(line_shape)
    en_l_shape = np.zeros_like(line_shape)
    en_d_shape = np.zeros_like(line_shape)
    long_shape = np.zeros_like(line_shape)
    shrt_shape = np.zeros_like(line_shape)
    line_shape[:, 1] = 1
    diag_shape[[0, 1, 2], [0, 1, 2]] = 1
    en_l_shape[:2, 1] = 1
    en_d_shape[[0, 1], [0, 1]] = 1
    long_shape[:, 1] = 1
    long_shape[0, 0] = 1
    shrt_shape[:1, 1] = 1
    shrt_shape[0, 0] = 1
    
    for i in range(len(all_chunk)):
        i_chk = ibdy[chunk_number == all_chunk[i]]
        j_chk = jbdy[chunk_number == all_chunk[i]]
        i_range1 = np.max(i_chk) - np.min(i_chk)
        j_range1 = np.max(j_chk) - np.min(j_chk)

        # check if we need a corner split
        if (i_range1 > (rw + 10)) & (j_range1 > (rw + 10)):

            # work out which corner by taking each rim and looking for a
            # non-straight section
            for r in range(rw):
                ir_chk = ibdy[(rbdy == r) & (chunk_number == all_chunk[i])]
                jr_chk = jbdy[(rbdy == r) & (chunk_number == all_chunk[i])]
                
                for p in range(len(ir_chk)):
                    i_p = ir_chk - ir_chk[p]
                    j_p = jr_chk - jr_chk[p]
                    
                    closeness_test = (np.abs(i_p) <= 1) & (np.abs(j_p) <= 1)
                    i_p = i_p[closeness_test] + 1
                    j_p = j_p[closeness_test] + 1
                    shape = np.zeros((3, 3))
                    shape[i_p, j_p] = 1
                    
                    # check for straight line or deadend
                    if ((shape == line_shape).all() | (shape == line_shape.T).all() # straight
                            | (shape == en_l_shape).all() | (shape == en_l_shape[::-1, :]).all() # straight end
                            | (shape == en_l_shape.T).all() | (shape == en_l_shape.T[:, ::-1]).all()
                            | (shape == diag_shape).all() | (shape == diag_shape[::-1, :]).all() # diagonal
                            | (shape == en_d_shape).all() | (shape == en_d_shape[::-1, :]).all() # diagonal end
                            | (shape == en_d_shape[:, ::-1]).all() | (shape == en_d_shape.T[::-1, ::-1]).all()
                            | (shape == long_shape).all() | (shape == long_shape[:, ::-1]).all() # L shape
                            | (shape == long_shape[::-1, :]).all() | (shape == long_shape[::-1, ::-1]).all()
                            | (shape == long_shape.T).all() | (shape == long_shape.T[:, ::-1]).all()
                            | (shape == long_shape.T[::-1, :]).all() | (shape == long_shape.T[::-1, ::-1]).all()
                            | (shape == shrt_shape).all() | (shape == shrt_shape[:, ::-1]).all() # square shape
                            | (shape == shrt_shape[::-1, :]).all() | (shape == shrt_shape[::-1, ::-1]).all()
                            | (shape == shrt_shape.T).all() | (shape == shrt_shape.T[:, ::-1]).all()
                            | (shape == shrt_shape.T[::-1, :]).all() | (shape == shrt_shape.T[::-1, ::-1]).all()
                       ):
                        continue
                    else:
                        # found corner
                        corner_index = np.nonzero((rbdy == r) & (chunk_number == all_chunk[i]))[0][p]
                        print(corner_index)
                        corner[corner_index] = 1
                        # remove corner points then do something similar to chunk_land 
                        # then add them to the highest neighbouring chunk number
    plt.scatter(ibdy, jbdy, c=corner)
    plt.show()
    
    return chunk_number, mid_split

    
def chunk_mid(ibdy, jbdy, chunk_number, mid_split):
    """
    Find midpoint of chunks if splitting at corners didn't make the chunk smaller.
    
    Args:
    ----
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
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
