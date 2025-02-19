"""
Generate Depth information.

Written by John Kazimierz Farey, Sep 2012
Port of Matlab code of James Harle

# Generates depth points for t, u and v in one loop iteration

Initialise with bdy t, u and v grid attributes (Grid.bdy_i) and settings dictionary
"""

import logging

import numpy as np

from .reader.factory import GetFile
from .utils.nemo_bdy_lib import sub2ind

# Query name


def get_bdy_depths(bdy_t, bdy_u, bdy_v, DstCoord, settings):
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
