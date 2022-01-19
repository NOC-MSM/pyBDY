'''
This is to extract the tidal harmonic constants out of a tidal model
for a given locations
[amp,gph] = fes_extract_HC(Model,lat,lon,type,Cid)

Modified from tpxo_extract_HC.py

3 Nov 2017
jelt
'''

# pylint: disable=E1103
# pylint: disable=no-name-in-module
from netCDF4 import Dataset
from scipy import interpolate
import numpy as np

class FesExtract(object):
    """
    This is FES model extract of harmonic constituents.
    The source FES data are stored in one-file-per-constituent
    Note the FES data are structre with lat and lon reversed relative to TPXO
    I.e. FES(lat,lon)
    c.f. TPXO(con,lon,lat)

    Note the FES heights are in cm (need to convert to metres)
    The momentum vector quantities are depth integrated TRANSPORTS (m^2/s).
    In TPXO both transport (m^2/s) and velocies (cm/s) are given.
    Here we use the transport fluxes.
    """
    def __init__(self, settings, lat, lon, grid_type):
        """initialises the Extract of tide information from the netcdf
           Tidal files"""

        if True:
           constituents = ['M2','S2','K2']
           #constituents = ['2N2','EPS2','J1','K1','K2','L2','LA2','M2','M3','M4','M6','M8','MF','MKS2','MM','MN4','MS4','MSF','MSQM','MTM','MU2','N2','N4','NU2','O1','P1','Q1','R2','S1','S2','S4','SA','SSA','T2']

           icon = -1
           self.cons = []
           self.amp_z = []
           self.pha_z = []
           self.amp_u = []
           self.pha_u = []
           self.amp_v = []
           self.pha_v = []

           for con in constituents:
             icon = icon+1
             #print 'jelt: con ',con.lower()
             #print '/projectsa/NEMO/Forcing/FES2014/ocean_tide_extrapolated//' +con.lower()+ '.nc'
             ## load in the data
             #self.Z_dataset = Dataset('/work/thopri/Global_Tide_Model/FES_NetCDFs/' +con.lower()+ '_Z.nc')
             #self.U_dataset = Dataset('/work/thopri/Global_Tide_Model/FES_NetCDFs/' +con.lower()+ '_U.nc')
             #self.V_dataset = Dataset('/work/thopri/Global_Tide_Model/FES_NetCDFs/' +con.lower()+ '_V.nc')
             self.Z_dataset = Dataset(settings['tide_fes'] +'/ocean_tide_extrapolated/' +con.lower()+ '.nc')
             self.U_dataset = Dataset(settings['tide_fes'] +'/eastward_velocity/' +con.lower()+ '.nc')
             self.V_dataset = Dataset(settings['tide_fes'] +'/northward_velocity/' +con.lower()+ '.nc')

             if icon==0:
                     ny,nx = np.shape(self.Z_dataset['amplitude'][:,:])

                     self.amp_z = np.reshape( self.Z_dataset['amplitude'][:,:]/100., (1,ny,nx) )
                     self.pha_z = np.reshape( self.Z_dataset['phase'][:,:], (1,ny,nx) )

                     self.amp_u = np.reshape( self.U_dataset['Ua'][:,:], (1,ny,nx) )
                     self.pha_u = np.reshape( self.U_dataset['Ug'][:,:], (1,ny,nx) )

                     self.amp_v = np.reshape( self.V_dataset['Va'][:,:], (1,ny,nx) )
                     self.pha_v = np.reshape( self.V_dataset['Vg'][:,:], (1,ny,nx) )
                     print('jelt: ',np.shape(self.amp_z))

             else:
                     self.amp_z = np.concatenate( (self.amp_z, np.reshape(self.Z_dataset['amplitude'][:,:]/100.,(1,ny,nx))), axis=0 )
                     self.pha_z = np.concatenate( (self.pha_z, np.reshape(self.Z_dataset['phase'][:,:],(1,ny,nx))), axis=0 )
                     self.amp_u = np.concatenate( (self.amp_u, np.reshape(self.U_dataset['Ua'][:,:],(1,ny,nx))), axis=0 )
                     self.pha_u = np.concatenate( (self.pha_u, np.reshape(self.U_dataset['Ug'][:,:],(1,ny,nx))), axis=0 )
                     self.amp_v = np.concatenate( (self.amp_v, np.reshape(self.V_dataset['Va'][:,:],(1,ny,nx))), axis=0 )
                     self.pha_v = np.concatenate( (self.pha_v, np.reshape(self.V_dataset['Vg'][:,:],(1,ny,nx))), axis=0 )
                     print('jelt: ',np.shape(self.amp_z))
             self.cons.append(con) # self.height_dataset.variables['con'][ncon, :].tostring().strip())

           # Swap the lat and lon axes to be ordered according to (con,lon,lat)
           self.amp_z = np.swapaxes(self.amp_z,1,2)
           self.pha_z = np.swapaxes(self.pha_z,1,2)
           self.amp_u = np.swapaxes(self.amp_u,1,2)
           self.pha_u = np.swapaxes(self.pha_u,1,2)
           self.amp_v = np.swapaxes(self.amp_v,1,2)
           self.pha_v = np.swapaxes(self.pha_v,1,2)

           # Construct mask from missing values. Also NaN these out. 1=Wet. 0=land
           mask_z = np.ones((np.shape(self.amp_z)[1], np.shape(self.amp_z)[2]))
           mask_z[self.amp_z[0,:,:] > 9999] = 0

           self.lon_z = self.Z_dataset['lon'][:]
           self.lat_z = self.Z_dataset['lat'][:]
           self.lon_u = self.U_dataset['lon'][:]
           self.lat_u = self.U_dataset['lat'][:]
           self.lon_v = self.V_dataset['lon'][:]
           self.lat_v = self.V_dataset['lat'][:]
           lon_resolution = self.lon_z[1] - self.lon_z[0]
           data_in_km = 0 # added to maintain the reference to matlab tmd code


        else:
           print('You wont get here.')

        # Wrap coordinates in longitude if the domain is global
        glob = 0
        if self.lon_z[-1]-self.lon_z[0] == 360-lon_resolution:
            glob = 1
        if glob == 1:
            lon_z = np.concatenate(([self.lon_z[0]-lon_resolution, ], self.lon_z,
                                    [self.lon_z[-1]+lon_resolution, ]))
