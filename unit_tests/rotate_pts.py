"""
Source: https://gist.github.com/LyleScott/d17e9d314fbe6fc29767d8c5c029c362

Adapted Function to rotate NEMO grid for unit testing. rot variable defines how much rotation
occurs, the results are then plotted in a figure showing original (blue points) and rotated (red) grids.
The source coordinate grid is also plotted (green).

"""

from math import cos,sin,radians
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs

import unit_tests.coord_gen as cg

# TODO: add in auto max and min lat and lon
# TODO: remove hard coded file names and directories.

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
    # tweak margins of subplots as tight layout doesn't work
    plt.subplots_adjust(left=0.01, right=1, top=0.9, bottom=0.05,wspace=0.01)

    plt.show()


def _main():
    #Source Coords
    dx = 1000 # units in km
    dy = 1000 # units in Km
    jpi = 15
    jpj = 15
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    h_fname = 'unit_tests/test_data/test_src__hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_src_zgr_zps.nc'
    grid_h1 = cg.set_hgrid(dx,dy,jpi,jpj)
    grid_z1 = cg.set_zgrid(grid_h1,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = cg.write_coord_H(h_fname,grid_h1)
    write_coord_Z = cg.write_coord_Z(z_fname,grid_h1,grid_z1)
    if write_coord_H + write_coord_Z == 0:
        print("Success!")

    #Dst Coords
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 20
    zoffy = 20
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    sf = 10
    h_fname = 'unit_tests/test_data/test_dst_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_dst_zgr_zps.nc'
    grid_h2 = cg.set_hgrid(dx,dy,jpi,jpj,zoffx,zoffy,sf)
    grid_z2 = cg.set_zgrid(grid_h2,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = cg.write_coord_H(h_fname,grid_h2)
    write_coord_Z = cg.write_coord_Z(z_fname,grid_h2,grid_z2)
    if write_coord_H + write_coord_Z == 0:
        print("Success!")

    # set rotation and origin point
    rot = 45
    theta = radians(rot)
    origin = (7,7)


    rot_lat,rot_lon = rotate_around_point(grid_h2['latt'],grid_h2['lont'],theta,origin)

    #offset coords
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 25
    zoffy = 25
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    sf = 10
    h_fname = 'unit_tests/test_data/test_dst_offset_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_dst_offset_zgr_zps.nc'
    grid_h3 = cg.set_hgrid(dx,dy,jpi,jpj,zoffx,zoffy,sf)
    grid_z3 = cg.set_zgrid(grid_h2,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = cg.write_coord_H(h_fname,grid_h3)
    write_coord_Z = cg.write_coord_Z(z_fname,grid_h3,grid_z3)
    if write_coord_H + write_coord_Z == 0:
        print("Success!")


    # plot orginal, rotatated and source lat and lon
    plot_grids(grid_h2['latt'],grid_h2['lont'],rot_lat,rot_lon,grid_h3['latt'], \
               grid_h3['lont'],grid_h1['latt'],grid_h1['lont'])
    # save new lat lon to dataset
    #ds.nav_lat.values[:], ds.nav_lon.values[:] = new_lat,new_lon
    # save dataset to netcdf
    #ds.to_netcdf('unit_tests/test_data/rot_'+str(rot)+'_dst_hgr_zps.nc')
    # close data files
    #ds.close()
    #src.close()

if __name__ == '__main__':
    _main()