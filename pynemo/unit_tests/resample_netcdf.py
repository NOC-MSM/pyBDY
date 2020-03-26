# -*- coding: utf-8 -*-
"""
Resample netcdf code, used for making small low res testing datasets.
"""

import xarray as xr
import numpy as np

# subset X Y dims netcdf
ds = xr.open_dataset('unit_tests/test_data/NNA_R12_bathy_meter_bench.nc')

new_y = np.linspace(ds.y[0],ds.y[-1],100)

new_x = np.linspace(ds.x[0],ds.x[-1],85)

dsi = ds.interp(x=new_x,y=new_y)

dsi.to_netcdf('unit_tests/test_data/dst_bathy.nc')

# subset lat lon dims netcdf

ds = xr.open_dataset('unit_tests/test_data/subset_bathy.nc')

new_lon = np.linspace(ds.longitude[0],ds.longitude[-1],45)

new_lat = np.linspace(ds.latitude[0],ds.latitude[-1],30)

dsi = ds.interp(latitude=new_lat,longitude=new_lon)

dsi.to_netcdf('unit_tests/test_data/resample_bathy.nc')


# drop unneeded variables
dsd = xr.Dataset.drop_vars(ds,'zos')

# remove unwanted time
ds_sel = dsd.sel({'time':'01-01-2017'})

