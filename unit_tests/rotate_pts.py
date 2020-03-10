"""
Source: https://gist.github.com/LyleScott/d17e9d314fbe6fc29767d8c5c029c362

Adapted Function to rotate NEMO grid for unit testing.

"""

from math import cos,sin,radians
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs

def rotate_around_point(lat_in,lon_in, radians , origin=(0, 0)):
    """Rotate a point around a given point.
    """
    new_lon = np.zeros(np.shape(lon_in))
    new_lat = np.zeros(np.shape(lat_in))

    offset_lat, offset_lon = origin
    cos_rad = cos(radians)
    sin_rad = sin(radians)

    for indx in range(np.shape(lat_in)[0]):
        for indy in range(np.shape(lon_in)[1]):

            adjusted_lat = (lat_in[indx,indy] - offset_lat)
            adjusted_lon = (lon_in[indx,indy] - offset_lon)
            new_lat[indx,indy] = offset_lat + cos_rad * adjusted_lat + -sin_rad * adjusted_lon
            new_lon[indx,indy] = offset_lon + sin_rad * adjusted_lat + cos_rad * adjusted_lon

    return new_lat, new_lon

def plot_grids(lat_in,lon_in,new_lat,new_lon,src_lat,src_lon):

    maxlat = 72
    minlat = 32
    maxlon = 18
    minlon = -28

    plt.figure(figsize=[18, 8])  # a new figure window

    ax = plt.subplot(121, projection=ccrs.PlateCarree())  # specify (nrows, ncols, axnum)
    ax.set_extent([minlon,maxlon,minlat,maxlat],crs=ccrs.PlateCarree()) #set extent
    ax.set_title('Original Grid', fontsize=20,y=1.05) #set title
    ax.add_feature(cartopy.feature.LAND, zorder=0)  # add land polygon
    ax.add_feature(cartopy.feature.COASTLINE, zorder=10)  # add coastline polyline
    gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='black', alpha=0.5, linestyle='--', draw_labels=True)

    ax1 = plt.subplot(122, projection=ccrs.PlateCarree())  # specify (nrows, ncols, axnum)
    ax1.set_extent([minlon,maxlon,minlat,maxlat],crs=ccrs.PlateCarree()) #set extent
    ax1.set_title('Rotated Grid', fontsize=20,y=1.05) #set title
    ax1.add_feature(cartopy.feature.LAND, zorder=0)  # add land polygon
    ax1.add_feature(cartopy.feature.COASTLINE, zorder=10)  # add coastline polyline
    gl1 = ax1.gridlines(crs=ccrs.PlateCarree(), linewidth=2, color='black', alpha=0.5, linestyle='--', draw_labels=True)

    src_lon = np.tile(src_lon, (np.shape(src_lat)[0], 1))
    src_lat = np.tile(src_lat, (np.shape(src_lon)[1], 1))
    src_lat = np.rot90(src_lat)

    ax.plot(lon_in, lat_in, color='blue', marker='.')
    ax.plot(src_lon,src_lat, color='green', marker='.')
    ax1.plot(new_lon,new_lat, color='red', marker='.')
    ax1.plot(src_lon,src_lat, color='green',marker='.')
    plt.subplots_adjust(left=0.01, right=1, top=0.9, bottom=0.05,wspace=0.01)

    plt.show()


def _main():
    ds = xr.open_dataset('unit_tests/test_data/dst_hgr_zps.nc')
    src = xr.open_dataset('unit_tests/test_data/src_coordinates.nc')
    rot = 45
    theta = radians(rot)
    origin = (54, -6)
    new_lat,new_lon = rotate_around_point(ds.nav_lat.values[:],ds.nav_lon.values[:],theta,origin)
    plot_grids(ds.nav_lat.values[:],ds.nav_lon.values[:],new_lat,new_lon,src.latitude.values[:],src.longitude.values[:])
    ds.nav_lat.values[:], ds.nav_lon.values[:] = new_lat,new_lon
    ds.to_netcdf('unit_tests/test_data/rot_'+str(rot)+'_dst_hgr_zps.nc')
    ds.close()
    src.close()








if __name__ == '__main__':
    _main()