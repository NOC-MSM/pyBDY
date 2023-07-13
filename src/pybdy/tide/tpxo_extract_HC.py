"""
Extract the tidal harmonic constants out of a tidal model for given locations.

[amp,Gph] = tpxo_extract_HC(Model,lat,lon,type,Cid).

@author: Mr. Srikanth Nagella
"""

import numpy as np
from netCDF4 import Dataset
from scipy import interpolate


class TpxoExtract(object):
    """TPXO model extract_hc.c implementation in python."""

    def __init__(self, settings, lat, lon, grid_type):
        """Initialise the Extract of tide information from the netcdf Tidal files."""
        # Set tide model
        if settings["tide_model"].lower() == "tpxo7p2":
            hRe_name = "hRe"
            hIm_name = "hIm"
            lon_z_name = "lon_z"
            lat_z_name = "lat_z"
            URe_name = "URe"
            UIm_name = "UIm"
            lon_u_name = "lon_u"
            lat_u_name = "lat_u"
            VRe_name = "VRe"
            VIm_name = "VIm"
            lon_v_name = "lon_v"
            lat_v_name = "lat_v"
            mz_name = "mz"
            mu_name = "mu"
            mv_name = "mv"
            self.grid = Dataset(settings["tide_grid"])  # ../data/tide/grid_tpxo7.2.nc')
            # read the height_dataset file
            self.height_dataset = Dataset(
                settings["tide_h"]
            )  # ../data/tide/h_tpxo7.2.nc')
            # read the velocity_dataset file
            self.velocity_dataset = Dataset(
                settings["tide_u"]
            )  # ../data/tide/u_tpxo7.2.nc')

            height_z = self.grid.variables["hz"]
            mask_z = self.grid.variables["mz"]
            lon_z = self.height_dataset.variables[lon_z_name][:, 0]
            lat_z = self.height_dataset.variables[lat_z_name][0, :]
            lon_resolution = lon_z[1] - lon_z[0]
            data_in_km = 0  # added to maintain the reference to matlab tmd code
            # Pull out the constituents that are avaibable
            self.cons = []
            for ncon in range(self.height_dataset.variables["con"].shape[0]):
                self.cons.append(
                    self.height_dataset.variables["con"][ncon, :]
                    .tostring()
                    .strip()
                    .decode("utf-8")
                )
        elif settings["tide_model"].lower() == "fes2014":
            print(
                "did not actually code stuff for FES in this routine.\
Though that would be ideal. Instead put it in fes_extract_HC.py"
            )
        else:
            print("Don" "t know that tide model")

        # Wrap coordinates in longitude if the domain is global
        glob = 0
        if lon_z[-1] - lon_z[0] == 360 - lon_resolution:
            glob = 1
        if glob == 1:
            lon_z = np.concatenate(
                (
                    [
                        lon_z[0] - lon_resolution,
                    ],
                    lon_z,
                    [
                        lon_z[-1] + lon_resolution,
                    ],
                )
            )
            height_z = np.concatenate(
                (
                    [
                        height_z[-1, :],
                    ],
                    height_z,
                    [
                        height_z[0, :],
                    ],
                ),
                axis=0,
            )
            mask_z = np.concatenate(
                (
                    [
                        mask_z[-1, :],
                    ],
                    mask_z,
                    [
                        mask_z[0, :],
                    ],
                ),
                axis=0,
            )

        # adjust lon convention
        xmin = np.min(lon)

        if data_in_km == 0:
            if xmin < lon_z[0]:
                lon[lon < 0] = lon[lon < 0] + 360
            if xmin > lon_z[-1]:
                lon[lon > 180] = lon[lon > 180] - 360

        # height_z[height_z==0] = np.NaN
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

        height_z[height_z == 0] = np.NaN
        lonlat = np.concatenate((lon, lat))
        lonlat = np.reshape(lonlat, (lon.size, 2), order="F")

        depth = interpolate.interpn((lon_z, lat_z), height_z, lonlat)
        #        f=interpolate.RectBivariateSpline(lon_z,lat_z,mask_z,kx=1,ky=1)
        #        depth_mask = np.zeros(lon.size)
        #        for idx in range(lon.size):
        #            depth_mask[idx] = f(lon[idx],lat[idx])
        depth_mask = interpolate.interpn((lon_z, lat_z), mask_z, lonlat)
        index = np.where((np.isnan(depth)) & (depth_mask > 0))

        if index[0].size != 0:
            depth[index] = bilinear_interpolation(
                lon_z, lat_z, height_z, lon[index], lat[index]
            )

        if grid_type == "z" or grid_type == "t":
            self.amp, self.gph = self.interpolate_constituents(
                self.height_dataset,
                hRe_name,
                hIm_name,
                lon_z_name,
                lat_z_name,
                lon,
                lat,
                maskname=mz_name,
            )
        elif grid_type == "u":
            self.amp, self.gph = self.interpolate_constituents(
                self.velocity_dataset,
                URe_name,
                UIm_name,
                lon_u_name,
                lat_u_name,
                lon,
                lat,
                depth,
                maskname=mu_name,
            )
        elif grid_type == "v":
            self.amp, self.gph = self.interpolate_constituents(
                self.velocity_dataset,
                VRe_name,
                VIm_name,
                lon_v_name,
                lat_v_name,
                lon,
                lat,
                depth,
                maskname=mv_name,
            )
        else:
            print("Unknown grid_type")
            return

    def interpolate_constituents(
        self,
        nc_dataset,
        real_var_name,
        img_var_name,
        lon_var_name,
        lat_var_name,
        lon,
        lat,
        height_data=None,
        maskname=None,
    ):
        """Interpolate the tidal constituents along the given lat lon coordinates."""
        amp = np.zeros(
            (
                nc_dataset.variables["con"].shape[0],
                lon.shape[0],
            )
        )
        gph = np.zeros(
            (
                nc_dataset.variables["con"].shape[0],
                lon.shape[0],
            )
        )
        data = np.array(np.ravel(nc_dataset.variables[real_var_name]), dtype=complex)
        data.imag = np.array(np.ravel(nc_dataset.variables[img_var_name]))

        data = data.reshape(nc_dataset.variables[real_var_name].shape)
        # data[data==0] = np.NaN

        # Lat Lon values
        x_values = nc_dataset.variables[lon_var_name][:, 0]
        y_values = nc_dataset.variables[lat_var_name][0, :]
        x_resolution = x_values[1] - x_values[0]
        glob = 0
        if x_values[-1] - x_values[0] == 360 - x_resolution:
            glob = 1

        if glob == 1:
            x_values = np.concatenate(
                (
                    [
                        x_values[0] - x_resolution,
                    ],
                    x_values,
                    [
                        x_values[-1] + x_resolution,
                    ],
                )
            )

        # adjust lon convention
        xmin = np.min(lon)
        if xmin < x_values[0]:
            lon[lon < 0] = lon[lon < 0] + 360
        if xmin > x_values[-1]:
            lon[lon > 180] = lon[lon > 180] - 360

        lonlat = np.concatenate((lon, lat))
        lonlat = np.reshape(lonlat, (lon.size, 2), order="F")

        mask = self.grid.variables[maskname]
        mask = np.concatenate(
            (
                [
                    mask[-1, :],
                ],
                mask,
                [
                    mask[0, :],
                ],
            ),
            axis=0,
        )
        # interpolate the mask values
        maskedpoints = interpolate.interpn((x_values, y_values), mask, lonlat)

        data_temp = np.zeros(
            (
                data.shape[0],
                lon.shape[0],
                2,
            )
        )
        for cons_index in range(data.shape[0]):
            # interpolate real values
            data_temp[cons_index, :, 0] = interpolate_data(
                x_values, y_values, data[cons_index, :, :].real, maskedpoints, lonlat
            )
            # interpolate imag values
            data_temp[cons_index, :, 1] = interpolate_data(
                x_values, y_values, data[cons_index, :, :].imag, maskedpoints, lonlat
            )

            # for velocity_dataset values
            if height_data is not None:
                data_temp[cons_index, :, 0] = data_temp[cons_index, :, 0] / height_data
                data_temp[cons_index, :, 1] = data_temp[cons_index, :, 1] / height_data

            zcomplex = np.array(data_temp[cons_index, :, 0], dtype=complex)
            zcomplex.imag = data_temp[cons_index, :, 1]

            amp[cons_index, :] = np.absolute(zcomplex)
            gph[cons_index, :] = np.arctan2(-1 * zcomplex.imag, zcomplex.real)
        gph = gph * 180.0 / np.pi
        gph[gph < 0] = gph[gph < 0] + 360.0
        return amp, gph


