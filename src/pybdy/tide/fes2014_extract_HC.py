"""
Fes extraction of harmonic constituents.

Extract the tidal harmonic constants out of a tidal model for a given locations
[amp,gph] = fes2014_extract_HC(Model,lat,lon,type,Cid).

Modified from tpxo_extract_HC.py

3 Nov 2017
jelt
"""
import logging

import numpy as np
from netCDF4 import Dataset
from scipy import interpolate

from . import nemo_bdy_tide3


class FesExtract(object):
    """
    FES model extract of harmonic constituents.

    Notes
    -----
    The source FES data are stored in one-file-per-constituent
    Note the FES data are structre with lat and lon reversed relative to TPXO
    I.e. FES(lat,lon)
    c.f. TPXO(con,lon,lat).

    Note the FES heights are in cm (need to convert to metres)
    The momentum vector quantities are depth integrated TRANSPORTS (m^2/s).
    In TPXO both transport (m^2/s) and velocies (cm/s) are given.
    Here we use the transport fluxes.
    """

    def __init__(self, settings, lat, lon, grid_type):
        """Initialise the Extract of tide information from the netcdf Tidal files."""
        # Complete set of available constituents
        constituents = [
            "2N2",
            "EPS2",
            "J1",
            "K1",
            "K2",
            "L2",
            "LA2",
            "M2",
            "M3",
            "M4",
            "M6",
            "M8",
            "MF",
            "MKS2",
            "MM",
            "MN4",
            "MS4",
            "MSF",
            "MSQM",
            "MTM",
            "MU2",
            "N2",
            "N4",
            "NU2",
            "O1",
            "P1",
            "Q1",
            "R2",
            "S1",
            "S2",
            "S4",
            "SA",
            "SSA",
            "T2",
        ]

        # Extract the subset requested by the namelist
        compindx = [
            icon.astype(int)
            for icon in nemo_bdy_tide3.constituents_index(
                constituents, settings["clname"]
            )
        ]
        constit_list = [constituents[i] for i in compindx]

        try:
            icon = 0
            self.cons = []
            self.amp = []
            self.pha = []

            scale = 1.0  # multiplication scale to convert units, if needed
            if grid_type == "t":
                filename = "/ocean_tide_extrapolated/"
                amp_var = "amplitude"
                pha_var = "phase"
                scale = 0.01  # convert amplitude from cm to metres
            elif grid_type == "u":
                filename = "/eastward_velocity/"
                amp_var = "Ua"
                pha_var = "Ug"
                scale = 0.01  # convert cm/s to m/s
            elif grid_type == "v":
                filename = "/northward_velocity/"
                amp_var = "Va"
                pha_var = "Vg"
                scale = 0.01  # convert amplitude from cm to metres
            else:
                logging.error(f"Not expecting grid_type:{grid_type}")

            for con in constit_list:
                print(
                    f"Grid:{grid_type}. Extracting FES constituent:{con}, {icon+1}/{len(constit_list)}"
                )
                # load in the data
                ds = Dataset(settings["tide_fes"] + filename + con.lower() + ".nc", "r")

                if icon == 0:
                    lon_grd = ds["lon"][:]
                    lat_grd = ds["lat"][:]
                    nx = np.shape(lon_grd)[0]
                    ny = np.shape(lat_grd)[0]

                    amp_grd = np.reshape(ds[amp_var][:, :] * scale, (1, ny, nx))
                    pha_grd = np.reshape(ds[pha_var][:, :], (1, ny, nx))

                else:
                    amp_grd = np.concatenate(
                        (amp_grd, np.reshape(ds[amp_var][:, :] * scale, (1, ny, nx))),
                        axis=0,
                    )
                    pha_grd = np.concatenate(
                        (pha_grd, np.reshape(ds[pha_var][:, :], (1, ny, nx))), axis=0
                    )

                ds.close()

                self.cons.append(
                    con
                )  # self.height_dataset.variables['con'][ncon, :].tostring().strip())
                icon = icon + 1

            # Swap the lat and lon axes to be ordered according to (con,lon,lat)
            amp_grd = np.swapaxes(amp_grd, 1, 2)
            pha_grd = np.swapaxes(pha_grd, 1, 2)

            # Construct mask from missing values. Also NaN these out. 1=Wet. 0=land
            mask_grd = np.ones((np.shape(amp_grd)[1], np.shape(amp_grd)[2]))
            mask_grd[amp_grd[0, :, :] > 9999] = 0

            lon_resolution = lon_grd[1] - lon_grd[0]
            data_in_km = 0  # added to maintain the reference to matlab tmd code
        except Exception:
            logging.debug("You wont get here.")

        # Wrap coordinates in longitude if the domain is global.
        # This was previously only applied to the *_z grid
        glob = 0
        if lon_grd[-1] - lon_grd[0] == 360 - lon_resolution:
            glob = 1
        if glob == 1:
            lon_grd = np.concatenate(
                (
                    [
                        lon_grd[0] - lon_resolution,
                    ],
                    lon_grd,
                    [
                        lon_grd[-1] + lon_resolution,
                    ],
                )
            )
            mask_grd = np.concatenate(
                (
                    [
                        mask_grd[-1, :],
                    ],
                    mask_grd,
                    [
                        mask_grd[0, :],
                    ],
                ),
                axis=0,
            )

        # adjust lon convention
        xmin = np.min(lon)

        if data_in_km == 0:
            if xmin < lon_grd[0]:
                lon[lon < 0] = lon[lon < 0] + 360
            if xmin > lon_grd[-1]:
                lon[lon > 180] = lon[lon > 180] - 360

        lonlat = np.concatenate((lon, lat))
        lonlat = np.reshape(lonlat, (lon.size, 2), order="F")

        # print('jelt: grid_type', grid_type)
        # print('jelt: amp_z', np.shape(amp_grd))
        # print('jelt: lon_z', np.shape(lon_grd))
        self.amp, self.gph = self.interpolate_constituents(
            amp_grd, pha_grd, lon_grd, lat_grd, lon, lat
        )

    def interpolate_constituents(self, amp_fes, pha_fes, lon_fes, lat_fes, lon, lat):
        """Interpolates the tidal constituents along the given lat lon coordinates."""
        # print('jelt: amp_fes',np.shape(amp_fes))
        # print('jelt: lon_fes',np.shape(lon_fes))
        # print('jelt: amp_fes[0]',np.shape(amp_fes)[0])
        # print('jelt: lon_fes[0]',np.shape(lon_fes)[0])
        amp = np.zeros(
            (
                np.shape(amp_fes)[0],
                np.shape(lon)[0],
            )
        )
        gph = np.zeros(
            (
                np.shape(amp_fes)[0],
                np.shape(lon)[0],
            )
        )
        # data = np.array(np.ravel(nc_dataset.variables[real_var_name]), dtype=complex)
        # data.imag = np.array(np.ravel(nc_dataset.variables[img_var_name]))
        data = np.array(np.ravel(amp_fes * np.cos(np.deg2rad(pha_fes))), dtype=complex)
        data.imag = np.array(np.ravel(amp_fes * np.sin(np.deg2rad(pha_fes))))

        data = data.reshape(amp_fes.shape)
        # data[data==0] = np.NaN

        # Lat Lon values. Note FES lon, lat are already 1D (TPXO are 2D)
        x_values = lon_fes  # [:, 0]
        y_values = lat_fes  # [0, :]
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

        # Construct mask from missing values. Also NaN these out.
        mask = np.ones((np.shape(amp_fes)[1], np.shape(amp_fes)[2]))
        mask[amp_fes[0, :, :] > 9999] = 0
        data[amp_fes > 9999] = np.NaN

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
            # jelt: comment bathymetric dependent functionality out
            #            #for velocity_dataset values
            #            if height_data is not None:
            #                data_temp[cons_index, :, 0] = data_temp[cons_index, :, 0]/height_data*100
            #                data_temp[cons_index, :, 1] = data_temp[cons_index, :, 1]/height_data*100

            zcomplex = np.array(data_temp[cons_index, :, 0], dtype=complex)
            zcomplex.imag = data_temp[cons_index, :, 1]

            amp[cons_index, :] = np.absolute(zcomplex)
            gph[cons_index, :] = np.arctan2(
                zcomplex.imag, zcomplex.real
            )  # Remove the minus sign since phase is already has 'clockwise' rotation
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
    """Perform a bilinear interpolation of grid where the data values are NaN's."""
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
