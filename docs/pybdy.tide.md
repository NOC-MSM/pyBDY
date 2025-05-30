# pybdy.tide package

## Submodules

# pybdy.tide.fes2014_extract_HC module

Fes extraction of harmonic constituents.

Extract the tidal harmonic constants out of a tidal model for a given locations
[amp,gph] = fes2014_extract_HC(Model,lat,lon,type,Cid).

Modified from tpxo_extract_HC.py

3 Nov 2017
jelt

## *class* pybdy.tide.fes2014_extract_HC.FesExtract(settings, lat, lon, grid_type)

> Bases: `object`<br>

FES model extract of harmonic constituents.

## Notes

The source FES data are stored in one-file-per-constituent
Note the FES data are structured with lat and lon reversed relative to TPXO
I.e. FES(lat,lon)
c.f. TPXO7(con,lon,lat).
c.f. TPXO9(lon,lat)

Note the FES heights are in cm (need to convert to metres)
The momentum vector quantities are depth integrated TRANSPORTS (m^2/s).
In TPXO7 both transport (m^2/s) and velocies (cm/s) are given.
In TPXO9 only transport (cm^2/s) are given.
Here we use the transport fluxes.

### \_\_init\_\_(settings, lat, lon, grid_type)

Initialise the Extract of tide information from the netcdf Tidal files.

### interpolate_constituents(amp_fes, pha_fes, lon_fes, lat_fes, lon, lat)

Interpolates the tidal constituents along the given lat lon coordinates.

## pybdy.tide.fes2014_extract_HC.bilinear_interpolation(lon, lat, data, lon_new, lat_new)

Perform a bilinear interpolation of grid where the data values are NaN’s.

## pybdy.tide.fes2014_extract_HC.interpolate_data(lon, lat, data, mask, lonlat)

Interpolate data data on regular grid for given lonlat coordinates.

# pybdy.tide.nemo_bdy_tide module

## *class* pybdy.tide.nemo_bdy_tide.Extract(setup, DstCoord, Grid)

> Bases: `object`<br>

### \_\_init\_\_(setup, DstCoord, Grid)

### extract_con(con)

# pybdy.tide.nemo_bdy_tide3 module

Module to extract constituents for the input grid mapped onto output grid.

> @author: Mr. Srikanth Nagella<br>

## pybdy.tide.nemo_bdy_tide3.constituents_index(constituents, inputcons)

Convert the input contituents to index in the tidal constituents.

### Parameters

> constituents: The list of constituents available from the source data<br>
> : e.g. TPXO: [‘m2’, ‘s2’, ‘n2’, ‘k2’, ‘k1’, ‘o1’, ‘p1’, ‘q1’, ‘mf’, ‘mm’, ‘m4’, ‘ms4’, ‘mn4’]<br>

> inputcons: The dictionary of constituents from the namelist with their numbers<br>
> : e.g. {‘1’: “‘M2’”, ‘3’: “‘K2’”, ‘2’: “‘S2’”, ‘4’: “‘M4’”}<br>

### Returns

> retindx: The indices (relative to the source data list) of the dictionary items from the namelist<br>
> : e.g. [ 0. 3. 1. 10.]<br>

## pybdy.tide.nemo_bdy_tide3.nemo_bdy_tide_rot(setup, DstCoord, Grid_T, Grid_U, Grid_V, comp)

Global Tidal model interpolation onto target grid, including grid rotation.

### Parameters

> setup: settings<br>
> DstCoord: …<br>
> Grid_T : grid_type, bdy_r<br>
> Grid_U, Grid_V : bdy_i , grid_type, bdy_r<br>
> comp: dictionary of harmonics read from namelist.<br>

> e.g. {‘1’:”M2” , ‘2’:”<constituent name>”, …}<br>

### Returns

> cosz, sinz, cosu, sinu, cosv, sinv: [of constituents, number of bdy points]<br>

# pybdy.tide.nemo_bdy_tide_ncgen module

Create a Tide netcdf file ready for population.

> @author: Mr. Srikanth Nagella<br>

## pybdy.tide.nemo_bdy_tide_ncgen.CreateBDYTideNetcdfFile(filename, xb_len, x_len, y_len, h, fv, grd)

# pybdy.tide.tpxo_extract_HC module

Extract the tidal harmonic constants out of a tidal model for given locations.

[amp,Gph] = tpxo_extract_HC(Model,lat,lon,type,Cid).

> original author: Mr. Srikanth Nagella<br>

TPXO data has a grid file and then data file for harmonic heights and harmonic currents
In TPXO7.2 the resolution was sufficiently low that all the harmonics could be bundled together
In TPXO9v5 the resolution increased such that separate files are issued for each constituent

Files are processed in real and imaginary parts as they are easier to interpolate.

## *class* pybdy.tide.tpxo_extract_HC.TpxoExtract(settings, lat, lon, grid_type)

> Bases: `object`<br>

TPXO model extract_hc.c implementation in python.

### \_\_init\_\_(settings, lat, lon, grid_type)

Initialise the Extract of tide information from the netcdf Tidal files.

### generate_landmask_from_bathymetry(bathy_name)

Create a boolean mask xr.DataArray from bathymetry.

TPXO7.2 carries a binary variable called mask and a bathymetry variable
TPXO9v5 only carries the bathymetry variable

> return: mask dataarray.<br>

> Useage:<br>
> : self.grid[mask_name] = generate_landmask(bathy_name)<br>

### interpolate_constituents(nc_dataset, real_var_name, img_var_name, lon_var_name, lat_var_name, lon, lat, height_data=None, maskname=None)

Interpolate the tidal constituents along the given lat lon coordinates.

## pybdy.tide.tpxo_extract_HC.bilinear_interpolation(lon, lat, data, lon_new, lat_new)

Do a bilinear interpolation of grid where the data values are NaN’s.

## pybdy.tide.tpxo_extract_HC.interpolate_data(lon, lat, data, mask, lonlat)

Interpolate data data on regular grid for given lonlat coordinates.

## Module contents