def interpolate_data(lon, lat, data, mask, lonlat):
    """Interpolate data data on regular grid for given lonlat coordinates."""
    result = np.zeros((lonlat.shape[0],))
    data[data == 0] = np.NaN
    data = np.concatenate(
        (
            [
                data[-1, :],
            ],
            data,
            [
                data[0, :],
            ],
        ),
        axis=0,
    )
    result[:] = interpolate.interpn((lon, lat), data, lonlat)
    index = np.where((np.isnan(result)) & (mask > 0))
    if index[0].size != 0:
        result[index] = bilinear_interpolation(
            lon, lat, data, np.ravel(lonlat[index, 0]), np.ravel(lonlat[index, 1])
        )
    return result


def bilinear_interpolation(lon, lat, data, lon_new, lat_new):
    """Do a bilinear interpolation of grid where the data values are NaN's."""
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
        print("Check Dimensions")
        return np.NaN
    if glob == 1:
        lon = np.concatenate(
            (
                [
                    lon[0] - 2 * lon_resolution,
                    lon[0] - lon_resolution,
                ],
                lon,
                [lon[-1] + lon_resolution, lon[-1] + 2 * lon_resolution],
            )
        )
        data = np.concatenate(
            (data[-2, :], data[-1, :], data, data[0, :], data[1, :]), axis=0
        )
        mask = np.concatenate(
            (mask[-2, :], mask[-1, :], mask, mask[0, :], mask[1, :]), axis=0
        )
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
    height_temp = (
        weight_factor_1 * data[0:-2, 0:-2]
        + weight_factor_0 * data[0:-2, 1:-1]
        + weight_factor_1 * data[0:-2, 2:]
        + weight_factor_1 * data[2:, 0:-2]
        + weight_factor_0 * data[2:, 1:-1]
        + weight_factor_1 * data[2:, 2:]
        + weight_factor_0 * data[1:-1, 0:-2]
        + weight_factor_0 * data[1:-1, 2:]
    )
    mask_temp = (
        weight_factor_1 * mask[0:-2, 0:-2]
        + weight_factor_0 * mask[0:-2, 1:-1]
        + weight_factor_1 * mask[0:-2, 2:]
        + weight_factor_1 * mask[2:, 0:-2]
        + weight_factor_0 * mask[2:, 1:-1]
        + weight_factor_1 * mask[2:, 2:]
        + weight_factor_0 * mask[1:-1, 0:-2]
        + weight_factor_0 * mask[1:-1, 2:]
    )
    mask_temp[mask_temp == 0] = 1
    data_copy = data.copy()
    data_copy[1:-1, 1:-1] = np.divide(height_temp, mask_temp)
    nonmask_index = np.where(mask == 1)
    data_copy[nonmask_index] = data[nonmask_index]
    data_copy[data_copy == 0] = np.NaN
    lonlat = np.concatenate((lon_new_copy, lat_new))
    lonlat = np.reshape(lonlat, (lon_new_copy.size, 2), order="F")
    result = interpolate.interpn((lon, lat), data_copy, lonlat)

    return result


# lat=[42.8920,42.9549,43.0178]
# lon=[339.4313,339.4324,339.4335]
# lat_u=[42.8916,42.9545,43.0174]
# lon_u=[339.4735,339.4746,339.4757]
# lat = np.array(lat_u)
# lon = np.array(lon_u)
# lon = TPXO_Extract(lat,lon,'velocity_dataset')
