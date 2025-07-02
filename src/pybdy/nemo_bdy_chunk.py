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
import warnings

import numpy as np


def chunk_bdy(bdy):
    """
    Master chunking function.

    Takes the boundary indicies and turns them into a list of boundary chunks.
    The boundary is first split at natural breaks like land or the east-west wrap.
    The chunks are then split near corners.
    The chunks are then optionally split in the middle if they're above a certain size
    after attempting to split at corners.

    Parameters
    ----------
        bdy (obj)   : organised as bdy_i[point, i/j grid] and rim width bdy_r[point]
        logger                  : log error and messages

    Returns
    -------
        chunk_number (numpy.array) : array of chunk numbers
    """
    rw = bdy.settings["rimwidth"]

    ibdy = bdy.bdy_i[:, 0]
    jbdy = bdy.bdy_i[:, 1]
    chunk_number = np.zeros_like(bdy.bdy_r) - 1

    chunk_number = chunk_land(ibdy, jbdy, chunk_number, rw)
    chunk_number = chunk_corner(ibdy, jbdy, bdy.bdy_r, chunk_number, rw)
    chunk_number = chunk_large(ibdy, jbdy, chunk_number)

    # import matplotlib.pyplot as plt
    # plt.scatter(ibdy, jbdy, c=chunk_number)
    # plt.show()
    return chunk_number


def chunk_land(ibdy, jbdy, chunk_number, rw):
    """
    Find natural breaks in the boundary looking for gaps in i and j.

    Parameters
    ----------
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth

    Returns
    -------
        chunk_number (numpy.array) : array of chunk numbers
    """
    if np.min(chunk_number) <= -1:
        chk = 0
    else:
        chk = np.min(chunk_number)

    for i in range(np.shape(ibdy)[0]):
        # Subtract i and j index of point from the rest and test abs value
        i_abs = np.abs(ibdy - ibdy[i])
        j_abs = np.abs(jbdy - jbdy[i])
        closeness_test = (i_abs <= 1) & (j_abs <= 1)

        # Sanity check if the point is alone
        if np.sum(closeness_test) == 1:
            warnings.warn("One of the boundary chunks has only one grid point.")

        # Check if any of these points already has a chunk number
        chk_true = chunk_number[closeness_test] != -1
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
    np.max(chunk_number)
    chunk_number_s = np.zeros_like(chunk_number) - 1
    c = 0
    for i in range(len(all_chunk)):
        chunk_number_s[chunk_number == all_chunk[i]] = c
        c = c + 1
    chunk_number = chunk_number_s * 1

    # plt.scatter(ibdy, jbdy, c=chunk_number)
    # plt.show()

    return chunk_number


