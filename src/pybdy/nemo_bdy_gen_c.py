"""
NEMO Boundary module.

Creates indices for t, u and v points, plus rim gradient.
The variable names have been renamed to keep consistent with python standards and generalizing
the variable names eg. bdy_i is used instead of bdy_t

Ported from Matlab code by James Harle
@author: John Kazimierz Farey
@author: Srikanth Nagella.
"""
# External Imports
import logging

import numpy as np


class Boundary:
    """Class for boundary definitions."""

    def __init__(self, boundary_mask, settings, grid):
        """
        Generate the indices for NEMO Boundary and returns a Grid object with indices.

        Parameters
        ----------
        boundary_mask : boundary mask
        settings      : dictionary of setting values
        grid          : type of the grid 't', 'u', 'v'

        Returns
        -------
        Boundary (object) : where bdy_i is index and bdy_r is the r index
        """
        # Bearings for overlays
        self._NORTH = [1, -1, 1, -1, 2, None, 1, -1]
        self._SOUTH = [1, -1, 1, -1, None, -2, 1, -1]
        self._EAST = [1, -1, 1, -1, 1, -1, 2, None]
        self._WEST = [1, -1, 1, -1, 1, -1, None, -2]

        self.logger = logging.getLogger(__name__)
        bdy_msk = boundary_mask
        self.settings = settings
        rw = self.settings["rimwidth"]
        rm = rw - 1
        self.grid_type = grid.lower()
        # Throw an error for wrong grid input type
        if grid not in ["t", "u", "v", "f"]:
            self.logger.error("Grid Type not correctly specified:" + grid)
            raise ValueError(
                """%s is invalid grid grid_type;
                                must be 't', 'u', 'v' or 'f'"""
                % grid
            )

        # Configure grid grid_type
        if grid != "t":
            # We need to copy this before changing, because the original will be
            # needed in calculating later grid boundary types
            bdy_msk = boundary_mask.copy()
            grid_ind = np.zeros(bdy_msk.shape, dtype=bool, order="C")
            # NEMO works with a staggered 'C' grid. need to create a grid with staggered points
            for fval in [-1, 0]:  # -1 mask value, 0 Land, 1 Water/Ocean
                if grid == "u":
                    grid_ind[:, :-1] = np.logical_and(
                        bdy_msk[:, :-1] == 1, bdy_msk[:, 1:] == fval
                    )
                    bdy_msk[grid_ind] = fval
                elif grid == "v":
                    grid_ind[:-1, :] = np.logical_and(
                        bdy_msk[:-1, :] == 1, bdy_msk[1:, :] == fval
                    )
                    bdy_msk[grid_ind] = fval
                elif grid == "f":
                    grid_ind[:-1, :-1] = np.logical_and(
                        bdy_msk[:-1, :-1] == 1, bdy_msk[1:, 1:] == fval
                    )
                    grid_ind[:-1, :] = np.logical_or(
                        np.logical_and(bdy_msk[:-1, :] == 1, bdy_msk[1:, :] == fval),
                        grid_ind[:-1, :] == 1,
                    )

                    grid_ind[:, :-1] = np.logical_or(
                        np.logical_and(bdy_msk[:, :-1] == 1, bdy_msk[:, 1:] == fval),
                        grid_ind[:, :-1] == 1,
                    )
                    bdy_msk[grid_ind] = fval

        # Create padded array for overlays
        msk = np.pad(bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))
        # create index arrays of I and J coords
        igrid, jgrid = np.meshgrid(
            np.arange(bdy_msk.shape[1]), np.arange(bdy_msk.shape[0])
        )

        SBi, SBj = self.find_bdy(igrid, jgrid, msk, self._SOUTH)
        NBi, NBj = self.find_bdy(igrid, jgrid, msk, self._NORTH)
        EBi, EBj = self.find_bdy(igrid, jgrid, msk, self._EAST)
        WBi, WBj = self.find_bdy(igrid, jgrid, msk, self._WEST)

        # create a 2D array index for the points that are on border
        tij = np.column_stack(
            (np.concatenate((SBi, NBi, WBi, EBi)), np.concatenate((SBj, NBj, WBj, EBj)))
        )
        bdy_i = np.tile(tij, (rw, 1, 1))

        bdy_i = np.transpose(bdy_i, (1, 2, 0))
        bdy_r = bdy_r = np.tile(np.arange(0, rw), (bdy_i.shape[0], 1))

        # Add points for relaxation zone over rim width
        # In the relaxation zone with rim width. looking into the domain up to the rim width
        # and select the points. S head North (0,+1) N head South(0,-1) W head East (+1,0)
        # E head West (-1,0)
        temp = np.column_stack(
            (
                np.concatenate((SBi * 0, NBi * 0, WBi * 0 + 1, EBi * 0 - 1)),
                np.concatenate((SBj * 0 + 1, NBj * 0 - 1, WBj * 0, EBj * 0)),
            )
        )
        for i in range(rm):
            bdy_i[:, :, i + 1] = bdy_i[:, :, i] + temp

        bdy_i = np.transpose(bdy_i, (1, 2, 0))
        bdy_i = np.reshape(bdy_i, (bdy_i.shape[0], bdy_i.shape[1] * bdy_i.shape[2]))
        bdy_r = bdy_r.flatten("F")

        ##   Remove duplicate and open sea points  ##

        bdy_i, bdy_r = self.remove_duplicate_points(bdy_i, bdy_r)
        bdy_i, bdy_r, nonmask_index = self.remove_landpoints_open_ocean(
            bdy_msk, bdy_i, bdy_r
        )

        ###   Fill in any gradients between relaxation zone and internal domain
        ###   bdy_msk matches matlabs incarnation, r_msk is pythonic
        r_msk = bdy_msk.copy()
        r_msk[r_msk == 1] = rw
        r_msk = np.float16(r_msk)
        r_msk[r_msk < 1] = np.NaN
        r_msk[bdy_i[:, 1], bdy_i[:, 0]] = np.float16(bdy_r)

        r_msk_orig = r_msk.copy()
        r_msk_ref = r_msk[1:-1, 1:-1]

        self.logger.debug("Start r_msk bearings loop")
        # Removes the shape gradients by smoothing it out
        for i in range(rw - 1):
            # Check each bearing
            for b in [self._SOUTH, self._NORTH, self._WEST, self._EAST]:
                r_msk, r_msk_ref = self.fill(r_msk, r_msk_ref, b)
        self.logger.debug("done loop")

        # update bdy_i and bdy_r
        new_ind = np.abs(r_msk - r_msk_orig) > 0
        # The transposing gets around the Fortran v C ordering thing.
        bdy_i_tmp = np.array([igrid.T[new_ind.T], jgrid.T[new_ind.T]])
        bdy_r_tmp = r_msk.T[new_ind.T]
        bdy_i = np.vstack((bdy_i_tmp.T, bdy_i))

        uniqind = self.unique_rows(bdy_i)
        bdy_i = bdy_i[uniqind, :]
        bdy_r = np.hstack((bdy_r_tmp, bdy_r))
        bdy_r = bdy_r[uniqind]

        # sort by rimwidth
        igrid = np.argsort(bdy_r, kind="mergesort")
        bdy_r = bdy_r[igrid]
        bdy_i = bdy_i[igrid, :]

        self.bdy_i = bdy_i
        self.bdy_r = bdy_r

        self.logger.debug("Final bdy_i: %s", self.bdy_i.shape)

    def remove_duplicate_points(self, bdy_i, bdy_r):
        """
        Remove the duplicate points in the bdy_i and return the bdy_i and bdy_r.

        Parameters
        ----------
        bdy_i : bdy indexes
        bdy_r : bdy rim values.

        Returns
        -------
        bdy_i : bdy indexes
        bdy_r : bdy rim values.
        """
        bdy_i2 = np.transpose(bdy_i, (1, 0))
        uniqind = self.unique_rows(bdy_i2)

        bdy_i = bdy_i2[uniqind]
        bdy_r = bdy_r[uniqind]
        return bdy_i, bdy_r

    def remove_landpoints_open_ocean(self, mask, bdy_i, bdy_r):
        """Remove the land points and open ocean points."""
        unmask_index = mask[bdy_i[:, 1], bdy_i[:, 0]] == 1
        bdy_i = bdy_i[unmask_index, :]
        bdy_r = bdy_r[unmask_index]
        return bdy_i, bdy_r, unmask_index

    def find_bdy(self, igrid, jgrid, mask, brg):
        """
        Find the border indexes by checking the change from ocean to land.

        Notes
        -----
        Returns the i and j index array where the shift happens.

        Parameters
        ----------
        igrid : I x direction indexes
        jgrid : J y direction indexes
        mask  : mask data
        brg   : mask index range

        Returns
        -------
        bdy_i : bdy indexes
        bdy_r : bdy rim values.
        """
        # subtract matrices to find boundaries, set to True
        m1 = mask[brg[0] : brg[1], brg[2] : brg[3]]
        m2 = mask[brg[4] : brg[5], brg[6] : brg[7]]
        overlay = np.subtract(m1, m2)
        # Create boolean array of bdy points in overlay
        bool_arr = overlay == 2
        # index I or J to find bdies
        bdy_I = igrid[bool_arr]
        bdy_J = jgrid[bool_arr]

        return bdy_I, bdy_J

    def fill(self, mask, ref, brg):
        tmp = mask[brg[4] : brg[5], brg[6] : brg[7]]
        ind = (ref - tmp) > 1
        ref[ind] = tmp[ind] + 1
        mask[brg[0] : brg[1], brg[2] : brg[3]] = ref

        return mask, ref

    def unique_rows(self, t):
        """
        Find indexes of unique rows in the input 2D array.

        Parameters
        ----------
        t : input 2D array.

        Returns
        -------
        indx : indexes of unique rows
        """
        sh = np.shape(t)
        if (len(sh) > 2) or (sh[0] == 0) or (sh[1] == 0):
            print("Warning: Shape of expected 2D array:", sh)
        tlist = t.tolist()
        sortt = []
        indx = list(zip(*sorted([(val, i) for i, val in enumerate(tlist)])))[1]
        indx = np.array(indx)
        for i in indx:
            sortt.append(tlist[i])
        del tlist
        for i, x in enumerate(sortt):
            if x == sortt[i - 1]:
                indx[i] = -1
        # all the rows are identical, set the first as the unique row
        if sortt[0] == sortt[-1]:
            indx[0] = 0

        return indx[indx != -1]