#            height_z = np.concatenate(([height_z[-1, :], ], height_z, [height_z[0, :],]), axis=0)
            mask_z = np.concatenate(([mask_z[-1, :], ], mask_z, [mask_z[0, :], ]), axis=0)

        #adjust lon convention
        xmin = np.min(lon)

        if data_in_km == 0:
            if xmin < self.lon_z[0]:
                lon[lon < 0] = lon[lon < 0] + 360
            if xmin > self.lon_z[-1]:
                lon[lon > 180] = lon[lon > 180]-360

        #height_z[height_z==0] = np.NaN
#        f=interpolate.RectBivariateSpline(lon_z,lat_z,height_z,kx=1,ky=1)
#        depth = np.zeros(lon.size)
#        for idx in range(lon.size):
#            depth[idx] = f(lon[idx],lat[idx])
#        print depth[369:371]

#        H2 = np.ravel(height_z)
#        H2[H2==0] = np.NaN
#        points= np.concatenate((np.ravel(self.height_dataset.variables['lon_z']),
#                                np.ravel(self.height_dataset.variables['lat_z'])))
#        points= np.reshape(points,(points.shape[0]/2,2),order='F')
#        print points.shape
#        print np.ravel(height_z).shape
#        depth = interpolate.griddata(points,H2,(lon,lat))
#        print depth
#        print depth.shape

#        height_z[height_z == 0] = np.NaN # This is a bathymetry variable (not in _my_ FES data)
        lonlat = np.concatenate((lon, lat))
        lonlat = np.reshape(lonlat, (lon.size, 2), order='F')

#        depth = interpolate.interpn((lon_z, lat_z), height_z, lonlat)
#        f=interpolate.RectBivariateSpline(lon_z,lat_z,mask_z,kx=1,ky=1)
#        depth_mask = np.zeros(lon.size)
#        for idx in range(lon.size):
#            depth_mask[idx] = f(lon[idx],lat[idx])
#        depth_mask = interpolate.interpn((lon_z, lat_z), mask_z, lonlat)
#       index = np.where((np.isnan(depth)) & (depth_mask > 0)) # jelt: i.e. land (from bathy) and wet (from harmonics)

