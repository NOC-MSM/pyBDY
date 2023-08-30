"""
NEMO Boundary module.

Creates indices for t, u and v points, plus rim gradient.
The variable names have been renamed to keep consistent with python standards and generalizing
the variable names eg. bdy_i is used instead of bdy_t

Ported from Matlab code by James Harle.
@author: John Kazimierz Farey
@author: Srikanth Nagella.

Refactoring by Joao Morado and Ryan Patmore.
"""
import logging
from typing import List, Optional, Tuple, Union

import numpy as np


class Boundary:
    # Bearings for overlays
    _NORTH = [1, -1, 1, -1, 2, None, 1, -1]
    _SOUTH = [1, -1, 1, -1, None, -2, 1, -1]
    _EAST = [1, -1, 1, -1, 1, -1, 2, None]
    _WEST = [1, -1, 1, -1, 1, -1, None, -2]
    _SUPPORTED_GRIDS = ["t", "u", "v", "f"]

    def __init__(
        self,
        boundary_mask: np.ndarray,
        settings: dict,
        grid: str,
        create_boundary: bool = True,
    ) -> None:
        """
        Generate the indices for NEMO Boundary and return a Grid object with indices.

        Parameters
        ----------
        boundary_mask
            Mask for the boundary.
        settings
            Dictionary of setting values.
        grid
            Type of the grid 't', 'u', 'v' or 'f'.
        create_boundary
            Whether to create the boundary upon initialisation.
        """
        self.logger = logging.getLogger(__name__)

        # We need to copy this before changing, because the original will be
        # needed in calculating later grid boundary types
        self.bdy_msk = boundary_mask.copy()
        self.settings = settings

        # Grid variables
        if grid not in self._SUPPORTED_GRIDS:
            error_msg = (
                "Grid type {} is not supported. Supported grid types are: {}".format(
                    grid, self._SUPPORTED_GRIDS
                )
            )
            raise ValueError(error_msg)

        self.grid = grid
        self.grid_type = grid.lower()

        # Rim variables
        self.rw = self.settings["rimwidth"]
        self.rm = self.rw - 1

        if create_boundary:
            self.create_boundary()

    def create_boundary(self):
        """Create the boundary."""
        # Create boundary mask
        self._create_boundary_mask()

        # Calculate boundary indexes
        self._calculate_boundary_indexes()

    def _create_boundary_mask(self) -> np.ndarray:
        """
        Create the boundary mask based on u, v and f points.

        Returns
        -------
        self.bdy_msk
            New boundary mask for the respective grid.
        """
        if self.grid_type != "t":
            # Mask for the grid
            grid_ind = np.zeros(self.bdy_msk.shape, dtype=bool, order="C")

            # NEMO works with a staggered C-grid
            # We need to create a grid with staggered points

            # -1: mask value
            #  0: land
            #  1: water/ocean
            for fval in [-1, 0]:
                if self.grid_type == "u":
                    # Current point is 1 (water) and its neighboring point is either -1 or 0
                    grid_ind[:, :-1] = np.logical_and(
                        self.bdy_msk[:, :-1] == 1, self.bdy_msk[:, 1:] == fval
                    )
                    self.bdy_msk[grid_ind] = fval
                elif self.grid_type == "v":
                    grid_ind[:-1, :] = np.logical_and(
                        self.bdy_msk[:-1, :] == 1, self.bdy_msk[1:, :] == fval
                    )
                    self.bdy_msk[grid_ind] = fval
                elif self.grid_type == "f":
                    grid_ind[:-1, :-1] = np.logical_and(
                        self.bdy_msk[:-1, :-1] == 1, self.bdy_msk[1:, 1:] == fval
                    )
                    grid_ind[:-1, :] = np.logical_or(
                        np.logical_and(
                            self.bdy_msk[:-1, :] == 1, self.bdy_msk[1:, :] == fval
                        ),
                        grid_ind[:-1, :] == 1,
                    )

                    grid_ind[:, :-1] = np.logical_or(
                        np.logical_and(
                            self.bdy_msk[:, :-1] == 1, self.bdy_msk[:, 1:] == fval
                        ),
                        grid_ind[:, :-1] == 1,
                    )
                    self.bdy_msk[grid_ind] = fval

        return self.bdy_msk

    def _calculate_boundary_indexes(self) -> None:
        """Create and process boundary indexes."""
        # Get i,j positions of boundary mask along each boundary
        igrid, jgrid = self.__create_i_j_indexes()

        # Create boundary indexes
        SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj = self.__create_boundary_indexes(
            igrid, jgrid
        )

        # Process rim width
        bdy_i, bdy_r = self.__formalise_boundaries(
            SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj
        )

        # Remove duplicate points
        bdy_i, bdy_r = self.__remove_duplicate_points(bdy_i, bdy_r)

        # Remove land points and open ocean points
        bdy_i, bdy_r, _ = self.__remove_landpoints_open_ocean(
            self.bdy_msk, bdy_i, bdy_r
        )
        # Process the boundary indexes
        r_msk, r_msk_orig = self.__smooth_interior_relaxation_gradients(bdy_i, bdy_r)
        bdy_i, bdy_r = self.__assign_smoothed_boundary_index(
            bdy_i, bdy_r, r_msk, r_msk_orig, igrid, jgrid
        )
        bdy_i, bdy_r = self.__sort_by_rimwidth(bdy_i, bdy_r)

        # Assign the boundary indexes to the corresponding instance variables
        self.bdy_i = bdy_i
        self.bdy_r = bdy_r

    def __create_i_j_indexes(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Assign i, j positions of boundary mask along each boundary.

        Returns
        -------
        igrid, jgrid
            Index arrays of i and j coordinates.
        """
        # Create index arrays of i and j coordinates
        igrid, jgrid = np.meshgrid(
            np.arange(self.bdy_msk.shape[1]), np.arange(self.bdy_msk.shape[0])
        )
        return igrid, jgrid

    def __create_boundary_indexes(
        self, igrid: np.ndarray, jgrid: np.ndarray
    ) -> Tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        """
        Get the boundary indexes.

        Parameters
        ----------
        igrid
            Index array of i coordinates.
        jgrid
            Index array of j coordinates.

        Returns
        -------
        SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj
            Boundary indexes along each direction. Index arrays of i and j coordinates.
        """
        # Create padded array for overlays
        msk = np.pad(self.bdy_msk, ((1, 1), (1, 1)), "constant", constant_values=(-1))

        # Find boundary indexes
        SBi, SBj = self.__find_bdy(igrid, jgrid, msk, self._SOUTH)
        NBi, NBj = self.__find_bdy(igrid, jgrid, msk, self._NORTH)
        EBi, EBj = self.__find_bdy(igrid, jgrid, msk, self._EAST)
        WBi, WBj = self.__find_bdy(igrid, jgrid, msk, self._WEST)

        return SBi, SBj, NBi, NBj, EBi, EBj, WBi, WBj

    def __formalise_boundaries(
        self,
        SBi: np.ndarray,
        SBj: np.ndarray,
        NBi: np.ndarray,
        NBj: np.ndarray,
        EBi: np.ndarray,
        EBj: np.ndarray,
        WBi: np.ndarray,
        WBj: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Merge boundary indexes into a continuous array for all boundaries.

        Parameters
        ----------
        SBi
            i position of south boundary.
        SBj
            j position of south boundary.
        NBi
            i position of north boundary.
        NBj
            j position of north boundary.
        EBi
            i position of east boundary.
        EBj
            j position of east boundary.
        WBi
            i position of west boundary.
        WBj
            j position of west boundary.

        Returns
        -------
        bdy_i, bdy_r
            Boundary indexes and rim values.
        """
        # Create a 2D array index for the points that are on the border
        tij = np.column_stack(
            (np.concatenate((SBi, NBi, WBi, EBi)), np.concatenate((SBj, NBj, WBj, EBj)))
        )

        bdy_i = np.tile(tij, (self.rw, 1, 1))
        bdy_i = np.transpose(bdy_i, (1, 2, 0))
        bdy_r = bdy_r = np.tile(np.arange(0, self.rw), (bdy_i.shape[0], 1))

        # Add points for relaxation zone over rim width
        # S head North (0,+1)
        # N head South(0,-1)
        # W head East (+1,0)
        # E head West (-1,0)
        temp = np.column_stack(
            (
                np.concatenate((SBi * 0, NBi * 0, WBi * 0 + 1, EBi * 0 - 1)),
                np.concatenate((SBj * 0 + 1, NBj * 0 - 1, WBj * 0, EBj * 0)),
            )
        )
        for i in range(self.rm):
            bdy_i[:, :, i + 1] = bdy_i[:, :, i] + temp

        bdy_i = np.transpose(bdy_i, (1, 2, 0))
        bdy_i = np.reshape(bdy_i, (bdy_i.shape[0], bdy_i.shape[1] * bdy_i.shape[2]))
        bdy_r = bdy_r.flatten("F")

        return bdy_i, bdy_r

    def __find_bdy(
        self, igrid: np.ndarray, jgrid: np.ndarray, mask: np.ndarray, brg: list
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find the border indexes by checking the change from ocean to land.

        Parameters
        ----------
        igrid
            I, x direction indexes.
        jgrid
            J, y direction indexes.
        mask
            Padded boundary mask.
        brg
            Mask index range.

        Returns
        -------
        bdy_I, bdy_J
            Border indexes.

        Notes
        -----
        Returns the i and j index array where the shift happens.
        """
        # Subtract matrices to find boundaries, set to True
        m1 = mask[brg[0] : brg[1], brg[2] : brg[3]]
        m2 = mask[brg[4] : brg[5], brg[6] : brg[7]]
        overlay = np.subtract(m1, m2)

        # Create boolean array of bdy points in overlay
        bool_arr = overlay == 2

        # index I or J to find bdies
        bdy_I = igrid[bool_arr]
        bdy_J = jgrid[bool_arr]

        return bdy_I, bdy_J

    def __smooth_interior_relaxation_gradients(
        self, bdy_i: np.ndarray, bdy_r: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fill in any gradients between relaxation zone and internal domain.

        Parameters
        ----------
        bdy_i
            Boundary indexes.
        bdy_r
            Rim values.

        Returns
        -------
        r_msk, r_msk_orig
            Boundary rim mask and original rim mask.

        Notes
        -----
        bdy_msk matches matlabs incarnation, r_msk is pythonic
        """
        r_msk = self.bdy_msk.copy()
        r_msk[r_msk == 1] = self.rw
        r_msk = r_msk.astype(np.float16)
        r_msk[r_msk < 1] = np.NaN
        r_msk[bdy_i[:, 1], bdy_i[:, 0]] = np.float16(bdy_r)

        r_msk_orig = r_msk.copy()
        r_msk_ref = r_msk[1:-1, 1:-1]

        # Removes the shape gradients by smoothing it out
        for _ in range(self.rw - 1):
            # Check each bearing
            for b in [self._SOUTH, self._NORTH, self._WEST, self._EAST]:
                r_msk, _ = self.__fill(r_msk, r_msk_ref, b)

        return r_msk, r_msk_orig

    def __assign_smoothed_boundary_index(
        self,
        bdy_i: np.ndarray,
        bdy_r: np.ndarray,
        r_msk: np.ndarray,
        r_msk_orig: np.ndarray,
        igrid: np.ndarray,
        jgrid: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update boundary arrays with smoothed fields.

        Parameters
        ----------
        bdy_i
            Boundary indexes.
        bdy_r
            Rim values.
        r_msk
            Boundary rim mask.
        r_msk_orig
            Original rim mask.
        igrid
            I, x direction indexes.
        jgrid
            J, y direction indexes.

        Returns
        -------
        bdy_i, bdy_r
            Updated boundary indexes and rim values.
        """
        # update bdy_i and bdy_r
        new_ind = np.abs(r_msk - r_msk_orig) > 0
        # The transposing gets around the Fortran v C ordering thing.
        bdy_i_tmp = np.array([igrid.T[new_ind.T], jgrid.T[new_ind.T]])
        bdy_r_tmp = r_msk.T[new_ind.T]
        bdy_i = np.vstack((bdy_i_tmp.T, bdy_i))

        uniqind = self.__unique_rows(bdy_i)
        bdy_i = bdy_i[uniqind, :]
        bdy_r = np.hstack((bdy_r_tmp, bdy_r))
        bdy_r = bdy_r[uniqind]

        return bdy_i, bdy_r

    def __sort_by_rimwidth(
        self, bdy_i: np.ndarray, bdy_r: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sort boundary index by rimwidth.

        Parameters
        ----------
        bdy_i
            Boundary indexes.
        bdy_r
            Rim values.
        """
        igrid = np.argsort(bdy_r, kind="mergesort")
        bdy_r = bdy_r[igrid]
        bdy_i = bdy_i[igrid, :]

        return bdy_i, bdy_r

    def __remove_duplicate_points(
        self, bdy_i: np.ndarray, bdy_r: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Remove the duplicate points in the bdy_i and return the bdy_i and bdy_r.

        Parameters
        ----------
        bdy_i
            Boundary indexes.
        bdy_r
            Boundary rim values.

        Returns
        -------
        bdy_i, bdy_r
            Boundary indexes (transposed) and rim values without duplicate points.
        """
        bdy_i2 = np.transpose(bdy_i, (1, 0))
        uniqind = self.__unique_rows(bdy_i2)

        bdy_i = bdy_i2[uniqind]
        bdy_r = bdy_r[uniqind]

        return bdy_i, bdy_r

    def __remove_landpoints_open_ocean(
        self, mask: np.ndarray, bdy_i: np.ndarray, bdy_r: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Remove the land points and open ocean points.

        Parameters
        ----------
        mask
            Padded boundary mask.
        bdy_i
            Boundary indexes.
        bdy_r
            Boundary rim values.

        Returns
        -------
        bdy_i, bdy_r, unmask_index
            Boundary indexes and rim values with land and open ocean points removed.
            Indexes of the removed points in the original mask.
        """
        unmask_index = mask[bdy_i[:, 1], bdy_i[:, 0]] != 0
        bdy_i = bdy_i[unmask_index, :]
        bdy_r = bdy_r[unmask_index]

        return bdy_i, bdy_r, unmask_index

    def __fill(
        self,
        mask: np.ndarray,
        ref: np.ndarray,
        brg: Union[np.ndarray, List[Optional[int]]],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fill in the border indexes by checking the change from ocean to land.

        Parameters
        ----------
        mask
            Padded boundary mask.
        ref
            Reference mask.
        brg
            Mask index range.

        Returns
        -------
        mask, ref
            Filled added boundary mask and reference mask.
        """
        tmp = mask[brg[4] : brg[5], brg[6] : brg[7]]
        ind = (ref - tmp) > 1
        ref[ind] = tmp[ind] + 1
        mask[brg[0] : brg[1], brg[2] : brg[3]] = ref

        return mask, ref

    def __unique_rows(self, t: np.ndarray) -> np.ndarray:
        """
        Return indexes of unique rows in the input 2D array.

        Parameters
        ----------
        t
            Input 2D array

        Returns
        -------
        indx
            Indexes of unique rows in the input 2D array.
        """
        if t.ndim != 2 or 0 in t.shape:
            self.logger.warning("Shape of expected 2D array: {}".format(t.shape))

        tlist = t.tolist()
        sortt = []
        indx = list(zip(*sorted([(val, i) for i, val in enumerate(tlist)])))[1]
        indx = np.array(indx)

        for i in indx:
            sortt.append(tlist[i])

        del tlist

        # At this point, sortt has the unique rows in the first indexes
        for i, x in enumerate(sortt[1:], start=1):
            if x == sortt[i - 1]:
                indx[i] = -1

        return indx[indx != -1]
