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
Created on Wed Sep 12 08:02:46 2012.

This Module defines the extraction of the data from the source grid and does
the interpolation onto the destination grid.

@author James Harle
@author John Kazimierz Farey
@author: Mr. Srikanth Nagella
$Last commit on:$
"""
# External Imports
import copy
import logging
from calendar import isleap, monthrange

import numpy as np
import scipy.spatial as sp
from cftime import datetime, utime
from scipy.interpolate import interp1d

from pybdy import nemo_bdy_extr_assist as extr_assist
from pybdy import nemo_bdy_ncgen as ncgen
from pybdy import nemo_bdy_ncpop as ncpop
from pybdy.reader.factory import GetFile
from pybdy.utils.nemo_bdy_lib import rot_rep, sub2ind

# Local Imports
from . import nemo_bdy_grid_angle as ga


# TODO: Convert the 'F' ordering to 'C' to improve efficiency
class Extract:
    def __init__(self, setup, SourceCoord, DstCoord, Grid, var_nam, grd, pair):
        """
        Initialise the Extract object.

        Notes
        -----
        Parent grid to child grid weights are defined along with rotation
        weightings for vector quantities.

        Parameters
        ----------
        setup           (list) : settings for bdy
        SourceCoord     (obj)  : source grid information
        DstCoord        (obj)  : destination grid information
        Grid            (dict) : containing grid type 't', 'u', 'v'
                                    and source time
        var_name        (list) : netcdf file variable names (str)
        years           (list) : years to extract (default [1979])
        months          (list) : months to extract (default [11])

        Returns
        -------
            None
        """
        self.logger = logging.getLogger(__name__)
        self.g_type = grd
        self.settings = setup
        self.key_vec = False

        # TODO: Why are we deepcopying the coordinates???

        SC = copy.deepcopy(SourceCoord)
        DC = copy.deepcopy(DstCoord)
        bdy_r = copy.deepcopy(Grid[grd].bdy_r)

        # Extract time and variable information

        sc_time = Grid[grd].source_time
        self.var_nam = var_nam
        sc_z = SC.zt[:]
        sc_z_len = len(sc_z)

        self.jpj, self.jpi = DC.lonlat[grd]["lon"].shape
        self.jpk = DC.depths[grd]["bdy_z"].shape[0]
        self.bdy_dz = DC.depths[grd]["bdy_dz"]
        if grd == "t":
            self.bdy_msk = DC.bdy_msk
        # Set some constants

        # Make function of dst grid resolution (used in 1-2-1 weighting)
        # if the weighting can only find one addtional point this implies an
        # point so fill the third point with itself as not to bias too much

        fr = 0.1

        # Set up any rotation that is required

        if pair == "uv":
            if grd == "u":
                self.rot_dir = "i"
                self.key_vec = True
                self.fnames_2 = Grid["v"].source_time
            elif grd == "v":
                self.rot_dir = "j"
                self.key_vec = True
                self.fnames_2 = Grid["v"].source_time
            else:
                raise ValueError("Invalid rotation grid grid_type: %s" % grd)

        #

        dst_lon = DC.bdy_lonlat[self.g_type]["lon"]
        dst_lat = DC.bdy_lonlat[self.g_type]["lat"]
        try:
            dst_dep = DC.depths[self.g_type]["bdy_z"]
            dst_dep = np.ma.masked_where(np.isnan(dst_dep), dst_dep)
        except KeyError:
            dst_dep = np.ma.zeros([1])

        isslab = len(dst_dep) == 1
        if dst_dep.size == len(dst_dep):
            dst_dep = np.ma.ones([1, len(dst_lon)])

        # ??? Should this be read from settings?
        wei_121 = np.array([0.5, 0.25, 0.25])

        SC.lon = SC.lon.squeeze()
        SC.lat = SC.lat.squeeze()

        # Check that we're only dealing with one pair of vectors

        self.nvar = len(self.var_nam)

        if self.key_vec:
            self.nvar = (
                self.nvar // 2
            )  # TODO: if  self.nvar=3 then this will pass and should not!
            if self.nvar != 1:
                self.logger.error(
                    "Code not written yet to handle more than\
                                   one pair of rotated vectors"
                )

        self.logger.info("Extract __init__: variables to process")
        self.logger.info("nvar: %s", self.nvar)
        self.logger.info("key vec: %s", self.key_vec)

        # Find subset of source data for each chunk individually
        # to reduce source data required

        # set up holding arrays

        num_bdy = len(dst_lon)
        dst_len_z = len(dst_dep[:, 0])
        chunk_number = Grid[grd].chunk_number
        all_chunk = np.unique(chunk_number)

        sc_ind_ch = []
        self.dst_chunk = chunk_number.copy()
        self.dist_tot = np.zeros((len(dst_lon), 9))
        self.num_bdy_ch = np.zeros((len(all_chunk)), dtype=int)
        self.tmp_filt_2d = np.zeros((1, len(dst_lon), len(wei_121)))
        self.tmp_filt_3d = np.zeros((sc_z_len, len(dst_lon), len(wei_121)))
        self.id_121_2d = np.zeros((1, len(dst_lon), len(wei_121)), dtype=int)
        self.id_121_3d = np.zeros((sc_z_len, len(dst_lon), len(wei_121)), dtype=int)
        if self.key_vec:
            self.dst_gcos = np.zeros((sc_z_len, len(dst_lon)))
            self.dst_gsin = np.zeros((sc_z_len, len(dst_lon)))
            self.gcos = np.empty((0, 9))
            self.gsin = np.empty((0, 9))
            self.sc_chunk = np.empty((0), int)
        self.z_ind = np.zeros((num_bdy * dst_len_z, 2), dtype=np.int64)
        self.z_dist = np.ma.zeros((num_bdy * dst_len_z, 2))
        self.z_chunk = np.zeros((num_bdy * dst_len_z), dtype=np.int64) - 1
        zc_count = 0

        # loop over chunks

        for c in range(len(all_chunk)):
            chunk = chunk_number == all_chunk[c]
            dst_lon_ch = dst_lon[chunk]
            dst_lat_ch = dst_lat[chunk]
            self.num_bdy_ch[c] = len(dst_lon_ch)
            self.z_chunk[
                zc_count : zc_count + (self.num_bdy_ch[c] * dst_len_z)
            ] = all_chunk[c]
            zc_count = zc_count + (self.num_bdy_ch[c] * dst_len_z)
            chunk_z_bool = self.z_chunk == all_chunk[c]

            imin, imax, jmin, jmax = extr_assist.get_ind(
                dst_lon_ch, dst_lat_ch, SC.lon, SC.lat
            )
            # Summarise subset region

            self.logger.info("Extract __init__: subset region limits")
            self.logger.info(
                " \n imin: %d\n imax: %d\n jmin: %d\n jmax: %d\n",
                imin,
                imax,
                jmin,
                jmax,
            )

            # Reduce the source coordinates to the sub region identified

            SC.lon_ch = SC.lon[jmin:jmax, imin:imax]
            SC.lat_ch = SC.lat[jmin:jmax, imin:imax]

            # Initialise gsin* and gcos* for rotation of vectors

            if self.key_vec:
                bdy_ind = Grid[grd].bdy_i[chunk, :]

                maxI = DC.lonlat["t"]["lon"].shape[1]
                maxJ = DC.lonlat["t"]["lon"].shape[0]
                dst_gcos = np.ones([maxJ, maxI])
                dst_gsin = np.zeros([maxJ, maxI])

                # TODO: allow B-Grid Extraction

                # Extract the source rotation angles on the T-Points as the C-Grid
                # U/V points naturally average onto these

                src_ga = ga.GridAngle(
                    self.settings["src_hgr"], imin, imax, jmin, jmax, "t"
                )

                # Extract the rotation angles for the bdy velocities points

                dst_ga = ga.GridAngle(self.settings["dst_hgr"], 1, maxI, 1, maxJ, grd)

                sc_gcos = src_ga.cosval
                sc_gsin = src_ga.sinval
                dst_gcos[1:, 1:] = dst_ga.cosval
                dst_gsin[1:, 1:] = dst_ga.sinval

                # Retain only boundary points rotation information

                tmp_gcos = np.zeros((1, bdy_ind.shape[0]))
                tmp_gsin = np.zeros((1, bdy_ind.shape[0]))

                # TODO: can this be converted to an ind op rather than a loop?

                for p in range(bdy_ind.shape[0]):
                    tmp_gcos[:, p] = dst_gcos[bdy_ind[p, 1], bdy_ind[p, 0]]
                    tmp_gsin[:, p] = dst_gsin[bdy_ind[p, 1], bdy_ind[p, 0]]

                self.dst_gcos[:, chunk] = np.tile(tmp_gcos, (sc_z_len, 1))
                self.dst_gsin[:, chunk] = np.tile(tmp_gsin, (sc_z_len, 1))

            # Determine size of source data subset

            source_dims = SC.lon_ch.shape

            # Find nearest neighbour on the source grid to each dst bdy point
            # Ann Query substitute
            source_tree = None
            try:
                source_tree = sp.cKDTree(
                    list(zip(SC.lon_ch.ravel(order="F"), SC.lat_ch.ravel(order="F"))),
                    balanced_tree=False,
                    compact_nodes=False,
                )
            except TypeError:  # added this fix to make it compatible with scipy 0.16.0
                source_tree = sp.cKDTree(
                    list(zip(SC.lon_ch.ravel(order="F"), SC.lat_ch.ravel(order="F")))
                )
            dst_pts = list(
                zip(dst_lon_ch.ravel(order="F"), dst_lat_ch.ravel(order="F"))
            )
            nn_dist, nn_id = source_tree.query(dst_pts, k=1)

            # Find surrounding points
            j_sp, i_sp = np.unravel_index(nn_id, source_dims, order="F")
            j_sp = np.vstack((j_sp, j_sp + 1, j_sp - 1))
            j_sp = np.vstack((j_sp, j_sp, j_sp))
            i_sp = np.vstack((i_sp, i_sp, i_sp))
            i_sp = np.vstack((i_sp, i_sp + 1, i_sp - 1))

            # Index out of bounds error check not implemented

            # Determine 9 nearest neighbours based on distance
            ind = sub2ind(source_dims, i_sp, j_sp)
            ind_rv = np.ravel(ind, order="F")
            sc_lon_rv = np.ravel(SC.lon_ch, order="F")
            sc_lat_rv = np.ravel(SC.lat_ch, order="F")
            sc_lon_ind = sc_lon_rv[ind_rv]

            diff_lon = sc_lon_ind - np.repeat(dst_lon_ch, 9).T
            diff_lon = diff_lon.reshape(ind.shape, order="F")
            out = np.abs(diff_lon) > 180
            diff_lon[out] = -np.sign(diff_lon[out]) * (360 - np.abs(diff_lon[out]))

            dst_lat_rep = np.repeat(dst_lat_ch.T, 9)
            diff_lon_rv = np.ravel(diff_lon, order="F")
            dist_merid = diff_lon_rv * np.cos(dst_lat_rep * np.pi / 180)
            dist_zonal = sc_lat_rv[ind_rv] - dst_lat_rep

            dist_tot = np.power(
                (np.power(dist_merid, 2) + np.power(dist_zonal, 2)), 0.5
            )
            dist_tot = dist_tot.reshape(ind.shape, order="F").T
            # Get sort inds, and sort
            dist_ind = np.argsort(dist_tot, axis=1, kind="mergesort")
            dist_tot = dist_tot[np.arange(dist_tot.shape[0])[:, None], dist_ind]

            # Shuffle ind to reflect ascending dist of source and dst points
            ind = ind.T
            for p in range(ind.shape[0]):
                ind[p, :] = ind[p, dist_ind[p, :]]

            if self.key_vec:
                self.gcos = np.append(
                    self.gcos,
                    sc_gcos.flatten("F")[ind].reshape(ind.shape, order="F"),
                    axis=0,
                )
                self.gsin = np.append(
                    self.gsin,
                    sc_gsin.flatten("F")[ind].reshape(ind.shape, order="F"),
                    axis=0,
                )
                self.sc_chunk = np.append(
                    self.sc_chunk, np.zeros(ind.shape[0]) + all_chunk[c], axis=0
                )

            sc_ind = {}
            sc_ind["ind"] = ind
            sc_ind["imin"], sc_ind["imax"] = imin, imax
            sc_ind["jmin"], sc_ind["jmax"] = jmin, jmax

            # Fig not implemented
            # Sri TODO::: key_vec compare to assign gcos and gsin
            # Determine 1-2-1 filter indices
            id_121 = np.zeros((self.num_bdy_ch[c], 3), dtype=np.int64)
            for r in range(int(np.amax(bdy_r[chunk])) + 1):
                r_id = bdy_r[chunk] != r
                rr_id = bdy_r[chunk] == r
                tmp_lon = dst_lon_ch.copy()
                tmp_lon[r_id] = -9999
                tmp_lat = dst_lat_ch.copy()
                tmp_lat[r_id] = -9999
                source_tree = None
                try:
                    source_tree = sp.cKDTree(
                        list(zip(tmp_lon.ravel(order="F"), tmp_lat.ravel(order="F"))),
                        balanced_tree=False,
                        compact_nodes=False,
                    )
                except TypeError:  # fix for scipy 0.16.0
                    source_tree = sp.cKDTree(
                        list(zip(tmp_lon.ravel(order="F"), tmp_lat.ravel(order="F")))
                    )

                dst_pts = list(
                    zip(
                        dst_lon_ch[rr_id].ravel(order="F"),
                        dst_lat_ch[rr_id].ravel(order="F"),
                    )
                )
                junk, an_id = source_tree.query(dst_pts, k=3, distance_upper_bound=fr)
                id_121[rr_id, :] = an_id
            #            id_121[id_121 == len(dst_lon_ch)] = 0

            reptile = np.tile(id_121[:, 0], 3).reshape(id_121.shape, order="F")
            tmp_reptile = reptile * (id_121 == len(dst_lon_ch))
            id_121[id_121 == len(dst_lon_ch)] = 0
            tmp_reptile[tmp_reptile == len(dst_lon_ch)] = 0
            id_121 = id_121 + tmp_reptile
            #        id_121 = id_121 + reptile * (id_121 == len(dst_lon_ch))

            rep_dims = (id_121.shape[0], id_121.shape[1], sc_z_len)
            rep_dims_2d = (id_121.shape[0], id_121.shape[1], 1)
            # These tran/tiles work like matlab. Tested with same Data.
            id_121_2d = id_121.repeat(1).reshape(rep_dims_2d).transpose(2, 0, 1)
            reptile = (
                np.arange(1).repeat(self.num_bdy_ch[c]).reshape(1, self.num_bdy_ch[c])
            )
            reptile = (
                reptile.repeat(3)
                .reshape(self.num_bdy_ch[c], 3, 1, order="F")
                .transpose(2, 0, 1)
            )

            id_121_2d = sub2ind((1, self.num_bdy_ch[c]), id_121_2d, reptile)

            id_121 = id_121.repeat(sc_z_len).reshape(rep_dims).transpose(2, 0, 1)
            reptile = (
                np.arange(sc_z_len)
                .repeat(self.num_bdy_ch[c])
                .reshape(sc_z_len, self.num_bdy_ch[c])
            )
            reptile = (
                reptile.repeat(3)
                .reshape(self.num_bdy_ch[c], 3, sc_z_len, order="F")
                .transpose(2, 0, 1)
            )

            id_121_3d = sub2ind((sc_z_len, self.num_bdy_ch[c]), id_121, reptile)

            tmp_filt = wei_121.repeat(self.num_bdy_ch[c]).reshape(
                self.num_bdy_ch[c], len(wei_121), order="F"
            )
            tmp_filt_2d = (
                tmp_filt.repeat(1)
                .reshape(self.num_bdy_ch[c], len(wei_121), 1)
                .transpose(2, 0, 1)
            )

            tmp_filt_3d = (
                tmp_filt.repeat(sc_z_len)
                .reshape(self.num_bdy_ch[c], len(wei_121), sc_z_len)
                .transpose(2, 0, 1)
            )

            # Fig not implemented

            if not isslab:  # TODO or no vertical interpolation required
                # Determine vertical weights for the linear interpolation
                # onto Dst grid
                # Allocate vertical index array
                dst_dep_rv = dst_dep[:, chunk].ravel(order="F").filled(np.nan)
                z_ind = np.zeros((self.num_bdy_ch[c] * dst_len_z, 2), dtype=np.int64)
                source_tree = None
                try:
                    source_tree = sp.cKDTree(
                        list(zip(sc_z.ravel(order="F"))),
                        balanced_tree=False,
                        compact_nodes=False,
                    )
                except TypeError:  # fix for scipy 0.16.0
                    source_tree = sp.cKDTree(list(zip(sc_z.ravel(order="F"))))

                junk, nn_id = source_tree.query(list(zip(dst_dep_rv)), k=1)

                # WORKAROUND: the tree query returns out of range val when
                # dst_dep point is NaN, causing ref problems later.
                nn_id[nn_id == sc_z_len] = sc_z_len - 1

                # Find next adjacent point in the vertical
                z_ind[:, 0] = nn_id
                z_ind[sc_z[nn_id] > dst_dep_rv[:], 1] = (
                    nn_id[sc_z[nn_id] > dst_dep_rv[:]] - 1
                )
                z_ind[sc_z[nn_id] <= dst_dep_rv[:], 1] = (
                    nn_id[sc_z[nn_id] <= dst_dep_rv[:]] + 1
                )
                # Adjust out of range values
                z_ind[z_ind == -1] = 0
                z_ind[z_ind == sc_z_len] = sc_z_len - 1

                # Create weightings array
                z_dist = np.abs(
                    sc_z[z_ind]
                    - dst_dep[:, chunk].T.repeat(2).reshape(len(dst_dep_rv), 2)
                )
                rat = np.ma.sum(z_dist, axis=1)
                z_dist = 1 - (z_dist / rat.repeat(2).reshape(len(rat), 2))

                # Update z_ind for the dst array dims and vector indexing
                # Replicating this part of matlab is difficult without causing
                # a Memory Error. This workaround may be +/- brilliant
                # In theory it maximises memory efficiency
                z_ind[:, :] += np.arange(0, (self.num_bdy_ch[c]) * sc_z_len, sc_z_len)[
                    np.arange(self.num_bdy_ch[c]).repeat(2 * dst_len_z)
                ].reshape(z_ind.shape)
            else:
                z_ind = np.zeros([1, 1])
                z_dist = np.ma.zeros([1, 1])
            # End isslab

            # Put variables in list and array

            sc_ind_ch.append(sc_ind)
            self.dist_tot[chunk, :] = dist_tot
            self.tmp_filt_2d[:, chunk, :] = tmp_filt_2d
            self.tmp_filt_3d[:, chunk, :] = tmp_filt_3d
            self.id_121_2d[:, chunk, :] = id_121_2d
            self.id_121_3d[:, chunk, :] = id_121_3d
            self.z_ind[chunk_z_bool, :] = z_ind
            self.z_dist[chunk_z_bool, :] = z_dist

            # End of chunk loop

        # Set instance attributes
        self.first = True
        self.nav_lon = DC.lonlat[grd]["lon"]
        self.nav_lat = DC.lonlat[grd]["lat"]
        self.sc_ind_ch = sc_ind_ch
        self.num_bdy = num_bdy
        if not isslab:
            self.bdy_z = DC.depths[self.g_type]["bdy_H"]
        else:
            self.bdy_z = np.zeros([1])
        self.dst_dep = dst_dep.filled(np.nan)
        self.dst_z = self.dst_dep
        self.sc_z_len = sc_z_len
        self.sc_time = sc_time

        self.d_bdy = {}

        # Need to qualify for key_vec
        for v in range(self.nvar):
            if grd == "v":
                self.d_bdy[self.var_nam[v + 1]] = {}
            else:
                self.d_bdy[self.var_nam[v]] = {}

    def extract_month(self, year, month):
        """
        Extract monthly data and interpolates onto the destination grid.

        Parameters
        ----------
        year -- year of data to be extracted
        month -- month of the year to be extracted
        """
        self.logger.info("extract_month function called")

        sc_time = self.sc_time
        sc_z_len = self.sc_z_len

        # define src/dst cals
        if self.settings.get("time_interpolation", True) is False:
            # Source calender
            self.S_cal = utime(sc_time.units, sc_time.calendar)
            # First second of the target month
            target_time = self.S_cal.date2num(datetime(year, month, 1))
            # Find index in source time counter for target year and month
            closest_time_ind = min(
                ind1
                for ind1, item in enumerate(sc_time.time_counter)
                if item >= target_time
            )
            # This is index for first and last date
            first_date = closest_time_ind
            last_date = first_date
            self.logger.info(
                "matched month: "
                + str(self.S_cal.num2date(sc_time.time_counter[last_date]))
            )
            # Set time counter for output as array
            self.time_counter = sc_time.time_counter[last_date : last_date + 1]
        else:
            sf, ed = self.cal_trans(
                sc_time.calendar,  # sc_time[0].calendar
                self.settings["dst_calendar"],
                year,
                month,
            )
            DstCal = utime("seconds since %d-1-1" % year, self.settings["dst_calendar"])
            dst_start = DstCal.date2num(datetime(year, month, 1))
            dst_end = DstCal.date2num(datetime(year, month, ed, 23, 59, 59))

            self.S_cal = utime(
                sc_time.units, sc_time.calendar
            )  # sc_time[0].units,sc_time[0].calendar)

            self.D_cal = utime(
                "seconds since %d-1-1" % self.settings["base_year"],
                self.settings["dst_calendar"],
            )

            src_date_seconds = np.zeros(len(sc_time.time_counter))
            for index in range(len(sc_time.time_counter)):
                tmp_date = self.S_cal.num2date(sc_time.time_counter[index])
                src_date_seconds[index] = DstCal.date2num(tmp_date) * sf

            # Get first and last date within range, init to cover entire range
            first_date = 0
            last_date = len(sc_time.time_counter) - 1
            rev_seq = list(range(len(sc_time.time_counter)))
            rev_seq.reverse()
            for date in rev_seq:
                if src_date_seconds[date] < dst_start:
                    first_date = date
                    break
            for date in range(len(sc_time.time_counter)):
                if src_date_seconds[date] > dst_end:
                    last_date = date
                    break

        self.logger.info("first/last dates: %s %s", first_date, last_date)

        # Identify missing values and scale factors if defined
        meta_data = []
        meta_range = self.nvar
        if self.key_vec:
            meta_range += 1
        for v in range(meta_range):
            meta_data.append({})
            for x in "mv", "sf", "os", "fv":
                meta_data[v][x] = np.ones((self.nvar, 1)) * np.NaN

        for v in range(self.nvar):
            #            meta_data[v] = self._get_meta_data(sc_time[first_date].file_name,
            #                                               self.var_nam[v], meta_data[v])
            meta_data[v] = sc_time.get_meta_data(self.var_nam[v], meta_data[v])

        if self.key_vec:
            #  n = self.nvar
            #            meta_data[n] = self.fnames_2[first_date].get_meta_data(self.var_nam[n], meta_data[n])
            meta_data[1] = self.fnames_2.get_meta_data(self.var_nam[1], meta_data[1])

        for vn in range(self.nvar):
            if self.key_vec is True and self.rot_dir == "j":
                self.d_bdy[self.var_nam[vn + 1]]["date"] = sc_time.date_counter[
                    first_date : last_date + 1
                ]
            else:
                self.d_bdy[self.var_nam[vn]]["date"] = sc_time.date_counter[
                    first_date : last_date + 1
                ]

        # Check year entry exists in d_bdy, if not create it with data holding array.
        for v in range(self.nvar):
            try:
                if self.key_vec is True and self.rot_dir == "j":
                    self.d_bdy[self.var_nam[v + 1]][year]
                else:
                    self.d_bdy[self.var_nam[v]][year]
            except KeyError:
                if len(sc_time[self.var_nam[v]]._get_dimensions()) == 3:
                    hold = np.zeros((((last_date + 1) - first_date), 1, self.num_bdy))
                else:
                    hold = np.zeros(
                        (((last_date + 1) - first_date), len(self.dst_z), self.num_bdy)
                    )

                if self.key_vec is True and self.rot_dir == "j":
                    self.d_bdy[self.var_nam[v + 1]][year] = {"data": hold, "date": {}}
                else:
                    self.d_bdy[self.var_nam[v]][year] = {"data": hold, "date": {}}

        # loop over chunks

        chunk_number = self.dst_chunk
        all_chunk = np.unique(chunk_number)

        for chk in range(len(all_chunk)):
            chunk_d = chunk_number == all_chunk[chk]
            chunk_z = self.z_chunk == all_chunk[chk]
            if self.key_vec:
                chunk_s = self.sc_chunk == all_chunk[chk]

            i_run = np.arange(self.sc_ind_ch[chk]["imin"], self.sc_ind_ch[chk]["imax"])
            j_run = np.arange(self.sc_ind_ch[chk]["jmin"], self.sc_ind_ch[chk]["jmax"])
            extended_i = np.arange(
                self.sc_ind_ch[chk]["imin"] - 1, self.sc_ind_ch[chk]["imax"]
            )
            extended_j = np.arange(
                self.sc_ind_ch[chk]["jmin"] - 1, self.sc_ind_ch[chk]["jmax"]
            )
            ind = self.sc_ind_ch[chk]["ind"]

            if self.first:
                sc_z_len = self.sc_z_len
                nc_3 = GetFile(self.settings["src_msk"])
                varid_3 = nc_3["tmask"]
                t_mask = varid_3[
                    :1,
                    :sc_z_len,
                    np.min(j_run) : np.max(j_run) + 1,
                    np.min(i_run) : np.max(i_run) + 1,
                ]
                if self.key_vec:
                    varid_3 = nc_3["umask"]
                    u_mask = varid_3[
                        :1,
                        :sc_z_len,
                        np.min(j_run) : np.max(j_run) + 1,
                        np.min(extended_i) : np.max(extended_i) + 1,
                    ]
                    varid_3 = nc_3["vmask"]
                    v_mask = varid_3[
                        :1,
                        :sc_z_len,
                        np.min(extended_j) : np.max(extended_j) + 1,
                        np.min(i_run) : np.max(i_run) + 1,
                    ]
                nc_3.close()

            # Loop over identified files
            for f in range(first_date, last_date + 1):
                sc_array = [None, None]
                sc_alt_arr = [None, None]
                # self.logger.info('opening nc file: %s', sc_time[f].file_name)
                # Counters not implemented

                sc_bdy = {}
                # sc_bdy = np.zeros((len(self.var_nam), sc_z_len, ind.shape[0],
                #                   ind.shape[1]))

                # Loop over time entries from file f
                for vn in range(self.nvar):
                    # Extract sub-region of data
                    self.logger.info("var_nam = %s", self.var_nam[vn])
                    varid = sc_time[self.var_nam[vn]]
                    # If extracting vector quantities open second var
                    if self.key_vec:
                        varid_2 = self.fnames_2[
                            self.var_nam[vn + 1]
                        ]  # nc_2.variables[self.var_nam[vn + 1]]

                    # Determine if slab or not
                    isslab = len(varid._get_dimensions()) == 3

                    # Set up tmp dict of tmp arrays
                    if isslab:
                        sc_z_len = 1
                    else:
                        sc_z_len = self.sc_z_len

                    sc_bdy[vn] = np.zeros((sc_z_len, ind.shape[0], ind.shape[1]))
                    if self.key_vec:
                        sc_bdy[vn + 1] = np.zeros(
                            (sc_z_len, ind.shape[0], ind.shape[1])
                        )

                    # Extract 3D scalar variables
                    if not isslab and not self.key_vec:
                        self.logger.info(" 3D source array ")
                        sc_array[0] = varid[
                            f : f + 1,
                            :sc_z_len,
                            np.min(j_run) : np.max(j_run) + 1,
                            np.min(i_run) : np.max(i_run) + 1,
                        ]
                    # Extract 3D vector variables
                    elif self.key_vec:
                        # For u vels take i-1
                        sc_alt_arr[0] = varid[
                            f : f + 1,
                            :sc_z_len,
                            np.min(j_run) : np.max(j_run) + 1,
                            np.min(extended_i) : np.max(extended_i) + 1,
                        ]
                        # For v vels take j-1
                        sc_alt_arr[1] = varid_2[
                            f : f + 1,
                            :sc_z_len,
                            np.min(extended_j) : np.max(extended_j) + 1,
                            np.min(i_run) : np.max(i_run) + 1,
                        ]
                    # Extract 2D scalar vars
                    else:
                        self.logger.info(" 2D source array ")
                        sc_array[0] = varid[
                            f : f + 1,
                            np.min(j_run) : np.max(j_run) + 1,
                            np.min(i_run) : np.max(i_run) + 1,
                        ].reshape([1, 1, j_run.size, i_run.size])

                    # Average vector vars onto T-grid
                    if self.key_vec:
                        # First make sure land points have a zero val
                        sc_alt_arr[0] *= u_mask
                        sc_alt_arr[1] *= v_mask
                        # Average from to T-grid assuming C-grid stagger
                        sc_array[0] = 0.5 * (
                            sc_alt_arr[0][:, :, :, :-1] + sc_alt_arr[0][:, :, :, 1:]
                        )
                        sc_array[1] = 0.5 * (
                            sc_alt_arr[1][:, :, :-1, :] + sc_alt_arr[1][:, :, 1:, :]
                        )

                    # Set land points to NaN and adjust with any scaling
                    # Factor offset
                    # Note using isnan/sum is relatively fast, but less than
                    # bottleneck external lib
                    self.logger.info(
                        "SC ARRAY MIN MAX : %s %s",
                        np.nanmin(sc_array[0]),
                        np.nanmax(sc_array[0]),
                    )

                    if isslab and not self.key_vec:
                        sc_array[0][t_mask[:, 0:1, :, :] == 0] = np.NaN
                    else:
                        sc_array[0][t_mask == 0] = np.NaN
                    self.logger.info(
                        "SC ARRAY MIN MAX : %s %s",
                        np.nanmin(sc_array[0]),
                        np.nanmax(sc_array[0]),
                    )
                    if not np.isnan(np.sum(meta_data[vn]["sf"])):
                        sc_array[0] *= meta_data[vn]["sf"]
                    if not np.isnan(np.sum(meta_data[vn]["os"])):
                        sc_array[0] += meta_data[vn]["os"]

                    if self.key_vec:
                        sc_array[1][t_mask == 0] = np.NaN
                        if not np.isnan(np.sum(meta_data[vn + 1]["sf"])):
                            sc_array[1] *= meta_data[vn + 1]["sf"]
                        if not np.isnan(np.sum(meta_data[vn + 1]["os"])):
                            sc_array[1] += meta_data[vn + 1]["os"]

                    # Now collapse the extracted data to an array
                    # containing only nearest neighbours to dest bdy points
                    # Loop over the depth axis
                    for dep in range(sc_z_len):
                        tmp_arr = [None, None]
                        # Consider squeezing
                        tmp_arr[0] = sc_array[0][0, dep, :, :].flatten("F")  # [:,:,dep]
                        if not self.key_vec:
                            sc_bdy[vn][dep, :, :] = self._flat_ref(tmp_arr[0], ind)
                        else:
                            tmp_arr[1] = sc_array[1][0, dep, :, :].flatten(
                                "F"
                            )  # [:,:,dep]
                            # Include in the collapse the rotation from the
                            # grid to real zonal direction, ie ij -> e
                            sc_bdy[vn][dep, :] = (
                                tmp_arr[0][ind[:]] * self.gcos[chunk_s, :]
                                - tmp_arr[1][ind[:]] * self.gsin[chunk_s, :]
                            )
                            # Include... meridinal direction, ie ij -> n
                            sc_bdy[vn + 1][dep, :] = (
                                tmp_arr[1][ind[:]] * self.gcos[chunk_s, :]
                                + tmp_arr[0][ind[:]] * self.gsin[chunk_s, :]
                            )

                    # End depths loop
                    self.logger.info(" END DEPTHS LOOP ")
                # End Looping over vars
                self.logger.info(" END VAR LOOP ")
                # ! Skip sc_bdy permutation

                x = sc_array[0]
                y = np.isnan(x)
                z = np.invert(np.isnan(x))
                x[y] = 0
                self.logger.info("nans: %s", np.sum(y[:]))
                # x = x[np.invert(y)]
                self.logger.info(
                    "%s %s %s %s",
                    x.shape,
                    np.sum(x[z], dtype=np.float64),
                    np.amin(x),
                    np.amax(x),
                )

                # Calculate weightings to be used in interpolation from
                # source data to dest bdy pts. Only need do once.
                # if self.first:
                for vn in range(self.nvar):
                    varid = sc_time[self.var_nam[vn]]
                    # Determine if slab or not
                    isslab = len(varid._get_dimensions()) == 3

                    # Set up tmp dict of tmp arrays
                    if isslab:
                        sc_z_len = 1
                    else:
                        sc_z_len = self.sc_z_len

                    # identify valid pts
                    data_ind = np.invert(np.isnan(sc_bdy[vn][:, :, :]))
                    # dist_tot is currently 2D so extend along depth
                    # axis to allow single array calc later, also remove
                    # any invalid pts using our eldritch data_ind
                    self.logger.info(
                        "DIST TOT ZEROS BEFORE %s",
                        np.sum(self.dist_tot[chunk_d, :] == 0),
                    )
                    dist_tot = (
                        np.repeat(self.dist_tot[chunk_d, :], sc_z_len).reshape(
                            self.dist_tot[chunk_d, :].shape[0],
                            self.dist_tot[chunk_d, :].shape[1],
                            sc_z_len,
                        )
                    ).transpose(2, 0, 1)
                    dist_tot *= data_ind
                    self.logger.info("DIST TOT ZEROS %s", np.sum(dist_tot == 0))

                    self.logger.info("DIST IND ZEROS %s", np.sum(data_ind == 0))

                    # Identify problem pts due to grid discontinuities
                    # using dists >  lat
                    over_dist = np.sum(dist_tot[:] > 4)
                    if over_dist > 0:
                        raise RuntimeError(
                            """Distance between source location
                                              and new boundary points is greater
                                              than 4 degrees of lon/lat"""
                        )

                    # Calculate guassian weighting with correlation dist
                    r0 = self.settings["r0"]
                    dist_wei = (1 / (r0 * np.power(2 * np.pi, 0.5))) * (
                        np.exp(-0.5 * np.power(dist_tot / r0, 2))
                    )
                    # Calculate sum of weightings
                    dist_fac = np.sum(dist_wei * data_ind, 2)
                    # identify loc where all sc pts are land
                    nan_ind = np.sum(data_ind, 2) == 0
                    self.logger.info("NAN IND : %s ", np.sum(nan_ind))

                    # Calc max zlevel to which data available on sc grid
                    data_ind = np.sum(nan_ind == 0, 0) - 1
                    # set land val to level 1 otherwise indexing problems
                    # may occur- should not affect later results because
                    # land is masked in weightings array
                    data_ind[data_ind == -1] = 0
                    # transform depth levels at each bdy pt to vector
                    # index that can be used to speed up calcs
                    data_ind += np.arange(0, sc_z_len * self.num_bdy_ch[chk], sc_z_len)

                    # ? Attribute only used on first run so clear.
                    del dist_tot

                    # weighted averaged onto new horizontal grid
                    self.logger.info(
                        " sc_bdy %s %s", np.nanmin(sc_bdy[vn]), np.nanmax(sc_bdy[vn])
                    )
                    dst_bdy = np.zeros_like(dist_fac) * np.nan
                    # dst_bdy = np.zeros_like(dist_fac)
                    ind_valid = dist_fac > 0.0
                    dst_bdy[ind_valid] = (
                        np.nansum(sc_bdy[vn][:, :, :] * dist_wei, 2)[ind_valid]
                        / dist_fac[ind_valid]
                    )
                    # dst_bdy = (np.nansum(sc_bdy[vn][:,:,:] * dist_wei, 2) /
                    #           dist_fac)
                    self.logger.info(
                        " dst_bdy %s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy)
                    )
                    # Quick check to see we have not got bad values
                    if np.sum(dst_bdy == np.inf) > 0:
                        raise RuntimeError(
                            """Bad values found after
                                              weighted averaging"""
                        )

                    # weight vector array and rotate onto dest grid
                    if self.key_vec:
                        # [:,:,:,vn+1]
                        dst_bdy_2 = np.zeros_like(dist_fac)
                        ind_valid = dist_fac > 0.0
                        dst_bdy_2[ind_valid] = (
                            np.nansum(sc_bdy[vn + 1][:, :, :] * dist_wei, 2)[ind_valid]
                            / dist_fac[ind_valid]
                        )
                        # dst_bdy_2 = (np.nansum(sc_bdy[vn+1][:,:,:] * dist_wei, 2) /
                        #             dist_fac)
                        self.logger.info("time to to rot and rep ")
                        self.logger.info(
                            "%s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy)
                        )
                        self.logger.info(
                            "%s en to %s %s", self.rot_dir, self.rot_dir, dst_bdy.shape
                        )
                        dst_bdy = rot_rep(
                            dst_bdy,
                            dst_bdy_2,
                            self.rot_dir,
                            "en to %s" % self.rot_dir,
                            self.dst_gcos[:, chunk_d],
                            self.dst_gsin[:, chunk_d],
                        )
                        self.logger.info(
                            "%s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy)
                        )
                    # Apply 1-2-1 filter along bdy pts using NN ind self.id_121
                    if False:  # turning off filter for now
                        # if self.first:
                        if isslab:
                            id_121 = self.id_121_2d[:, chunk_d, :]
                            tmp_filt = self.tmp_filt_2d[:, chunk_d, :]
                        else:
                            id_121 = self.id_121_3d[:, chunk_d, :]
                            tmp_filt = self.tmp_filt_3d[:, chunk_d, :]

                        tmp_valid = np.invert(np.isnan(dst_bdy.flatten("F")[id_121]))

                        dst_bdy = np.nansum(
                            dst_bdy.flatten("F")[id_121] * tmp_filt, 2
                        ) / np.sum(tmp_filt * tmp_valid, 2)

                        # Finished first run operations
                        # self.first = False

                    # Set land pts to zero
                    self.logger.info(
                        " pre dst_bdy[nan_ind] %s %s",
                        np.nanmin(dst_bdy),
                        np.nanmax(dst_bdy),
                    )
                    dst_bdy[nan_ind] = 0
                    self.logger.info(
                        " post dst_bdy %s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy)
                    )
                    # Remove any data on dst grid that is in land
                    dst_bdy[:, np.isnan(self.bdy_z[chunk_d])] = 0
                    self.logger.info(
                        " 3 dst_bdy %s %s", np.nanmin(dst_bdy), np.nanmax(dst_bdy)
                    )

                    # If we have depth dimension
                    if not isslab:
                        # If all else fails fill down using deepest pt
                        dst_bdy = dst_bdy.flatten("F")
                        dst_bdy += (dst_bdy == 0) * dst_bdy[data_ind].repeat(sc_z_len)
                        # Weighted averaged on new vertical grid
                        dst_bdy = (
                            dst_bdy[self.z_ind[chunk_z, 0]] * self.z_dist[chunk_z, 0]
                            + dst_bdy[self.z_ind[chunk_z, 1]] * self.z_dist[chunk_z, 1]
                        )
                        data_out = dst_bdy.reshape(
                            self.dst_dep[:, chunk_d].shape, order="F"
                        )

                        # If z-level replace data below bed !!! make stat
                        # of this as could be problematic
                        ind_z = self.bdy_z[chunk_d].repeat(
                            len(self.dst_dep[:, chunk_d])
                        )
                        ind_z = ind_z.reshape(
                            len(self.dst_dep[:, chunk_d]),
                            len(self.bdy_z[chunk_d]),
                            order="F",
                        )
                        ind_z -= self.dst_dep[:, chunk_d]
                        ind_z = ind_z < 0
                        data_out[ind_z] = np.NaN
                    else:
                        data_out = dst_bdy
                        data_out[:, np.isnan(self.bdy_z[chunk_d])] = np.NaN

                    # add data to self.d_bdy
                    if self.key_vec is True and self.rot_dir == "j":
                        self.d_bdy[self.var_nam[vn + 1]][year]["data"][
                            int(f - first_date), :, chunk_d
                        ] = data_out.T
                    else:
                        self.d_bdy[self.var_nam[vn]][year]["data"][
                            int(f - first_date), :, chunk_d
                        ] = data_out.T

        # Need stats on fill pts in z and horiz + missing pts...

    # end month
    # end year
    # End great loop of crawling chaos

    # Allows reference of two equal sized but misshapen arrays
    # equivalent to Matlab alpha(beta(:))
    def _flat_ref(self, alpha, beta):
        """
        Extract input index elements from array and order them in Fotran array and return the new array.

        Parameters
        ----------
        alpha -- input array
        beta -- index array
        """
        return alpha.flatten("F")[beta.flatten("F")].reshape(beta.shape, order="F")

    # Convert numeric date from source to dest
    #   def convert_date(self, date):
    #       val = self.S_cal.num2date(date)
    #       return self.D_cal.date2num(val)

    def cal_trans(self, source, dest, year, month):
        """
        Translate between calendars and return scale factor and number of days in month.

        Parameters
        ----------
        source -- source calendar
        dest -- destination calendar
        year -- input year
        month -- input month
        """
        vals = {"gregorian": 365.0 + isleap(year), "noleap": 365.0, "360_day": 360.0}
        if source not in list(vals.keys()):
            raise ValueError("Unknown source calendar type: %s" % source)
        # Get month length
        if dest == "360_day":
            ed = 30
        else:
            ed = monthrange(year, month)[1]
        # Calculate scale factor
        sf = vals[source] / vals[dest]

        return sf, ed

    # BEWARE FORTRAN V C ordering
    # Replicates and tiles an array
    # def _trig_reptile(self, trig, size):
    #    trig = np.transpose(trig, (2, 1, 0)) # Matlab 2 0 1
    #    return np.tile(trig, (1, size, 1)) # Matlab size 1 1

    def time_delta(self, time_counter):
        """
        Get time delta and number of time steps per day.

        Calculates difference between time steps for time_counter and checks
        these are uniform. Then retrives the number of time steps per day.

        Parameters
        ----------
        time_counter
            model time coordinate

        Returns
        -------
        deltaT
            length of time step
        dstep
            number of time steps per day
        """
        # get time derivative
        deltaT = np.diff(time_counter)

        # check for uniform time steps
        if not np.all(deltaT == deltaT[0]):
            self.logger.warning("time interpolation expects uniform time step.")
            self.logger.warning("time_counter is not uniform.")

        # get  number of timesteps per day (zero if deltaT > 86400)
        dstep = 86400 // int(deltaT[0])

        return deltaT[0], dstep

    def time_interp(self, year, month):
        """
        Perform a time interpolation of the BDY data to daily frequency.

        Notes
        -----
        This method performs a time interpolation (if required). This is
        necessary if the time frequency is not a factor of monthly output or the
        input and output calendars differ. CF compliant calendar options
        accepted: gregorian | standard, proleptic_gregorian, noleap | 365_day,
        360_day or julian.*
        """
        # RDP: this could be made more flexible to interpolate to other deltaTs

        # Extract time information
        # TODO: check that we can just use var_nam[0]. Rational is that if
        # we're grouping variables then they must all have the same date stamps
        if self.key_vec is True and self.rot_dir == "j":
            var_id = 1
        else:
            var_id = 0

        nt = len(self.d_bdy[self.var_nam[var_id]]["date"])
        time_counter = np.zeros([nt])
        tmp_cal = utime(
            "seconds since %d-1-1" % year, self.settings["dst_calendar"].lower()
        )

        for t in range(nt):
            time_counter[t] = tmp_cal.date2num(
                self.d_bdy[self.var_nam[var_id]]["date"][t]
            )

        date_000 = datetime(year, month, 1, 12, 0, 0)
        if month < 12:
            date_end = datetime(year, month + 1, 1, 12, 0, 0)
        else:
            date_end = datetime(year + 1, 1, 1, 12, 0, 0)
        time_000 = tmp_cal.date2num(date_000)
        time_end = tmp_cal.date2num(date_end)

        # get deltaT and number of time steps per day (dstep)
        del_t, dstep = self.time_delta(time_counter)

        if self.key_vec is True:
            if self.rot_dir == "i":
                varnams = [
                    self.var_nam[0],
                ]
            else:
                varnams = [
                    self.var_nam[1],
                ]
        else:
            varnams = self.var_nam

        # target time index
        target_time = np.arange(time_000, time_end, 86400)

        # interpolate
        for v in varnams:
            if del_t >= 86400.0:  # upsampling
                intfn = interp1d(
                    time_counter,
                    self.d_bdy[v][year]["data"][:, :, :],
                    axis=0,
                    bounds_error=True,
                )
                self.d_bdy[v][year]["data"] = intfn(target_time)
            else:  # downsampling
                for t in range(dstep):
                    intfn = interp1d(
                        time_counter[t::dstep],
                        self.d_bdy[v].data[t::dstep, :, :],
                        axis=0,
                        bounds_error=True,
                    )
                    self.d_bdy[v].data[t::dstep, :, :] = intfn(target_time)

        # update time_counter
        self.time_counter = target_time

        # RDP: self.d_bdy[v]["date"] is not updated during interpolation, but
        #      self.time_counter is. This could be prone to unexpected errors.

    def write_out(self, year, month, ind, unit_origin):
        """
        Write monthy BDY data to netCDF file.

        Notes
        -----
        This method writes out all available variables for a given grid along with
        any asscoaied metadata. Currently data are only written out as monthly
        files.

        Parameters
        ----------
        year         (int) : year to write out
        month        (int) : month to write out
        ind          (dict): dictionary holding grid information
        unit_origin  (str) : time reference '%d-01-01 00:00:00' %year_000

        Returns
        -------
            None
        """
        # Define output filename

        self.logger.info(
            "Defining output file for grid %s, month: %d, year: %d",
            self.g_type.upper(),
            month,
            year,
        )

        f_out = (
            self.settings["dst_dir"]
            + self.settings["fn"]
            + "_bdy"
            + self.g_type.upper()
            + "_y"
            + str(year)
            + "m"
            + "%02d" % month
            + ".nc"
        )

        ncgen.CreateBDYNetcdfFile(
            f_out,
            self.num_bdy,
            self.jpi,
            self.jpj,
            self.jpk,
            self.settings["rimwidth"],
            self.settings["dst_metainfo"],
            unit_origin,
            self.settings["fv"],
            self.settings["dst_calendar"],
            self.g_type.upper(),
        )

        self.logger.info("Writing out BDY data to: %s", f_out)

        # Loop over variables in extracted object

        #        for v in self.variables:
        if self.key_vec is True:
            if self.rot_dir == "i":
                varnams = [
                    self.var_nam[0],
                ]
            else:
                varnams = [
                    self.var_nam[1],
                ]
        else:
            varnams = self.var_nam

        for v in varnams:
            if self.settings["dyn2d"] and (
                (v == "vozocrtx") or (v == "vomecrty")
            ):  # Calculate depth averaged velocity
                tile_dz = np.tile(self.bdy_dz, [len(self.time_counter), 1, 1, 1])
                tmp_var = np.reshape(
                    self.d_bdy[v][year]["data"][:, :, :], tile_dz.shape
                )
                tmp_var = np.nansum(tmp_var * tile_dz, 2) / np.nansum(tile_dz, 2)
                # Write variable to file
                if v == "vozocrtx":
                    ncpop.write_data_to_file(f_out, "vobtcrtx", tmp_var)
                else:
                    ncpop.write_data_to_file(f_out, "vobtcrty", tmp_var)

            # else: # Replace NaNs with specified fill value

            tmp_var = np.where(
                np.isnan(self.d_bdy[v][year]["data"][:, :, :]),
                self.settings["fv"],
                self.d_bdy[v][year]["data"][:, :, :],
            )
            jpk, jpj, jpi = tmp_var.shape
            if jpj > 1:
                for k in range(jpk):
                    tmp_var[k, :, :] = np.where(
                        np.isnan(self.dst_dep), self.settings["fv"], tmp_var[k, :, :]
                    )

            # Write variable to file
            ncpop.write_data_to_file(f_out, v, tmp_var)

        # check depth array has had NaNs removed

        tmp_dst_dep = np.where(
            np.isnan(self.dst_dep), self.settings["fv"], self.dst_dep
        )

        # Write remaining data to file (indices are in Python notation
        # therefore we must add 1 to i,j and r)
        ncpop.write_data_to_file(f_out, "nav_lon", self.nav_lon)
        ncpop.write_data_to_file(f_out, "nav_lat", self.nav_lat)
        ncpop.write_data_to_file(f_out, "gdep" + self.g_type, tmp_dst_dep)
        # TODO: e3 is just populated with gdep
        ncpop.write_data_to_file(f_out, "e3" + self.g_type, tmp_dst_dep)
        ncpop.write_data_to_file(f_out, "nbidta", ind.bdy_i[:, 0] + 1)
        ncpop.write_data_to_file(f_out, "nbjdta", ind.bdy_i[:, 1] + 1)
        ncpop.write_data_to_file(f_out, "nbrdta", ind.bdy_r[:] + 1)
        ncpop.write_data_to_file(f_out, "time_counter", self.time_counter)
        if self.g_type == "t":
            ncpop.write_data_to_file(f_out, "bdy_msk", self.bdy_msk)