# jelt: I don't really get this index quantity. But I don't need it. Some descriptions would be good
#        if index[0].size != 0:
#            depth[index] = bilinear_interpolation(lon_z, lat_z, height_z, lon[index], lat[index])

        print('jelt: grid_type', grid_type)
        print('jelt: amp_z', np.shape(self.amp_z))
        print('jelt: lon_z', np.shape(self.lon_z))
        if grid_type == 'z' or grid_type == 't':
            self.amp, self.gph = self.interpolate_constituents(self.amp_z, self.pha_z, self.lon_z, self.lat_z, lon, lat)
        elif grid_type == 'u':
            self.amp, self.gph = self.interpolate_constituents( self.amp_u, self.pha_u, self.lon_u, self.lat_u,
                                                               lon, lat) # Not passing depth for depth normalisation
        elif grid_type == 'v':
            self.amp, self.gph = self.interpolate_constituents( self.amp_v, self.pha_v, self.lon_v, self.lat_v,
                                                               lon, lat) # Not passing depth for depth normalisation
        else:
            print('Unknown grid_type')
            return

    def interpolate_constituents(self, amp_fes, pha_fes, lon_fes, lat_fes, lon, lat):
        """ Interpolates the tidal constituents along the given lat lon coordinates """
        print('jelt: amp_fes',np.shape(amp_fes))
        print('jelt: lon_fes',np.shape(lon_fes))
        print('jelt: amp_fes[0]',np.shape(amp_fes)[0])
        print('jelt: lon_fes[0]',np.shape(lon_fes)[0])
        amp = np.zeros((np.shape(amp_fes)[0], np.shape(lon)[0],))
        gph = np.zeros((np.shape(amp_fes)[0], np.shape(lon)[0],))
        #data = np.array(np.ravel(nc_dataset.variables[real_var_name]), dtype=complex)
        #data.imag = np.array(np.ravel(nc_dataset.variables[img_var_name]))
        data = np.array(np.ravel(amp_fes * np.cos( np.deg2rad(pha_fes)) ), dtype=complex)
        data.imag = np.array(np.ravel( amp_fes * np.sin( np.deg2rad(pha_fes)) ))

        data = data.reshape(amp_fes.shape)
        #data[data==0] = np.NaN

        #Lat Lon values. Note FES lon, lat are already 1D (TPXO are 2D)
        x_values = lon_fes #[:, 0]
        y_values = lat_fes #[0, :]
        x_resolution = x_values[1] - x_values[0]
        glob = 0
        if x_values[-1]-x_values[0] == 360-x_resolution:
            glob = 1

        if glob == 1:
            x_values = np.concatenate(([x_values[0]-x_resolution,], x_values,
                                       [x_values[-1]+x_resolution, ]))

        #adjust lon convention
        xmin = np.min(lon)
        if xmin < x_values[0]:
            lon[lon < 0] = lon[lon < 0] + 360
        if xmin > x_values[-1]:
            lon[lon > 180] = lon[lon > 180]-360

        lonlat = np.concatenate((lon, lat))
        lonlat = np.reshape(lonlat, (lon.size, 2), order='F')

        # Construct mask from missing values. Also NaN these out.
        mask = np.ones((np.shape(amp_fes)[1], np.shape(amp_fes)[2]))
        mask[amp_fes[0,:,:] > 9999] = 0
        data[amp_fes > 9999] = np.NaN

        mask = np.concatenate(([mask[-1, :], ], mask, [mask[0, :], ]), axis=0)
        #interpolate the mask values
        maskedpoints = interpolate.interpn((x_values, y_values), mask, lonlat)

        data_temp = np.zeros((data.shape[0], lon.shape[0], 2, ))
        for cons_index in range(data.shape[0]):
            #interpolate real values
            data_temp[cons_index, :, 0] = interpolate_data(x_values, y_values,
                                                                data[cons_index, :, :].real,
                                                                maskedpoints, lonlat)
            #interpolate imag values
            data_temp[cons_index, :, 1] = interpolate_data(x_values, y_values,
                                                                data[cons_index, :, :].imag,
                                                                maskedpoints, lonlat)
# jelt: comment bathymetric dependent functionality out
#            #for velocity_dataset values
#            if height_data is not None:
#                data_temp[cons_index, :, 0] = data_temp[cons_index, :, 0]/height_data*100
#                data_temp[cons_index, :, 1] = data_temp[cons_index, :, 1]/height_data*100

            zcomplex = np.array(data_temp[cons_index, :, 0], dtype=complex)
            zcomplex.imag = data_temp[cons_index, :, 1]

            amp[cons_index, :] = np.absolute(zcomplex)
            gph[cons_index, :] = np.arctan2(zcomplex.imag, zcomplex.real) # Remove the minus sign since phase is already has 'clockwise' rotation
        gph = gph*180.0/np.pi
        gph[gph < 0] = gph[gph < 0]+360.0
        return amp, gph