def chunk_corner(ibdy, jbdy, rbdy, chunk_number, rw):
    """
    Find corners and split along the change in direction.

    To do this we look for a change in direction along each rim.

    Parameters
    ----------
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
        rbdy (numpy.array)         : rim index
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number
        rw (int)                   : rimwidth

    Returns
    -------
        chunk_number (numpy.array) : array of chunk numbers
    """
    all_chunk = np.unique(chunk_number)
    all_chunk_st = all_chunk * 1
    np.max(all_chunk) + 1
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
                    if (
                        (shape == line_shape).all()
                        | (shape == line_shape.T).all()  # straight
                        | (shape == en_l_shape).all()
                        | (shape == en_l_shape[::-1, :]).all()  # straight end
                        | (shape == en_l_shape.T).all()
                        | (shape == en_l_shape.T[:, ::-1]).all()
                        | (shape == diag_shape).all()
                        | (shape == diag_shape[::-1, :]).all()  # diagonal
                        | (shape == en_d_shape).all()
                        | (shape == en_d_shape[::-1, :]).all()  # diagonal end
                        | (shape == en_d_shape[:, ::-1]).all()
                        | (shape == en_d_shape.T[::-1, ::-1]).all()
                        | (shape == long_shape).all()
                        | (shape == long_shape[:, ::-1]).all()  # L shape
                        | (shape == long_shape[::-1, :]).all()
                        | (shape == long_shape[::-1, ::-1]).all()
                        | (shape == long_shape.T).all()
                        | (shape == long_shape.T[:, ::-1]).all()
                        | (shape == long_shape.T[::-1, :]).all()
                        | (shape == long_shape.T[::-1, ::-1]).all()
                        | (shape == shrt_shape).all()
                        | (shape == shrt_shape[:, ::-1]).all()  # square shape
                        | (shape == shrt_shape[::-1, :]).all()
                        | (shape == shrt_shape[::-1, ::-1]).all()
                        | (shape == shrt_shape.T).all()
                        | (shape == shrt_shape.T[:, ::-1]).all()
                        | (shape == shrt_shape.T[::-1, :]).all()
                        | (shape == shrt_shape.T[::-1, ::-1]).all()
                    ):
                        continue
                    else:
                        # found corner
                        corner_index = np.nonzero(
                            (rbdy == r) & (chunk_number == all_chunk[i])
                        )[0][p]
                        corner[corner_index] = 1

                        # make corners 2 points wider
                        corner_index = np.nonzero(
                            ((ir_chk[p] + 1) == ibdy) & (jr_chk[p] == jbdy)
                        )[0]
                        corner[corner_index] = 1
                        corner_index = np.nonzero(
                            (ir_chk[p] == ibdy) & ((jr_chk[p] + 1) == jbdy)
                        )[0]
                        corner[corner_index] = 1
                        corner_index = np.nonzero(
                            ((ir_chk[p] - 1) == ibdy) & (jr_chk[p] == jbdy)
                        )[0]
                        corner[corner_index] = 1
                        corner_index = np.nonzero(
                            (ir_chk[p] == ibdy) & ((jr_chk[p] - 1) == jbdy)
                        )[0]
                        corner[corner_index] = 1

    # plt.scatter(ibdy, jbdy, c=corner)
    # plt.show()

    # Reset chunk number
    chunk_number[:] = -1

    # remove corner points then do something similar to chunk_land()
    chunk_number[corner == 0] = chunk_land(
        ibdy[corner == 0], jbdy[corner == 0], chunk_number[corner == 0], rw
    )

    if np.sum(corner == 1) > 0:
        max_chunk = np.max(chunk_number) + 1
        chunk_number[corner == 1] = (
            chunk_land(
                ibdy[corner == 1], jbdy[corner == 1], chunk_number[corner == 1], rw
            )
            + max_chunk
        )

    # add corner points to the highest neighbouring chunk number
    corner_chunk = np.unique(chunk_number[corner == 1])
    np.max(chunk_number) + 1

    for c in range(len(corner_chunk)):
        icorn = ibdy[chunk_number == corner_chunk[c]]
        jcorn = jbdy[chunk_number == corner_chunk[c]]
        if len(icorn) <= (rw * 4):
            b_check = np.zeros(ibdy.shape, dtype=bool)
            for p in range(len(icorn)):
                for i in range(1, rw + 1):
                    i_abs = np.abs(ibdy - icorn[p])
                    j_abs = np.abs(jbdy - jcorn[p])
                    b_check = (i_abs <= i) & (j_abs <= i)

                    b_check[corner == 1] = False
                    if (b_check == 1).any():
                        break
            if (b_check == 1).any():
                new_chunk = np.min(chunk_number[b_check])
                chunk_number[chunk_number == corner_chunk[c]] = new_chunk

    # Need to add chunks that are too small together
    all_chunk = np.unique(chunk_number)
    chunk_size = [np.sum(chunk_number == all_chunk[i]) for i in range(len(all_chunk))]
    all_chunk = [x for _, x in sorted(zip(chunk_size, all_chunk))]
    chunk_size = np.array(sorted(chunk_size))

    for i in range(len(all_chunk)):
        if chunk_size[i] <= (rw**2):
            icorn = ibdy[chunk_number == all_chunk[i]]
            jcorn = jbdy[chunk_number == all_chunk[i]]

            b_check = np.zeros(ibdy.shape, dtype=bool)
            for p in range(len(icorn)):
                i_abs = np.abs(ibdy - icorn[p])
                j_abs = np.abs(jbdy - jcorn[p])
                b_check = (i_abs <= 1) & (j_abs <= 1)

            b_check[chunk_number == all_chunk[i]] = False
            if b_check.any():
                new_chunk = np.min(chunk_number[b_check])
                chunk_number[chunk_number == all_chunk[i]] = new_chunk

                chunk_size[i] = np.sum(chunk_number == all_chunk[i])
                chunk_size[all_chunk == new_chunk] = np.sum(chunk_number == new_chunk)

    all_chunk = np.unique(chunk_number)
    chunk_size = [np.sum(chunk_number == all_chunk[i]) for i in range(len(all_chunk))]
    all_chunk = [x for _, x in sorted(zip(chunk_size, all_chunk))]
    chunk_size = np.array(sorted(chunk_size))

    # Add small newly created chunks together if we have more than 10 corner chunks
    if len(all_chunk) > len(all_chunk_st) + 10:
        last_chunk = all_chunk[len(all_chunk_st) + 10]
        chunk_number[chunk_number > last_chunk] = last_chunk

    # Rectify the chunk numbers
    all_chunk = np.unique(chunk_number)
    max_chunk = np.max(chunk_number)
    chunk_number_s = np.zeros_like(chunk_number) - 1
    c = 0
    for i in range(len(all_chunk)):
        chunk_number_s[chunk_number == all_chunk[i]] = c
        c = c + 1
    chunk_number = chunk_number_s * 1

    return chunk_number


