'''
Module to extract constituents for the input grid mapped onto output grid

@author: Mr. Srikanth Nagella
@author: thopri
'''

# pylint: disable=E1103
# pylint: disable=no-name-in-module
import copy
from . import tpxo_extract_HC
from . import fes_extract_HC
import numpy as np
from netCDF4 import Dataset
from pynemo import nemo_bdy_grid_angle
from pynemo.utils.nemo_bdy_lib import rot_rep
from pynemo.reader.factory import GetFile

import logging

def nemo_bdy_tide_rot(setup, DstCoord, Grid_T, Grid_U, Grid_V, comp,tide_model):
    """ Global Tidal model interpolation including rotation grid"""
    key_transport = 0 # compute the velocities from transport
    numharm = len(comp)
    logger = logging.getLogger(__name__)
    g_type = Grid_T.grid_type
    DC = copy.deepcopy(DstCoord)
    dst_lon = DC.bdy_lonlat[g_type]['lon'][Grid_T.bdy_r == 0]
    dst_lat = DC.bdy_lonlat[g_type]['lat'][Grid_T.bdy_r == 0]

    #nbdyz = len(Grid_T.bdy_i)
    nbdyu = len(np.where(Grid_U.bdy_r == 0)[0])
    nbdyv = len(np.where(Grid_V.bdy_r == 0)[0])

    # TODO: change from if statement defining HC extract to string passed that defines HC extract script
    #   e.g. pass 'tpxo' for tpxo_extract_HC.py or 'fes' fro fes_extract_HC.py. This will make easier to add new
    #   databases of HC

    #convert the dst_lon into TMD Conventions (0E/360E)
    dst_lon[dst_lon < 0.0] = dst_lon[dst_lon < 0.0]+360.0
    #extract the surface elevation at each z-point
    if tide_model == 'tpxo':
        tpxo_z = tpxo_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, g_type)
    if tide_model == 'fes':
        fes_z = fes_extract_HC.HcExtract(setup.settings,dst_lat,dst_lon,g_type)

    #convert back the z-longitudes into the usual conventions (-180E/+180E)
    dst_lon[dst_lon > 180.0] = dst_lon[dst_lon > 180.0]-360.0
    #check if elevation data are missing
    if tide_model == 'tpxo':
        ind = np.where((np.isnan(tpxo_z.amp)) | (np.isnan(tpxo_z.gph)))
    if tide_model == 'fes':
        ind = np.where((np.isnan(fes_z.amp)) | (np.isnan(fes_z.gph)))
    if ind[0].size > 0:
        logger.warning('Missing elveation along the open boundary')
    if tide_model == 'tpxo':
        ampz = tpxo_z.amp
        phaz = tpxo_z.gph
    if tide_model == 'fes':
        ampz = fes_z.amp
        phaz = fes_z.gph

    ampz[ind] = 0.0
    phaz[ind] = 0.0

    #extract U values of constituents
    dst_lon = DC.bdy_lonlat[Grid_U.grid_type]['lon'][Grid_U.bdy_r == 0]
    dst_lat = DC.bdy_lonlat[Grid_U.grid_type]['lat'][Grid_U.bdy_r == 0]

    #convert the U-longitudes into the TMD conventions (0/360E)
    dst_lon[dst_lon < 0.0] = dst_lon[dst_lon < 0.0]+360.0
    if tide_model == 'tpxo':
        tpxo_ux = tpxo_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_U.grid_type)
        tpxo_vx = tpxo_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_V.grid_type)

        ampuX = tpxo_ux.amp
        phauX = tpxo_ux.gph
        ampvX = tpxo_vx.amp
        phavX = tpxo_vx.gph

    if tide_model == 'fes':
        fes_ux = fes_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_U.grid_type)
        fes_vx = fes_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_V.grid_type)

        ampuX = fes_ux.amp
        phauX = fes_ux.gph
        ampvX = fes_vx.amp
        phavX = fes_vx.gph

        #check if ux data are missing
    ind = np.where((np.isnan(ampuX)) | (np.isnan(phauX)))
    if ind[0].size > 0:
        logger.warning('Missing zonal velocity along the x open boundary')
    ampuX[ind] = 0
    phauX[ind] = 0
    #check if ux data are missing
    ind = np.where((np.isnan(ampvX)) | (np.isnan(phavX)))
    if ind[0].size > 0:
        logger.warning('Missing zonal velocity along the x open boundary')
    ampvX[ind] = 0
    phavX[ind] = 0

    #convert back the u-longitudes into the usual conventions (-180E/+180E)
    dst_lon[dst_lon > 180.0] = dst_lon[dst_lon > 180.0]-360.0

    #extract V values of constituents
    dst_lon = DC.bdy_lonlat[Grid_V.grid_type]['lon'][Grid_V.bdy_r == 0]
    dst_lat = DC.bdy_lonlat[Grid_V.grid_type]['lat'][Grid_V.bdy_r == 0]

    #convert the U-longitudes into the TMD conventions (0/360E)
    dst_lon[dst_lon < 0.0] = dst_lon[dst_lon < 0.0]+360.0
    if tide_model == 'tpxo':
        tpxo_uy = tpxo_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_U.grid_type)
        tpxo_vy = tpxo_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_V.grid_type)

        ampuY = tpxo_uy.amp
        phauY = tpxo_uy.gph
        ampvY = tpxo_vy.amp
        phavY = tpxo_vy.gph

    if tide_model == 'fes':
        fes_uy = fes_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_U.grid_type)
        fes_vy = fes_extract_HC.HcExtract(setup.settings, dst_lat, dst_lon, Grid_V.grid_type)

        ampuY = fes_uy.amp
        phauY = fes_uy.gph
        ampvY = fes_vy.amp
        phavY = fes_vy.gph

    #check if ux data are missing
    ind = np.where((np.isnan(ampuY)) | (np.isnan(phauY)))
    if ind[0].size > 0:
        logger.warning('Missing zonal velocity along the x open boundary')
    ampuY[ind] = 0
    phauY[ind] = 0
    #check if ux data are missing
    ind = np.where((np.isnan(ampvY)) | (np.isnan(phavY)))
    if ind[0].size > 0:
        logger.warning('Missing zonal velocity along the x open boundary')
    ampvY[ind] = 0
    phavY[ind] = 0

    #convert back the u-longitudes into the usual conventions (-180E/+180E)
    dst_lon[dst_lon > 180.0] = dst_lon[dst_lon > 180.0]-360.0

    #extract the depths along the U-point open boundary
    zgr = GetFile(setup.settings['dst_zgr'])#Dataset(settings['dst_zgr'], 'r')
    mbathy = zgr['mbathy'][:,:,:].squeeze() #zgr.variables['mbathy'][:,:,:]

    #summing over scale factors as zps doesn't have hbat variable
    #e3X = zgr.variables['e3u']
    #e3X = np.squeeze(e3X)
    try: # Read in either 3D or 4D data. 
        e3X = zgr['e3u'][:,:,:].squeeze()
    except ValueError:
        e3X = zgr['e3u'][:,:,:,:].squeeze()
    if len(np.shape(e3X)) != 3:
        logger.warning('Expected a 3D array for e3u field')

    heightrange = np.arange(1, e3X.shape[0]+1)
    regular_heightprofile = np.tile(heightrange,
                                    e3X.shape[1]*e3X.shape[2]\
                                    ).reshape(heightrange.shape[0],
                                              e3X.shape[1],
                                              e3X.shape[2],
                                              order='F')
    ind = np.tile(mbathy, [e3X.shape[0], 1, 1]) >= regular_heightprofile

    # in u direction blank cells neighbouring T-point land as defined by mbathy
    ind[:, :, 1:] = ind[:, :, 0:-1] | ind[:, :, 1:]
    hbatX = np.sum(e3X*ind, 0)

    depu = np.zeros((1, Grid_U.bdy_i.shape[0]))
    for n in range(0, Grid_U.bdy_i.shape[0]):
        depu[0, n] = hbatX[Grid_U.bdy_i[n, 1], Grid_U.bdy_i[n, 0]]

    #extract the depths along the V-point open boundary
    #summing over scale factors as zps doesn't have hbat variable
    #e3X = zgr.variables['e3v']
    #e3X = np.squeeze(e3X)
    try: # Read in either 3D or 4D data. 
        e3X = zgr['e3v'][:,:,:].squeeze()
    except ValueError:
        e3X = zgr['e3v'][:,:,:,:].squeeze()
    if len(np.shape(e3X)) != 3:
        logger.warning('Expected a 3D array for e3v field')

    heightrange = np.arange(1, e3X.shape[0]+1)
    regular_heightprofile = np.tile(heightrange,
                                    e3X.shape[1]*e3X.shape[2]\
                                    ).reshape(heightrange.shape[0],
                                              e3X.shape[1],
                                              e3X.shape[2],
                                              order='F')
    ind = np.tile(mbathy, [e3X.shape[0], 1, 1]) >= regular_heightprofile

    # in u direction blank cells neighbouring T-point land as defined by mbathy
    ind[:, 1:, :] = ind[:, 0:-1, :] | ind[:, 1:, :]
    hbatX = np.sum(e3X*ind, 0)

    depv = np.zeros((1, Grid_V.bdy_i.shape[0]))
    for n in range(0, Grid_V.bdy_i.shape[0]):
        depv[0, n] = hbatX[Grid_V.bdy_i[n, 1], Grid_V.bdy_i[n, 0]]

    cosz = np.zeros((numharm, ampz.shape[1]))
    sinz = np.zeros((numharm, ampz.shape[1]))
    cosuX = np.zeros((numharm, nbdyu))
    sinuX = np.zeros((numharm, nbdyu))
    cosvX = np.zeros((numharm, nbdyu))
    sinvX = np.zeros((numharm, nbdyu))
    cosuY = np.zeros((numharm, nbdyv))
    sinuY = np.zeros((numharm, nbdyv))
    cosvY = np.zeros((numharm, nbdyv))
    sinvY = np.zeros((numharm, nbdyv))

    if tide_model == 'tpxo':
        compindx = constituents_index(tpxo_z.cons, comp)

    if tide_model == 'fes':
        compindx = constituents_index(fes_z.cons, comp)

    for h in range(0, numharm):
        c = int(compindx[h])
        if c != -1:
            cosz[h, :] = ampz[c, :] * np.cos(np.deg2rad(phaz[c, :]))
            sinz[h, :] = ampz[c, :] * np.sin(np.deg2rad(phaz[c, :]))

            if key_transport == 1:
                if (np.sum(depu[:] <= 0.0) > 0) | (np.sum(depv[:] <= 0.0) > 0):
                    logger.error(' Error: Land or Mask contamination')

                cosuX[h, :] = ampuX[c, :] * np.cos(np.deg2rad(phauX[c, :])) / depu
                sinuX[h, :] = ampuX[c, :] * np.sin(np.deg2rad(phauX[c, :])) / depu
                cosvX[h, :] = ampvX[c, :] * np.cos(np.deg2rad(phavX[c, :])) / depu
                sinvX[h, :] = ampvX[c, :] * np.sin(np.deg2rad(phavX[c, :])) / depu
                cosuY[h, :] = ampuY[c, :] * np.cos(np.deg2rad(phauY[c, :])) / depv
                sinuY[h, :] = ampuY[c, :] * np.sin(np.deg2rad(phauY[c, :])) / depv
                cosvY[h, :] = ampvY[c, :] * np.cos(np.deg2rad(phavY[c, :])) / depv
                sinvY[h, :] = ampvY[c, :] * np.sin(np.deg2rad(phavY[c, :])) / depv
            else:
                cosuX[h, :] = 0.01 * ampuX[c, :] * np.cos(np.deg2rad(phauX[c, :]))
                sinuX[h, :] = 0.01 * ampuX[c, :] * np.sin(np.deg2rad(phauX[c, :]))
                cosvX[h, :] = 0.01 * ampvX[c, :] * np.cos(np.deg2rad(phavX[c, :]))
                sinvX[h, :] = 0.01 * ampvX[c, :] * np.sin(np.deg2rad(phavX[c, :]))
                cosuY[h, :] = 0.01 * ampuY[c, :] * np.cos(np.deg2rad(phauY[c, :]))
                sinuY[h, :] = 0.01 * ampuY[c, :] * np.sin(np.deg2rad(phauY[c, :]))
                cosvY[h, :] = 0.01 * ampvY[c, :] * np.cos(np.deg2rad(phavY[c, :]))
                sinvY[h, :] = 0.01 * ampvY[c, :] * np.sin(np.deg2rad(phavY[c, :]))