def interpolate_data(lon, lat, data, mask, lonlat):
    """ Interpolate data data on regular grid for given lonlat coordinates """
    result = np.zeros((lonlat.shape[0], ))
    data[data == 0] = np.NaN
    data = np.concatenate(([data[-1, :], ], data, [data[0, :], ]), axis=0)
    result[:] = interpolate.interpn((lon, lat), data, lonlat)
    index = np.where((np.isnan(result)) & (mask > 0))
    if index[0].size != 0:
        result[index] = bilinear_interpolation(lon, lat, data, np.ravel(lonlat[index, 0]),
                                               np.ravel(lonlat[index, 1]))
    return result

def bilinear_interpolation(lon, lat, data, lon_new, lat_new):
    """ Does a bilinear interpolation of grid where the data values are NaN's"""
    glob = 0
    lon_resolution = lon[1] - lon[0]
    if lon[-1] - lon[1] == 360 - lon_resolution:
        glob = 1
    inan = np.where(np.isnan(data))
    data[inan] = 0
    mask = np.zeros(data.shape)
    mask[data != 0] = 1
#    n = lon.size
#    m = lat.size
    if lon.size != data.shape[0] or lat.size != data.shape[1]:
        print('Check Dimensions')
        return np.NaN
    if glob == 1:
        lon = np.concatenate(([lon[0] - 2 * lon_resolution, lon[0] - lon_resolution, ],
                              lon, [lon[-1] + lon_resolution, lon[-1] + 2 * lon_resolution]))
        data = np.concatenate((data[-2, :], data[-1, :], data, data[0, :], data[1, :]), axis=0)
        mask = np.concatenate((mask[-2, :], mask[-1, :], mask, mask[0, :], mask[1, :]), axis=0)
    lon_new_copy = lon_new

    nonmask_index = np.where((lon_new_copy < lon[0]) & (lon_new_copy > lon[-1]))
    if lon[-1] > 180:
        lon_new_copy[nonmask_index] = lon_new_copy[nonmask_index] + 360
    if lon[-1] < 0:
        lon_new_copy[nonmask_index] = lon_new_copy[nonmask_index] - 360
    lon_new_copy[lon_new_copy > 360] = lon_new_copy[lon_new_copy > 360] - 360
    lon_new_copy[lon_new_copy < -180] = lon_new_copy[lon_new_copy < -180] + 360

    weight_factor_0 = 1 / (4 + 2 * np.sqrt(2))
    weight_factor_1 = weight_factor_0 / np.sqrt(2)
    height_temp = weight_factor_1 * data[0:-2, 0:-2] + weight_factor_0 * data[0:-2, 1:-1] + \
                  weight_factor_1 * data[0:-2, 2:] + weight_factor_1 * data[2:, 0:-2] + \
                  weight_factor_0 * data[2:, 1:-1] + weight_factor_1 * data[2:, 2:] + \
                  weight_factor_0 * data[1:-1, 0:-2] + weight_factor_0 * data[1:-1, 2:]
    mask_temp = weight_factor_1 * mask[0:-2, 0:-2] + weight_factor_0 * mask[0:-2, 1:-1] + \
                weight_factor_1 * mask[0:-2, 2:] + weight_factor_1 * mask[2:, 0:-2] + \
                weight_factor_0 * mask[2:, 1:-1] + weight_factor_1 * mask[2:, 2:] + \
                weight_factor_0 * mask[1:-1, 0:-2] + weight_factor_0 * mask[1:-1, 2:]
    mask_temp[mask_temp == 0] = 1
    data_copy = data.copy()
    data_copy[1:-1, 1:-1] = np.divide(height_temp, mask_temp)
    nonmask_index = np.where(mask == 1)
    data_copy[nonmask_index] = data[nonmask_index]
    data_copy[data_copy == 0] = np.NaN
    lonlat = np.concatenate((lon_new_copy, lat_new))
    lonlat = np.reshape(lonlat, (lon_new_copy.size, 2), order='F')
    result = interpolate.interpn((lon, lat), data_copy, lonlat)

    return result


#lat=[42.8920,42.9549,43.0178]
#lon=[339.4313,339.4324,339.4335]
#lat_u=[42.8916,42.9545,43.0174]
#lon_u=[339.4735,339.4746,339.4757]
#lat = np.array(lat_u)
#lon = np.array(lon_u)
#lon = TPXO_Extract(lat,lon,'velocity_dataset')