def chunk_large(ibdy, jbdy, chunk_number):
    """
    Split boundaries that have too much white space and are too large.

    Parameters
    ----------
        ibdy (numpy.array)         : index in i direction
        jbdy (numpy.array)         : index in j direction
        chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number

    Returns
    -------
        chunk_number (numpy.array) : array of chunk numbers
    """
    thresh_ratio = 1 / 3  # 1:3
    thresh_large = 2000

    # Calculate ratio of bdy points to white space

    all_chunk = np.unique(chunk_number)
    ratio_box = np.zeros((len(all_chunk)))

    for i in range(len(all_chunk)):
        i_chk = ibdy[chunk_number == all_chunk[i]]
        j_chk = jbdy[chunk_number == all_chunk[i]]
        i_range = (np.max(i_chk) - np.min(i_chk)) + 1
        j_range = (np.max(j_chk) - np.min(j_chk)) + 1
        ratio_box[i] = np.sum(chunk_number == all_chunk[i]) / (i_range * j_range)

    # Calculate which boundaries are too big

    chunk_size = np.array(
        [np.sum(chunk_number == all_chunk[i]) for i in range(len(all_chunk))]
    )
    large_split = all_chunk[(chunk_size / thresh_large) > 1]
    n_part = np.ceil(chunk_size / thresh_large).astype(int)
    n_part = n_part[n_part > 1]

    if len(large_split):
        # Find average i and j for a chunk and orient a slice
        chk = np.max(all_chunk) + 1

        for c in range(len(large_split)):
            if ratio_box[all_chunk == large_split[c]] < thresh_ratio:
                i_chk = ibdy[chunk_number == large_split[c]]
                j_chk = jbdy[chunk_number == large_split[c]]
                chunk_to_split = large_split[c]
                for p in range(n_part[c] - 1):
                    i_split = np.percentile(i_chk, ((100 / n_part[c]) * (p + 1)))
                    j_split = np.percentile(j_chk, ((100 / n_part[c]) * (p + 1)))

                    # check which directional cut makes more closely clustered chunks
                    i_range1 = np.max(i_chk) - np.min(i_chk)
                    j_range1 = np.max(j_chk) - np.min(j_chk)
                    i_range2 = np.max(i_chk[i_chk >= i_split]) - np.min(
                        i_chk[i_chk >= i_split]
                    )
                    j_range2 = np.max(j_chk[j_chk >= j_split]) - np.min(
                        j_chk[j_chk >= j_split]
                    )
                    if (i_range1 - i_range2) > (j_range1 - j_range2):
                        chunk_number[
                            (chunk_number == chunk_to_split) & (ibdy >= i_split)
                        ] = chk
                    else:
                        chunk_number[
                            (chunk_number == chunk_to_split) & (jbdy >= j_split)
                        ] = chk
                    if np.sum(chunk_number == chunk_to_split) < np.sum(
                        chunk_number == chk
                    ):
                        chunk_to_split = chk
                    chk = chk + 1

    return chunk_number
