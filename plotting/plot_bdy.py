#!/usr/bin/env python3
# ===================================================================
# Copyright 2025 National Oceanography Centre.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================


"""
Script to plot extracted variables along boundary sections.

Args:
----
fname     (str) : filename of BDY file
variable  (str) : variable in file to plot.
filename  (str) : optional filename (png is added)

Example usage:
--------------
# 1D line plots of elevation
python plotting/plot_bdy.py outputs/NNA_R12_bdyT_y1979m11.nc sossheig
# 2D section plots of temperature
python plotting/plot_bdy.py outputs/NNA_R12_bdyT_y1979m11.nc votemper
# specify filename
python plotting/plot_bdy.py outputs/NNA_R12_bdyT_y1979m11.nc votemper filename

To do:
------
* labelling of plots : Add variable name
* Which segment is where? Add x-axis label could be bdy index?
* Not sure why sometime tmp.png (bdy index on map) is plotted and sometime not
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial as sp
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from netCDF4 import Dataset


def nemo_bdy_order(fname):
    """
    Determine the ordering and breaks in BDY files to aid plotting.

    This function takes the i/j coordinates from BDY files and orders them sequentially
    making it easier to visualise sections along the open boundary. Breaks in the open
    boundary are also determined (i.e. where the distance between two points > 2**0.5)

    Args:
    ----
        fname     (str) : filename of BDY file

    Returns:
    -------
        bdy_ind   (dict): re-ordered indices
        bdy_dst   (dict): distance (in model coords) between points
        bdy_brk   (dict): location of the break points in the open boundary
    """
    # open file pointer and extract data
    rootgrp = Dataset(fname, "r", format="NETCDF4")
    nbi = (
        np.squeeze(rootgrp.variables["nbidta"][:, :]) - 1
    )  # subtract 1 for python indexing
    nbj = np.squeeze(rootgrp.variables["nbjdta"][:, :]) - 1
    nbr = np.squeeze(rootgrp.variables["nbrdta"][:, :]) - 1
    np.squeeze(rootgrp.variables["nav_lon"][:, :])
    np.squeeze(rootgrp.variables["nav_lat"][:, :])
    rootgrp.close()

    rw = np.amax(nbr) + 1
    bdy_ind = {}
    bdy_brk = {}
    bdy_dst = {}
    nbdy = []

    for r in range(rw):
        nbdy.append(np.sum(nbr == r))

    # TODO: deal with domain that spans wrap

    # start with outer rim and work in

    for r in range(rw):
        # set initial constants

        ind = nbr == r
        nbi_tmp = nbi[ind]
        nbj_tmp = nbj[ind]

        count = 1
        id_order = np.zeros((nbdy[r], 1), dtype=int) - 1
        id_order[0,] = 0
        flag = False
        mark = 0
        source_tree = sp.cKDTree(
            list(zip(nbi_tmp, nbj_tmp)), balanced_tree=False, compact_nodes=False
        )

        # order bdy entries

        while count < nbdy[r]:
            nn_dist, nn_id = source_tree.query(
                list(zip(nbi_tmp[id_order[count - 1]], nbj_tmp[id_order[count - 1]])),
                k=3,
                distance_upper_bound=2.9,
            )
            if (
                np.sum(id_order == nn_id[0, 1]) == 1
            ):  # is the nearest point already in the list?
                if (
                    np.sum(id_order == nn_id[0, 2]) == 1
                ):  # is the 2nd nearest point already in the list?
                    if (
                        flag is False
                    ):  # then we've found an end point and we can start the search in earnest!
                        flag = True
                        id_order[mark] = id_order[count - 1]  # reset values
                        id_order[mark + 1 :] = -1  # reset values
                        count = mark + 1  # reset counter
                    else:
                        i = 0  # should this be zero?
                        t = count
                        while count == t:
                            if np.sum(id_order == i) == 1:
                                i += 1
                            else:
                                id_order[count] = i
                                flag = False
                                mark = count
                                count += 1
                elif nn_id[0, 2] == nbdy[r]:
                    i = 0
                    t = count
                    while count == t:
                        if np.sum(id_order == i) == 1:
                            i += 1
                        else:
                            id_order[count] = i
                            flag = False
                            mark = count
                            count += 1
                else:
                    id_order[count] = nn_id[0, 2]
                    count += 1
            else:
                id_order[count] = nn_id[0, 1]
                count += 1

        bdy_ind[r] = id_order
        bdy_dst[r] = np.sqrt(
            (
                np.diff(np.hstack((nbi_tmp[id_order], nbj_tmp[id_order])), axis=0) ** 2
            ).sum(axis=1)
        )
        (bdy_brk[r],) = np.where(bdy_dst[r] > 2**0.5)
        bdy_brk[r] += 1
        bdy_brk[r] = np.insert(bdy_brk[r], 0, 0)  # insert start point
        bdy_brk[r] = np.insert(
            bdy_brk[r], len(bdy_brk[r]), len(id_order)
        )  # insert end point
        bdy_dst[r] = np.insert(np.cumsum(bdy_dst[r]), 0, 0)

        if (
            r == 1
        ):  # change to a valid rw number to get a visual output (outer most rw is zero)
            f, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
            plt.scatter(nbi_tmp[bdy_ind[r][:]], nbj_tmp[bdy_ind[r][:]], s=1, marker=".")
            for t in np.arange(0, len(bdy_ind[r]), 20):
                plt.text(nbi_tmp[bdy_ind[r][t]], nbj_tmp[bdy_ind[r][t]], t)
            f.savefig("tmp.png")

    return bdy_ind, bdy_dst, bdy_brk


def process_plot_2d_sections(var, gdep, bdy_brk, bdy_ind, rw):
    """
    Plot 2d section along boundaries.

    Divide data into segments. Then (polgon patch) plot segments in separate panels as a function of depth

    Returns
    -------
        f - figure handle
    """
    jpk = len(gdep[:, 0])
    nsc = len(bdy_brk[rw][:]) - 1

    dep = {}
    dta = {}

    # divide data up into sections and re-order

    print(nsc)
    for n in range(nsc):
        dta[n] = np.squeeze(var[:, bdy_ind[rw][bdy_brk[rw][n] : bdy_brk[rw][n + 1]]])
        dep[n] = np.squeeze(gdep[:, bdy_ind[rw][bdy_brk[rw][n] : bdy_brk[rw][n + 1]]])

    # loop over number of sections and plot

    f, ax = plt.subplots(nrows=1, ncols=1, figsize=(11, 4))
    ax.plot(dta[0][10, :])
    ax.set_title("BDY points along section: 1, depth level: 10")

    f, ax = plt.subplots(nrows=nsc, ncols=1, figsize=(14, 10 * nsc))

    for n in range(nsc):
        if nsc > 1:
            nax = ax[n]
        else:
            nax = ax

        plt.sca(nax)
        # from gdep create some pseudo w points

        gdept = dep[n][:, :]
        coords = np.arange(0, len(gdept[0, :]))
        gdepw = np.zeros((len(gdept[:, 0]) + 1, len(gdept[0, :])))
        for z in range(jpk):
            gdepw[z + 1, :] = gdept[z, :] + (gdept[z, :] - gdepw[z, :])

        gdepvw = np.zeros((len(gdept[:, 0]) + 1, len(gdept[0, :]) + 1))

        # TODO: put in an adjustment for zps levels

        gdepvw[:, 1:-1] = (gdepw[:, :-1] + gdepw[:, 1:]) / 2
        gdepvw[:, 0] = gdepvw[:, 1]
        gdepvw[:, -1] = gdepvw[:, -2]

        # create a pseudo bathymetry from the depth data

        bathy = np.zeros_like(coords)
        np.sum(dta[n].mask == 0, axis=0)

        for i in range(len(coords)):
            bathy[i] = np.nanmax(gdepw[:, i])

        bathy_patch = Polygon(
            np.vstack(
                (
                    np.hstack((coords[0], coords, coords[-1])),
                    np.hstack((np.amax(bathy[:]), bathy, np.amax(bathy[:]))),
                )
            ).T,
            closed=True,
            facecolor=(0.8, 0.8, 0),
            alpha=0,
            edgecolor=None,
        )

        # Add patch to axes
        nax.add_patch(bathy_patch)
        nax.set_title("BDY points along section: " + str(n))
        patches = []
        colors = []

        for i in range(len(coords)):
            for k in np.arange(jpk - 2, -1, -1):
                if dta[n][k, i] > -10:
                    x = [
                        coords[i] - 0.5,
                        coords[i],
                        coords[i] + 0.5,
                        coords[i] + 0.5,
                        coords[i],
                        coords[i] - 0.5,
                        coords[i] - 0.5,
                    ]
                    y = [
                        gdepvw[k + 1, i],
                        gdepw[k + 1, i],
                        gdepvw[k + 1, i + 1],
                        gdepvw[k, i + 1],
                        gdepw[k, i],
                        gdepvw[k, i],
                        gdepvw[k + 1, i],
                    ]

                    polygon = Polygon(np.vstack((x, y)).T, closed=True)
                    patches.append(polygon)
                    colors = np.append(colors, dta[n][k, i])

        for i in range(len(coords)):
            for k in np.arange(jpk - 2, -1, -1):
                x = [
                    coords[i] - 0.5,
                    coords[i],
                    coords[i] + 0.5,
                    coords[i] + 0.5,
                    coords[i],
                    coords[i] - 0.5,
                    coords[i] - 0.5,
                ]
                y = [
                    gdepvw[k + 1, i],
                    gdepw[k + 1, i],
                    gdepvw[k + 1, i + 1],
                    gdepvw[k, i + 1],
                    gdepw[k, i],
                    gdepvw[k, i],
                    gdepvw[k + 1, i],
                ]
                plt.plot(x, y, "k-", linewidth=0.1)
                plt.plot(coords[i], gdept[k, i], "k.", markersize=1)

        plt.plot(coords, bathy, "-", color=(0.4, 0, 0))
        p = PatchCollection(patches, alpha=0.8, edgecolor="none")
        p.set_array(np.array(colors))
        nax.add_collection(p)
        f.colorbar(p, ax=nax)
        nax.set_ylim((0, np.max(bathy)))
        nax.invert_yaxis()

    return f


def process_plot_1d_sections(var, bdy_brk, bdy_ind, rw):
    """
    Plot 1d section along boundaries.

    Divide data into segments. Then (line) plot segments in separate panels

    Returns
    -------
        f - figure handle
    """
    nsc = len(bdy_brk[rw][:]) - 1  # number of sections
    dta = {}

    # divide data up into sections and re-order

    print(nsc)
    for n in range(nsc):
        dta[n] = np.squeeze(var[bdy_ind[rw][bdy_brk[rw][n] : bdy_brk[rw][n + 1]]])

    # loop over number of sections and plot

    f, ax = plt.subplots(nrows=1, ncols=1, figsize=(11, 4))
    ax.plot(dta[0][:])
    ax.set_title("BDY points along section: 1")

    f, ax = plt.subplots(nrows=nsc, ncols=1, figsize=(7, 5 * nsc))

    for n in range(nsc):
        if nsc > 1:
            nax = ax[n]
        else:
            nax = ax

        plt.sca(nax)

        # Add line to axes
        plt.plot(dta[n][:])
        plt.title(f"BDY points along section {n}")

    return f


def plot_bdy(fname, bdy_ind, bdy_dst, bdy_brk, varnam, t, rw=0):
    """
    Determine the ordering and breaks in BDY files to aid plotting.

    This function takes the i/j coordinates from BDY files and orders them sequentially
    making it easier to visualise sections along the open boundary. Breaks in the open
    boundary are also determined (i.e. where the distance between two points > 2**0.5)

    Args:
    ----
        fname     (str) : filename of BDY file

    Returns:
    -------
        bdy_ind   (dict): re-ordered indices
        bdy_dst   (dict): distance (in model coords) between points
        bdy_brk   (dict): location of the break points in the open boundary
    """
    # need to write in a check that either i or j are single values

    rootgrp = Dataset(fname, "r", format="NETCDF4")
    var = np.squeeze(rootgrp.variables[varnam][t, :])
    fv = rootgrp.variables[varnam]._FillValue
    mask = var == fv
    var = np.ma.MaskedArray(var, mask=mask)
    nbr = np.squeeze(rootgrp.variables["nbrdta"][:, :]) - 1
    if rw != 0:
        var = var[:, nbr == rw]

    # let us use gdept as the central depth irrespective of whether t, u or v
    if len(var.shape) == 2:
        section_flag = True
    elif len(var.shape) == 1:
        section_flag = False
    else:
        print(f"Not expecting var.shape = {var.shape}")

    try:
        gdep = np.squeeze(rootgrp.variables["deptht"][:, :, :])
    except KeyError:
        try:
            gdep = np.squeeze(rootgrp.variables["gdept"][:, :, :])
        except KeyError:
            try:
                gdep = np.squeeze(rootgrp.variables["depthu"][:, :, :])
            except KeyError:
                try:
                    gdep = np.squeeze(rootgrp.variables["depthv"][:, :, :])
                except KeyError:
                    print("depth variable not found")

    gdep[gdep == fv] = np.nan
    rootgrp.close()

    print(f"rimwidth {rw}")
    print(f"section_flag {section_flag}")

    if section_flag:
        f = process_plot_2d_sections(var, gdep, bdy_brk, bdy_ind, rw)

    else:
        f = process_plot_1d_sections(var, bdy_brk, bdy_ind, rw)
    return f


ind, dst, brk = nemo_bdy_order(str(sys.argv[1]))
f = plot_bdy(str(sys.argv[1]), ind, dst, brk, str(sys.argv[2]), 0, 0)
print(len(sys.argv))
if len(sys.argv) > 3:
    f.savefig(f"{str(sys.argv[3])}.png")
else:
    f.savefig("bdy_data.png")
