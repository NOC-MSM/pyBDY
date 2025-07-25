# ===================================================================
# Copyright 2025 National Oceanography Centre
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================

"""
Created.

@author John Kazimierz Farey
@author Benjamin Barton.
"""

# External imports
import logging

import numpy as np
import scipy.spatial as sp

# Local imports
from .reader.factory import GetFile
from .utils.nemo_bdy_lib import sub2ind


def get_bdy_depths_old(bdy_t, bdy_u, bdy_v, DstCoord, settings):
    """
    Generate Depth information.

    Written by John Kazimierz Farey, Sep 2012
    Port of Matlab code of James Harle

    Generates depth points for t, u and v in one loop iteration.
    Initialise with bdy t, u and v grid attributes (Grid.bdy_i) and settings dictionary.
    """
    logger = logging.getLogger(__name__)
    logger.debug("init Depth")
    hc = settings["hc"]
    nz = DstCoord.zgr.grid["gdept"].shape[1]  # number of depth levels

    # numpy requires float dtype to use NaNs
    mbathy = np.float16(DstCoord.zgr.grid["mbathy"].squeeze())
    mbathy[mbathy == 0] = np.NaN

    # Set up arrays
    t_nbdy = len(bdy_t[:, 0])
    u_nbdy = len(bdy_u[:, 0])
    v_nbdy = len(bdy_v[:, 0])
    zp = ["t", "wt", "u", "wu", "v", "wv"]
    zpoints = {}
    for z in zp:
        if "t" in z:
            nbdy = t_nbdy
        elif "u" in z:
            nbdy = u_nbdy
        elif "v" in z:
            nbdy = v_nbdy
        zpoints[z] = np.zeros((nz, nbdy))

    # Check inputs
    # FIX ME? Errors for wrong obj arg len. probably better to work around
    if settings["sco"]:
        # hc = ... FIX ME??
        nc = GetFile(settings["dst_zgr"])
        # Depth of water column at t-point
        hbatt = nc["hbatt"][:, :, :]  # nc.variables['hbatt'][:,:,:]
        # Replace land with NaN
        hbatt[mbathy == 0] = np.NaN
        nc.close()

    # find bdy indices from subscripts
    t_ind = sub2ind(mbathy.shape, bdy_t[:, 0], bdy_t[:, 1])

    u_ind = sub2ind(mbathy.shape, bdy_u[:, 0], bdy_u[:, 1])
    u_ind2 = sub2ind(mbathy.shape, bdy_u[:, 0] + 1, bdy_u[:, 1])

    v_ind = sub2ind(mbathy.shape, bdy_v[:, 0], bdy_v[:, 1])
    v_ind2 = sub2ind(mbathy.shape, bdy_v[:, 0], bdy_v[:, 1] + 1)

    # This is very slow
    logger.debug("starting nc reads loop")
    for k in range(nz):
        if settings["sco"]:
            nc = GetFile(settings["dst_zgr"])
            # sigma coeffs at t-point (1->0 indexed)
            gsigt = nc["gsigt"][0, k, :, :]  # nc.variables['gsigt'][0,k,:,:]
            # sigma coeffs at w-point
            gsigw = nc["gsigw"][0, k, :, :]  # nc.variables['gsigw'][0,k,:,:]
            nc.close()

            # NOTE:  check size of gsigt SKIPPED

            wrk1 = (hbatt - hc) * gsigt[:, :] + (hc * (k + 0.5) / (nz - 1))
            wrk2 = (hbatt - hc) * gsigw[:, :] + (hc * (k + 0.5) / (nz - 1))
        else:
            wrk1 = np.squeeze(DstCoord.zgr.grid["gdept"])[k, :, :]
            wrk2 = np.squeeze(DstCoord.zgr.grid["gdepw"])[k, :, :]

        # Replace deep levels that are not used with NaN
        wrk2[mbathy + 1 < k + 1] = np.NaN
        wrk1[mbathy < k + 1] = np.NaN

        # Set u and v grid point depths
        zshapes = {}
        for p in list(zpoints.keys()):
            zshapes[p] = zpoints[p].shape

        wrk1, wrk2 = wrk1.flatten("F"), wrk2.flatten("F")

        zpoints["t"][k, :] = wrk1[t_ind]
        zpoints["wt"][k, :] = wrk2[t_ind]

        zpoints["u"][k, :] = 0.5 * (wrk1[u_ind] + wrk1[u_ind2])
        zpoints["wu"][k, :] = 0.5 * (wrk2[u_ind] + wrk2[u_ind2])

        zpoints["v"][k, :] = 0.5 * (wrk1[v_ind] + wrk1[v_ind2])
        zpoints["wv"][k, :] = 0.5 * (wrk2[v_ind] + wrk2[v_ind2])

        for p in list(zpoints.keys()):
            zpoints[p] = zpoints[p].reshape(zshapes[p])

    logger.debug("Done loop, zpoints: %s ", zpoints["t"].shape)
    return zpoints