# TOD:: Do we need to rotate ??? And is this method  correct ????
    maxJ = DC.lonlat['t']['lon'].shape[0]
    maxI = DC.lonlat['t']['lon'].shape[1]
    dst_gcos = np.ones([maxJ, maxI])
    dst_gsin = np.zeros([maxJ, maxI])
    #lets start with the u-points
    grid_angles = nemo_bdy_grid_angle.GridAngle(setup.settings['dst_hgr'], 0, maxI, 0, maxJ, 'u')
    dst_gcos = grid_angles.cosval
    dst_gsin = grid_angles.sinval

    #retain only boundary points rotation information
    tmp_gcos = np.zeros(len(np.where(Grid_U.bdy_r == 0)[0]))
    tmp_gsin = np.zeros(len(np.where(Grid_U.bdy_r == 0)[0]))

    bdy_r_in_i = Grid_U.bdy_i[Grid_U.bdy_r == 0]

    for index in range(len(np.where(Grid_U.bdy_r == 0)[0])):
        tmp_gcos[index] = dst_gcos[bdy_r_in_i[index, 1], bdy_r_in_i[index, 0]]
        tmp_gsin[index] = dst_gsin[bdy_r_in_i[index, 1], bdy_r_in_i[index, 0]]
    dst_gcos = tmp_gcos
    dst_gsin = tmp_gsin

    cosu = rot_rep(cosuX, cosvX, 'u', 'en to i', dst_gcos, dst_gsin)
    sinu = rot_rep(sinuX, sinvX, 'u', 'en to i', dst_gcos, dst_gsin)

    #let do the v points
    dst_gcos = np.ones([maxJ, maxI])
    dst_gsin = np.zeros([maxJ, maxI])
    grid_angles = nemo_bdy_grid_angle.GridAngle(setup.settings['dst_hgr'], 0, maxI, 0, maxJ, 'v')
    dst_gcos = grid_angles.cosval
    dst_gsin = grid_angles.sinval

    #retain only boundary points rotation information
    tmp_gcos = np.zeros(len(np.where(Grid_V.bdy_r == 0)[0]))
    tmp_gsin = np.zeros(len(np.where(Grid_V.bdy_r == 0)[0]))

    bdy_r_in_i = Grid_V.bdy_i[Grid_V.bdy_r == 0]

    for index in range(len(np.where(Grid_V.bdy_r == 0)[0])):
        tmp_gcos[index] = dst_gcos[bdy_r_in_i[index, 1], bdy_r_in_i[index, 0]]
        tmp_gsin[index] = dst_gsin[bdy_r_in_i[index, 1], bdy_r_in_i[index, 0]]
    dst_gcos = tmp_gcos
    dst_gsin = tmp_gsin

    cosv = rot_rep(cosuY, cosvY, 'v', 'en to j', dst_gcos, dst_gsin)
    sinv = rot_rep(sinuY, sinvY, 'v', 'en to j', dst_gcos, dst_gsin)

    #return the values
    cons = {}
    cons['cos'] = {'z':cosz,'u':cosu,'v':cosv}
    cons['sin'] = {'z':sinz,'u':sinu,'v':sinv}
    return cons


def constituents_index(constituents, inputcons):
    """
    Converts the input contituents to index in the tidal constituents.
    Inputs:     constituents: The list of constituents available from the source data
                        e.g. TPXO: ['m2', 's2', 'n2', 'k2', 'k1', 'o1', 'p1', 'q1', 'mf', 'mm', 'm4', 'ms4', 'mn4']
                inputcons: The dictionary of constituents from the namelist with their numbers 
                        e.g. {'1': "'M2'", '3': "'K2'", '2': "'S2'", '4': "'M4'"}
    Output:     retindx: The indices (relative to the source data list) of the dictionary items from the namelist
                        e.g. [  0.   3.   1.  10.]
    """
    retindx = np.zeros(len(inputcons))
    count = 0
    for value in list(inputcons.values()):
        const_name = value.replace("'", "").lower() # force inputcons entries to lowercase
        retindx[count] = [x.lower() for x in constituents].index(const_name) # force constituents to lowercase
        count = count+1
    return retindx
#    tpxo_z.Gph
#    tpxo_z.amp
