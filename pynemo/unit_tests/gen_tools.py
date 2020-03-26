# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 11:16:57 2020

unit test grid generation tools

@author: thopri and jdha (for example code)

"""
from netCDF4 import Dataset
from math import cos,sin,radians
import numpy as np
import matplotlib.pyplot as plt
from math import radians


def set_hgrid(dx, dy, jpi, jpj, zoffx=0, zoffy=0,sf=1):
    if sf > 1:
        jpi = int(jpj - (jpi/sf))+1
        jpj = int(jpj -(jpj/sf))+1
    # Set grid positions [km]
    latt = np.zeros((jpi, jpj))
    lont = np.zeros((jpi, jpj))
    lonu = np.zeros((jpi, jpj))
    latu = np.zeros((jpi, jpj))
    lonv = np.zeros((jpi, jpj))
    latv = np.zeros((jpi, jpj))
    lonf = np.zeros((jpi, jpj))
    latf = np.zeros((jpi, jpj))

    for i in range(0, jpi):
        lont[i, :] = zoffx * dx * 1.e-3 + dx * 1.e-3 * np.float(i)
        lonu[i, :] = zoffx * dx * 1.e-3 + dx * 1.e-3 * (np.float(i) + 0.5)

    for j in range(0, jpj):
        latt[:, j] = zoffy * dy * 1.e-3 + dy * 1.e-3 * float(j)
        latv[:, j] = zoffy * dy * 1.e-3 + dy * 1.e-3 * (float(j) + 0.5)

    lonv = lont
    lonf = lonu
    latu = latt
    latf = latv

    e1t = np.ones((jpi, jpj)) * dx
    e2t = np.ones((jpi, jpj)) * dy
    e1u = np.ones((jpi, jpj)) * dx
    e2u = np.ones((jpi, jpj)) * dy
    e1v = np.ones((jpi, jpj)) * dx
    e2v = np.ones((jpi, jpj)) * dy
    e1f = np.ones((jpi, jpj)) * dx
    e2f = np.ones((jpi, jpj)) * dy

    # Set bathymetry [m]:
    batt = 500. + 0.5 * 1500. * (1.0 + np.tanh((lont - 40.) / 7.))

    # Set surface mask:
    ktop = np.zeros((jpi, jpj))
    #ktop[1:jpi - 1, nghost + 1:jpj - nghost - 1] = 1
    #batt = np.where((ktop == 0.), 0., batt)

    # Set coriolis parameter:
    ff_t = np.zeros((jpi, jpj))
    ff_f = np.zeros((jpi, jpj))

    grid_h = {'lont':lont, 'latt':latt, 'lonu':lonu, 'latu':latu, 'lonv':lonv, 'latv':latv, 'lonf':lonf, 'latf':latf, \
           'e1t':e1t, 'e2t':e2t, 'e1u':e1u, 'e2u':e2u, 'e1v':e1v, 'e2v':e2v, 'e1f':e1f, 'e2f':e2f, 'batt':batt, \
              'ktop':ktop, 'ff_f':ff_f, 'ff_t':ff_t,'jpi':jpi,'jpj':jpj,'dy':dy,'dx':dx}

    return grid_h

def set_zgrid(grid_h,jpk,max_dep,min_dep,z_dim):

    jpi = grid_h['jpi']
    jpj = grid_h['jpj']

    dept_1d = np.linspace(min_dep,max_dep,jpk)
    e3t_1d = np.linspace(1.0,z_dim,jpk)
    e3w_1d = np.linspace(1.0,z_dim,jpk)
    gdept_0 = np.linspace(min_dep,max_dep,jpk)
    gdepw_0 = np.linspace(min_dep,max_dep,jpk)

    e3t = np.zeros((jpi, jpj, len(e3t_1d)))
    e3u = np.zeros((jpi, jpj, len(e3t_1d)))
    e3v = np.zeros((jpi, jpj, len(e3t_1d)))
    e3w = np.zeros((jpi, jpj, len(e3w_1d)))
    e3f = np.zeros((jpi, jpj, len(e3t_1d)))
    e3uw = np.zeros((jpi, jpj, len(e3t_1d)))
    e3vw = np.zeros((jpi, jpj, len(e3t_1d)))
    gdept = np.zeros((jpi,jpj,len(gdept_0)))
    gdepw = np.zeros((jpi,jpj,len(gdepw_0)))

    e3t[:] = e3t_1d
    e3u[:] = e3t_1d
    e3v[:] = e3t_1d
    e3w[:] = e3w_1d
    e3f[:] = e3t_1d
    e3uw[:] = e3t_1d
    e3vw[:] = e3t_1d
    gdept[:] = gdept_0
    gdepw[:] = gdepw_0

    grid_z = {'dept_1d':dept_1d,'e3t_1d':e3t_1d,'e3w_1d':e3w_1d,'e3t':e3t,'e3u':e3u,'e3v':e3v,'e3w':e3w,'e3f':e3f, \
              'e3uw':e3uw,'e3vw':e3vw,'gdept_0':gdept_0,'gdept':gdept,'gdepw_0':gdepw_0,'gdepw':gdepw}

    return grid_z

def write_coord_H(fileout, grid_h):
    '''
    Writes out a NEMO formatted coordinates file.

    Args:
        fileout         (string): filename
        lon[t/u/v/f](np.ndarray): longitude array at [t/u/v/f]-points (2D)
        lat[t/u/v/f](np.ndarray): latitude array at [t/u/v/f]-points (2D)
        e1[t/u/v/f] (np.ndarray): zonal scale factors at [t/u/v/f]-points
        e2[t/u/v/f] (np.ndarray): meridional scale factors at [t/u/v/f]-points

    Returns:
    '''

    # Open pointer to netcdf file
    dataset = Dataset(fileout, 'w', format='NETCDF4_CLASSIC')

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nx, ny = np.shape(grid_h['lont'])
    nt = 1
    dataset.createDimension('x', nx)
    dataset.createDimension('y', ny)
    dataset.createDimension('t', nt)

    # Create Variables
    nav_lon = dataset.createVariable('nav_lon', np.float32, ('y', 'x'))
    nav_lat = dataset.createVariable('nav_lat', np.float32, ('y', 'x'))
    time_counter = dataset.createVariable('time_counter',np.float32,('t'))

    glamt = dataset.createVariable('glamt', np.float64, ('t','y', 'x'))
    glamu = dataset.createVariable('glamu', np.float64, ('t','y', 'x'))
    glamv = dataset.createVariable('glamv', np.float64, ('t','y', 'x'))
    glamf = dataset.createVariable('glamf', np.float64, ('t','y', 'x'))
    gphit = dataset.createVariable('gphit', np.float64, ('t','y', 'x'))
    gphiu = dataset.createVariable('gphiu', np.float64, ('t','y', 'x'))
    gphiv = dataset.createVariable('gphiv', np.float64, ('t','y', 'x'))
    gphif = dataset.createVariable('gphif', np.float64, ('t','y', 'x'))

    ge1t = dataset.createVariable('e1t', np.float64, ('t','y', 'x'))
    ge1u = dataset.createVariable('e1u', np.float64, ('t','y', 'x'))
    ge1v = dataset.createVariable('e1v', np.float64, ('t','y', 'x'))
    ge1f = dataset.createVariable('e1f', np.float64, ('t','y', 'x'))
    ge2t = dataset.createVariable('e2t', np.float64, ('t','y', 'x'))
    ge2u = dataset.createVariable('e2u', np.float64, ('t','y', 'x'))
    ge2v = dataset.createVariable('e2v', np.float64, ('t','y', 'x'))
    ge2f = dataset.createVariable('e2f', np.float64, ('t','y', 'x'))

    nav_lon.units, nav_lon.long_name = 'km', 'X'
    nav_lat.units, nav_lat.long_name = 'km', 'Y'
    time_counter.units, time_counter.long_name = 'seconds','time_counter'

    # Populate file with input data
    # TODO: do we need to transpose?
    nav_lon[:, :] = grid_h['lont'].T
    nav_lat[:, :] = grid_h['latt'].T

    glamt[:, :] = grid_h['lont'].T
    glamu[:, :] = grid_h['lonu'].T
    glamv[:, :] = grid_h['lonv'].T
    glamf[:, :] = grid_h['lonf'].T
    gphit[:, :] = grid_h['latt'].T
    gphiu[:, :] = grid_h['latu'].T
    gphiv[:, :] = grid_h['latv'].T
    gphif[:, :] = grid_h['latf'].T

    ge1t[:, :] = grid_h['e1t'].T
    ge1u[:, :] = grid_h['e1u'].T
    ge1v[:, :] = grid_h['e1v'].T
    ge1f[:, :] = grid_h['e1f'].T
    ge2t[:, :] = grid_h['e2t'].T
    ge2u[:, :] = grid_h['e2u'].T
    ge2v[:, :] = grid_h['e2v'].T
    ge2f[:, :] = grid_h['e2f'].T

    # Close off pointer
    dataset.close()

    return 0

def write_coord_Z(fileout, grid_h,grid_z):
    '''
    Writes out a NEMO formatted coordinates file.

    Args:

    Returns:
    '''

    # Open pointer to netcdf file
    dataset = Dataset(fileout, 'w', format='NETCDF4_CLASSIC')

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nx, ny, nz = np.shape(grid_z['e3t'])
    nt = 1
    dataset.createDimension('x', nx)
    dataset.createDimension('y', ny)
    dataset.createDimension('z', nz)
    dataset.createDimension('t', nt)


    # Create Variables
    nav_lon = dataset.createVariable('nav_lon', np.float32, ('y', 'x'))
    nav_lat = dataset.createVariable('nav_lat', np.float32, ('y', 'x'))
    nav_lev = dataset.createVariable('nav_lev', np.float32, 'z')
    time_counter = dataset.createVariable('time_counter', np.float32, ('t'))

    ge3t1d = dataset.createVariable('e3t_0', np.float64, ('t','z'))
    ge3w1d = dataset.createVariable('e3w_0', np.float64, ('t','z'))
    gdept_0 = dataset.createVariable('gdept_0', np.float64, ('t','z'))
    gdepw_0 = dataset.createVariable('gdepw_0', np.float64, ('t','z'))
    gbat = dataset.createVariable('mbathy', np.float64, ('t','y', 'x'))
    ge3t = dataset.createVariable('e3t', np.float64, ('t','z','y', 'x'))
    ge3u = dataset.createVariable('e3u', np.float64, ('t','z','y', 'x'))
    ge3v = dataset.createVariable('e3v', np.float64, ('t','z','y', 'x'))
    ge3w = dataset.createVariable('e3w', np.float64, ('t', 'z', 'y', 'x'))
    ge3f = dataset.createVariable('e3f', np.float64, ('t','z','y', 'x'))
    ge3uw = dataset.createVariable('e3uw', np.float64, ('t','z', 'y', 'x'))
    ge3vw = dataset.createVariable('e3vw', np.float64, ('t','z', 'y', 'x'))
    gdept = dataset.createVariable('gdept', np.float64, ('t','z', 'y', 'x'))
    gdepw = dataset.createVariable('gdepw', np.float64, ('t','z', 'y', 'x'))

    nav_lon.units, nav_lon.long_name = 'km', 'X'
    nav_lat.units, nav_lat.long_name = 'km', 'Y'
    nav_lev.units, nav_lev.long_name = 'm', 'Z'
    time_counter.units, time_counter.long_name = 'seconds', 'time_counter'

    # Populate file with input data
    # TODO: do we need to transpose?
    nav_lon[:, :] = grid_h['lont'].T
    nav_lat[:, :] = grid_h['latt'].T
    nav_lev[:] = grid_z['dept_1d']

    ge3t[:, :, :] = grid_z['e3t'].T
    ge3u[:, :, :] = grid_z['e3u'].T
    ge3v[:, :, :] = grid_z['e3v'].T
    ge3f[:, :, :] = grid_z['e3f'].T
    ge3w[:, :, :] = grid_z['e3w'].T
    ge3uw[:, :, :] = grid_z['e3uw'].T
    ge3vw[:, :, :] = grid_z['e3vw'].T

    ge3t1d[:] = grid_z['e3t_1d']
    ge3w1d[:] = grid_z['e3w_1d']
    gbat[:,:] = grid_h['batt'].T
    gdept[:,:,:] = grid_z['gdept'].T
    gdept_0[:] = grid_z['gdept_0']
    gdepw[:,:,:] = grid_z['gdepw'].T
    gdepw_0[:] = grid_z['gdepw_0']


    # Close off pointer
    dataset.close()

    return 0

# def write_domcfg(fileout, ln_zco, ln_zps, ln_sco, ln_isfcav, jperio, bat,
#                  lont, latt, lonu, latu, lonv, latv, lonf, latf,
#                  e1t, e2t, e1u, e2u, e1v, e2v, e1f, e2f, ff_f, ff_t,
#                  dept_1d, e3t_1d, e3w_1d, e3t, e3u, e3v, e3f, e3w, e3uw, e3vw,
#                  ktop, kbot):
#     '''
#     Writes out a NEMO formatted domcfg file.
#
#     Args:
#         fileout         (string): filename
#         ln_zco         (logical): vertical coordinate flag [z-level]
#         ln_zps         (logical): vertical coordinate flag [z-partial-step]
#         ln_sco         (logical): vertical coordinate flag [sigma]
#         ln_isfcav      (logical): ice cavity flag
#         jperio             (int): domain type
#         bat         (np.ndarray): bathymetry array at t-points (2D)
#         lon[t/u/v/f](np.ndarray): longitude array at [t/u/v/f]-points (2D)
#         lat[t/u/v/f](np.ndarray): latitude array at [t/u/v/f]-points (2D)
#         e1[t/u/v/f] (np.ndarray): zonal scale factors at [t/u/v/f]-points
#         e2[t/u/v/f] (np.ndarray): meridional scale factors at [t/u/v/f]-points
#         ff_[f/t]    (np.ndarray): coriolis parameter at [t/f]-points
#         dept_1d     (np.ndarray): 1D depth levels at t-points
#         e3[t/w]_1d  (np.ndarray): 1D vertical scale factors at [t/w]-points
#         e3[t/u/v/f] (np.ndarray): vertcal scale factors at [t/u/v/f]-points
#         e3[w/uw/vw] (np.ndarray): vertcal scale factors at [w/uw/vw]-points
#         ktop        (np.ndarray): upper most wet point
#         kbot        (np.ndarray): lower most wet point
#
#     Returns:
#     '''
#
#     # Open pointer to netcdf file
#     dataset = Dataset(fileout, 'w', format='NETCDF4_CLASSIC')
#
#     # Get input size and create appropriate dimensions
#     # TODO: add some sort of error handling
#     nx, ny, nz = np.shape(e3t)
#     dataset.createDimension('x', nx)
#     dataset.createDimension('y', ny)
#     dataset.createDimension('z', nz)
#
#     # create Variables
#     nav_lon = dataset.createVariable('nav_lon', np.float32, ('y', 'x'))
#     nav_lat = dataset.createVariable('nav_lat', np.float32, ('y', 'x'))
#     nav_lev = dataset.createVariable('nav_lev', np.float32, 'z')
#
#     giglo = dataset.createVariable('jpiglo', "i4")
#     gjglo = dataset.createVariable('jpjglo', "i4")
#     gkglo = dataset.createVariable('jpkglo', "i4")
#
#     gperio = dataset.createVariable('jperio', "i4")
#
#     gzco = dataset.createVariable('ln_zco', "i4")
#     gzps = dataset.createVariable('ln_zps', "i4")
#     gsco = dataset.createVariable('ln_sco', "i4")
#     gcav = dataset.createVariable('ln_isfcav', "i4")
#
#     ge3t1d = dataset.createVariable('e3t_1d', np.float64, 'z')
#     ge3w1d = dataset.createVariable('e3w_1d', np.float64, 'z')
#     gitop = dataset.createVariable('top_level', "i4", ('y', 'x'))
#     gibot = dataset.createVariable('bottom_level', "i4", ('y', 'x'))
#     gbat = dataset.createVariable('Bathymetry', np.float64, ('y', 'x'))
#     glamt = dataset.createVariable('glamt', np.float64, ('y', 'x'))
#     glamu = dataset.createVariable('glamu', np.float64, ('y', 'x'))
#     glamv = dataset.createVariable('glamv', np.float64, ('y', 'x'))
#     glamf = dataset.createVariable('glamf', np.float64, ('y', 'x'))
#     gphit = dataset.createVariable('gphit', np.float64, ('y', 'x'))
#     gphiu = dataset.createVariable('gphiu', np.float64, ('y', 'x'))
#     gphiv = dataset.createVariable('gphiv', np.float64, ('y', 'x'))
#     gphif = dataset.createVariable('gphif', np.float64, ('y', 'x'))
#     ge1t = dataset.createVariable('e1t', np.float64, ('y', 'x'))
#     ge1u = dataset.createVariable('e1u', np.float64, ('y', 'x'))
#     ge1v = dataset.createVariable('e1v', np.float64, ('y', 'x'))
#     ge1f = dataset.createVariable('e1f', np.float64, ('y', 'x'))
#     ge2t = dataset.createVariable('e2t', np.float64, ('y', 'x'))
#     ge2u = dataset.createVariable('e2u', np.float64, ('y', 'x'))
#     ge2v = dataset.createVariable('e2v', np.float64, ('y', 'x'))
#     ge2f = dataset.createVariable('e2f', np.float64, ('y', 'x'))
#     gfff = dataset.createVariable('ff_f', np.float64, ('y', 'x'))
#     gfft = dataset.createVariable('ff_t', np.float64, ('y', 'x'))
#     ge3t = dataset.createVariable('e3t_0', np.float64, ('z', 'y', 'x'))
#     ge3w = dataset.createVariable('e3w_0', np.float64, ('z', 'y', 'x'))
#     ge3u = dataset.createVariable('e3u_0', np.float64, ('z', 'y', 'x'))
#     ge3v = dataset.createVariable('e3v_0', np.float64, ('z', 'y', 'x'))
#     ge3f = dataset.createVariable('e3f_0', np.float64, ('z', 'y', 'x'))
#     ge3uw = dataset.createVariable('e3uw_0', np.float64, ('z', 'y', 'x'))
#     ge3vw = dataset.createVariable('e3vw_0', np.float64, ('z', 'y', 'x'))
#
#     nav_lon.units, nav_lon.long_name = 'km', 'X'
#     nav_lat.units, nav_lat.long_name = 'km', 'Y'
#
#     # Populate file with input data
#     giglo[:] = nx
#     gjglo[:] = ny
#     gkglo[:] = nz
#
#     gzco[:] = ln_zco
#     gzps[:] = ln_zps
#     gsco[:] = ln_sco
#     gcav[:] = ln_isfcav
#
#     gperio[:] = jperio
#
#     # TODO: do we need to transpose?
#     nav_lon[:, :] = lont.T
#     nav_lat[:, :] = latt.T
#     nav_lev[:] = dept_1d
#
#     ge3t1d[:] = e3t_1d
#     ge3w1d[:] = e3w_1d
#
#     gitop[:, :] = ktop.T
#     gibot[:, :] = kbot.T
#
#     gbat[:, :] = bat.T
#
#     glamt[:, :] = lont.T
#     glamu[:, :] = lonu.T
#     glamv[:, :] = lonv.T
#     glamf[:, :] = lonf.T
#     gphit[:, :] = latt.T
#     gphiu[:, :] = latu.T
#     gphiv[:, :] = latv.T
#     gphif[:, :] = latf.T
#
#     ge1t[:, :] = e1t.T
#     ge1u[:, :] = e1u.T
#     ge1v[:, :] = e1v.T
#     ge1f[:, :] = e1f.T
#     ge2t[:, :] = e2t.T
#     ge2u[:, :] = e2u.T
#     ge2v[:, :] = e2v.T
#     ge2f[:, :] = e2f.T
#     gfff[:, :] = ff_f.T
#     gfft[:, :] = ff_t.T
#
#     ge3t[:, :, :] = e3t.T
#     ge3w[:, :, :] = e3w.T
#     ge3u[:, :, :] = e3u.T
#     ge3v[:, :, :] = e3v.T
#     ge3f[:, :, :] = e3f.T
#     ge3uw[:, :, :] = e3uw.T
#     ge3vw[:, :, :] = e3vw.T
#
#     # Close off pointer
#     dataset.close()

def rotate_around_point(lat_in,lon_in, radians , origin=(0, 0)):
    """Rotate a point around a given point.
    """
    # create empty lat and lon arrays that match input
    new_lon = np.zeros(np.shape(lon_in))
    new_lat = np.zeros(np.shape(lat_in))
    # extract origin lat and lon as offset
    offset_lat, offset_lon = origin
    cos_rad = cos(radians)
    sin_rad = sin(radians)
    # cycle through lat and lon arrays and calcule new lat and lon values based on rotation
    # and origin values
    for indx in range(np.shape(lat_in)[0]):
        for indy in range(np.shape(lon_in)[1]):
            adjusted_lat = (lat_in[indx,indy] - offset_lat)
            adjusted_lon = (lon_in[indx,indy] - offset_lon)
            new_lat[indx,indy] = offset_lat + cos_rad * adjusted_lat + -sin_rad * adjusted_lon
            new_lon[indx,indy] = offset_lon + sin_rad * adjusted_lat + cos_rad * adjusted_lon

    return new_lat, new_lon

def plot_grids(lat_in,lon_in,new_lat,new_lon,off_lat,off_lon,src_lat,src_lon):

    # define lat and lon extents (define in future using input values?)
    #maxlat = 72
    #minlat = 32
    #maxlon = 18
    #minlon = -28

    plt.figure(figsize=[18, 18])  # a new figure window

    ax = plt.subplot(221)#, projection=ccrs.PlateCarree())  # specify (nrows, ncols, axnum)
    #ax.set_extent([minlon,maxlon,minlat,maxlat],crs=ccrs.PlateCarree()) #set extent
    #ax.set_title('Original Grid', fontsize=20,y=1.05) #set title
    #ax.add_feature(cartopy.feature.LAND, zorder=0)  # add land polygon
    #ax.add_feature(cartopy.feature.COASTLINE, zorder=10)  # add coastline polyline
    #gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='black', alpha=0.5, linestyle='--', draw_labels=True)

    ax1 = plt.subplot(222)#, projection=ccrs.PlateCarree())  # specify (nrows, ncols, axnum)
    #ax1.set_extent([minlon,maxlon,minlat,maxlat],crs=ccrs.PlateCarree()) #set extent
    #ax1.set_title('Rotated Grid', fontsize=20,y=1.05) #set title
    #ax1.add_feature(cartopy.feature.LAND, zorder=0)  # add land polygon
    #ax1.add_feature(cartopy.feature.COASTLINE, zorder=10)  # add coastline polyline
    #gl1 = ax1.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='black', alpha=0.5, linestyle='--', draw_labels=True)

    # tile 1D lat and lon to 2D arrays for plotting (src lat and lon only)
    #src_lon = np.tile(src_lon, (np.shape(src_lat)[0], 1))
    #src_lat = np.tile(src_lat, (np.shape(src_lon)[1], 1))
    #src_lat = np.rot90(src_lat)

    ax2 = plt.subplot(223)
    ax3 = plt.subplot(224)

    # plot lat and lon for all grids
    ax.plot(lon_in, lat_in, color='blue', marker='.', linestyle="")
    ax.plot(src_lon,src_lat, color='green', marker='o', linestyle="")
    ax1.plot(new_lon,new_lat, color='red', marker='.', linestyle="")
    ax1.plot(src_lon,src_lat, color='green',marker='o',linestyle="")
    ax2.plot(off_lon,off_lat, color='yellow',marker='.',linestyle="")
    ax2.plot(src_lon, src_lat, color='green', marker='o', linestyle="")
    # tweak margins of subplots as tight layout doesn't work for some reason?
    plt.subplots_adjust(left=0.01, right=1, top=0.9, bottom=0.05,wspace=0.01)

    plt.show()

def write_mask(fileout,grid_h,grid_z):
    '''
    Writes out a

    Args:

    Returns:
    '''
    # Open pointer to netcdf file
    dataset = Dataset(fileout, 'w', format='NETCDF4_CLASSIC')

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nt = 1
    nx, ny, nz = np.shape(grid_z['e3t'])
    dataset.createDimension('x', nx)
    dataset.createDimension('y', ny)
    dataset.createDimension('z', nz)
    dataset.createDimension('t', nt)
    # Create Variables
    nav_lon = dataset.createVariable('nav_lon', np.float32, ('y', 'x'))
    nav_lat = dataset.createVariable('nav_lat', np.float32, ('y', 'x'))
    nav_lev = dataset.createVariable('nav_lev', np.float32, 'z')
    time_counter = dataset.createVariable('time_counter', np.float32, ('t'))

    fmaskutil = dataset.createVariable('fmaskutil', np.float64, ('t','y', 'x'))
    tmaskutil = dataset.createVariable('tmaskutil', np.float64, ('t','y', 'x'))
    umaskutil = dataset.createVariable('umaskutil', np.float64, ('t','y', 'x'))
    vmaskutil = dataset.createVariable('vmaskutil', np.float64, ('t','y', 'x'))

    fmask = dataset.createVariable('fmask', np.float64, ('t','z','y', 'x'))
    tmask = dataset.createVariable('tmask', np.float64, ('t','z','y', 'x'))
    umask = dataset.createVariable('umask', np.float64, ('t','z','y', 'x'))
    vmask = dataset.createVariable('vmask', np.float64, ('t','z','y', 'x'))

    nav_lon.units, nav_lon.long_name = 'km', 'X'
    nav_lat.units, nav_lat.long_name = 'km', 'Y'
    nav_lev.units, nav_lev.long_name = 'm', 'Z'
    time_counter.units, time_counter.long_name = 'seconds', 'time_counter'

    # Populate file with input data
    # TODO: do we need to transpose?
    nav_lon[:, :] = grid_h['lont'].T
    nav_lat[:, :] = grid_h['latt'].T
    nav_lev[:] = grid_z['dept_1d']

    threeD_mask = np.ones(np.shape(grid_z['e3t']))
    twoD_mask = np.ones(np.shape(grid_h['e1t']))

    fmask[:,:,:] = threeD_mask.T
    fmaskutil[:,:] = twoD_mask.T
    tmask[:,:,:] = threeD_mask.T
    tmaskutil[:,:] = twoD_mask.T
    umask[:,:,:] = threeD_mask.T
    umaskutil[:,:] = twoD_mask.T
    vmask[:,:,:] = threeD_mask.T
    vmaskutil[:,:] = twoD_mask.T

    dataset.close()

    return 0

def write_parameter(fileout, grid_h,grid_z,params,grid):
    '''
    Writes out a

    Args:

    Returns:
    '''

    # Open pointer to netcdf file
    dataset = Dataset(fileout+'_'+grid.upper()+'.nc', 'w', format='NETCDF4_CLASSIC')

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nt = 31
    nx, ny, nz = np.shape(grid_z['e3t'])
    dataset.createDimension('x', nx)
    dataset.createDimension('y', ny)
    dataset.createDimension('z', nz)
    dataset.createDimension('time', nt)

    # Create Variables
    longitude = dataset.createVariable('longitude', np.float32, ('y', 'x'))
    latitude = dataset.createVariable('latitude', np.float32, ('y', 'x'))
    depth = dataset.createVariable('depth'+grid, np.float32, 'z')
    time_counter = dataset.createVariable('time', np.float32, ('time'))
    longitude.units, longitude.long_name = 'km', 'X'
    latitude.units, latitude.long_name = 'km', 'Y'
    depth.units, depth.long_name = 'm', 'Z'
    time_counter.units = 'hours since 1950-01-01 00:00:00'
    time_counter.long_name = 'Time (hours since 1950-01-01)'
    time_counter.axis = 'T'
    time_counter._CoordinateAxisType = "Time"
    time_counter.calendar = 'gregorian'
    time_counter.standard_name = 'time'
    # Populate file with input data
    longitude[:, :] = grid_h['lont'].T
    latitude[:, :] = grid_h['latt'].T
    depth[:] = grid_z['dept_1d']
    time_counter[:] = np.linspace(587340.00,588060.00,31)
    for key in params:
        parameter = dataset.createVariable(str(params[key]['name']), np.float64, ('time','z', 'y', 'x'))
        parameter.units, parameter.long_name = str(params[key]['units']), str(params[key]['longname'])
        value_fill = np.ones(np.shape(grid_z['e3t']))
        value_fill = value_fill*params[key]['const_value']
        parameter[:, :, :] = value_fill.T

    # Close off pointer
    dataset.close()
    return 0

def write_bathy(fileout, grid_h,grid_z):
    '''
    Writes out a

    Args:

    Returns:
    '''
    # Open pointer to netcdf file
    dataset = Dataset(fileout, 'w', format='NETCDF4_CLASSIC')

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nx, ny = np.shape(grid_h['e1t'])
    dataset.createDimension('x', nx)
    dataset.createDimension('y', ny)


    # Create Variables
    nav_lon = dataset.createVariable('nav_lon', np.float32, ('y', 'x'))

    nav_lat = dataset.createVariable('nav_lat', np.float32, ('y', 'x'))
    nav_lon.units, nav_lon.long_name = 'km', 'X'
    nav_lat.units, nav_lat.long_name = 'km', 'Y'

    Bathymetry = dataset.createVariable('Bathymetry', np.float64,('y','x'))
    Bathymetry.units,Bathymetry.long_name = 'meters','Median depth by area'
    nav_lon[:, :] = grid_h['lont'].T
    nav_lat[:, :] = grid_h['latt'].T

    Bathy = np.ones((nx,ny))
    Bathy = Bathy * grid_z['dept_1d'][-1]

    Bathymetry[:,:] = Bathy

    dataset.close()
    return 0