def get_bdy_depths(DstCoord, bdy_i, grd):
    """
    Depth levels on the destination grid at bdy points.

    Parameters
    ----------
        DstCoord (object)      : Object containing destination grid info
        bdy_i (np.array)       : indices of the i, j bdy points [bdy, 2]
        grd (str)              : grid type t, u, v

    Returns
    -------
        bdy_tz (array)          : sc depths on bdy points on t levels
        bdy_wz (array)          : sc depths on bdy points on w levels
        bdy_e3 (array)          : sc level thickness on bdy points on t levels
    """
    # numpy requires float dtype to use NaNs
    mbathy = np.float16(DstCoord.zgr.grid["mbathy"].squeeze())
    mbathy[mbathy == 0] = np.NaN

    if grd == "t":
        g = ""
    elif grd == "u":
        g = grd
    elif grd == "v":
        g = grd

    # find bdy indices from subscripts
    g_ind = sub2ind(mbathy.shape, bdy_i[:, 0], bdy_i[:, 1])

    # Get the gdept, gdepw and e3 data from the Dst grid
    m_w = np.ma.array(np.squeeze(DstCoord.zgr.grid["gdep" + g + "w"]))
    m_t = np.ma.array(np.squeeze(DstCoord.zgr.grid["gdep" + grd]))
    m_e = np.ma.array(np.squeeze(DstCoord.zgr.grid["e3" + grd]))

    bdy_wz = np.ma.zeros((m_w.shape[0], len(g_ind)))
    bdy_tz = np.ma.zeros((m_t.shape[0], len(g_ind)))
    bdy_e3 = np.ma.zeros((m_e.shape[0], len(g_ind)))
    for k in range(m_w.shape[0]):
        tmp_w = np.ma.masked_where(mbathy + 1 < k + 1, m_w[k, :, :])
        tmp_t = np.ma.masked_where(mbathy < k + 1, m_t[k, :, :])
        tmp_e = np.ma.masked_where(mbathy < k + 1, m_e[k, :, :])

        tmp_w = tmp_w.flatten("F")
        tmp_t = tmp_t.flatten("F")
        tmp_e = tmp_e.flatten("F")

        bdy_wz[k, :] = tmp_w[g_ind]
        bdy_tz[k, :] = tmp_t[g_ind]
        bdy_e3[k, :] = tmp_e[g_ind]

    return bdy_tz, bdy_wz, bdy_e3


def get_bdy_sc_depths(SourceCoord, DstCoord, grd):
    """
    Depth levels from the nearest neighbour on the source grid.

    Parameters
    ----------
        SourceCoord (object)   : Object containing source grid info
        DstCoord (object)      : Object containing destination grid info
        grd (str)              : grid type t, u, v

    Returns
    -------
        bdy_tz (array)          : sc depths on bdy points on t levels
        bdy_wz (array)          : sc depths on bdy points on w levels
        bdy_e3 (array)          : sc level thickness on bdy points on t levels
    """
    if grd == "t":
        g = ""
    else:
        g = grd

    source_tree = sp.cKDTree(
        list(
            zip(
                np.ravel(np.squeeze(SourceCoord.hgr.grid["glamt"])),
                np.ravel(np.squeeze(SourceCoord.hgr.grid["gphit"])),
            )
        )
    )
    dst_pts = list(
        zip(DstCoord.bdy_lonlat[grd]["lon"], DstCoord.bdy_lonlat[grd]["lat"])
    )
    nn_dist, nn_id = source_tree.query(dst_pts, k=1)

    mbathy = np.float16(SourceCoord.zgr.grid["mbathy"].squeeze())
    mbathy[mbathy == 0] = np.NaN

    tmp_w = np.ma.array(np.squeeze(SourceCoord.zgr.grid["gdep" + g + "w"]))
    tmp_t = np.ma.array(np.squeeze(SourceCoord.zgr.grid["gdep" + grd]))
    tmp_e = np.ma.array(np.squeeze(SourceCoord.zgr.grid["e3" + grd]))
    for k in range(tmp_w.shape[0]):
        tmp_w[k, :, :] = np.ma.masked_where(mbathy + 1 < k + 1, tmp_w[k, :, :])
        tmp_t[k, :, :] = np.ma.masked_where(mbathy + 1 < k + 1, tmp_t[k, :, :])
        tmp_e[k, :, :] = np.ma.masked_where(mbathy + 1 < k + 1, tmp_e[k, :, :])

    bdy_wz = np.ma.zeros((tmp_w.shape[0], len(nn_id)))
    bdy_tz = np.ma.zeros((tmp_t.shape[0], len(nn_id)))
    bdy_e3 = np.ma.zeros((tmp_e.shape[0], len(nn_id)))
    for k in range(bdy_wz.shape[0]):
        bdy_wz[k, :] = np.ravel(tmp_w[k, :, :])[nn_id]
        bdy_tz[k, :] = np.ravel(tmp_t[k, :, :])[nn_id]
        bdy_e3[k, :] = np.ravel(tmp_e[k, :, :])[nn_id]

    return bdy_tz, bdy_wz, bdy_e3
