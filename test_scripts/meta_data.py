# -*- coding: utf-8 -*-
"""
Set of functions to download CMEMS files using FTP (for static mask data) and MOTU (for subsetted variable data).

"""

from netCDF4 import Dataset
import re
# list of datasets to check
datasets = [ "http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_data/ORCA025-N206_19791101d05T.nc",
             "http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_data/ORCA025-N206_19791101d05U.nc",
             "http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_data/ORCA025-N206_19791101d05V.nc",
             "http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_data/ORCA025-N206_19791101d05I.nc"
            ]

# list of strings to catagorise variable names... each entry can have multiple entries.
# NOTE list in each dict entry is in a specifc order where long names go first e.g. latitude is before lat. This is to
# stop errors in selecting names. e.g. lat would also be valid for latitude and nav_lat so trying lat needs to be after those options
# DOUBLE NOTE order of dicts in check list is also important as it can result in false ID's e.g. ice data for some reason has long name
# sea surface height so if SSH is in dict before ice variables it will assign ice variable names to SSH.

chk_list = {'temperature': ['temp'],
            'salinity': ['sal'],
            'ice_thic': ['icethic'],
            'snow_thic': ['snowthi'],
            'ileadfra': ['leadfra'],
            'SSH': ['surface', 'sea'],
            'depth': ['depth'],
            'time': ['time', 'counter'],
            'latitude': ['latitude', 'nav_lat','lat','y'],
            'longitude': ['longitude','nav_lon','lon','x'],
            'depth': ['depth'],
            'Ucomponent': ['zonal', 'current'],
            'Vcomponent': ['meridional', 'current'],
            'windstress-i':['i-axis'],
            'windstress-j':['j-axis'],
            }

# function to use regex to find if string is in variable name or if not check long name. Case of string is ignored
# Attribute errors are common due to long name not existing in some datasets at the moment this error is passed (maybe log?)
def data_chk(data, str, key):
    for i in range(len(str)):
        try:
            chk = re.search(str[i], data[key].name, re.IGNORECASE)
            if chk is None:
                chk = re.search(str[i], data[key].long_name, re.IGNORECASE)
            return chk
        except AttributeError:
            pass

i = 0
meta_dataset = {}

for dat in datasets:
    # open netcdf dataset
    F = Dataset(dat)
    # extract variable meta data and dimension meta data
    meta = F.variables
    dims = F.dimensions
    # create empty dict to save catagorised data
    meta_dataset['dataset'+str(i+1)] = {}
    meta_dataset['dataset'+str(i+1)]['var_names'] = {}
    meta_dataset['dataset'+str(i+1)]['dim_names'] = {}

    # for all variable names, compare strings on chk list and write key to meta dict on first match
    for key in meta:
        for chk_key,chk in chk_list.items():
            var_match = data_chk(meta,chk,key)
            if var_match is not None:
                meta_dataset['dataset'+str(i+1)]['var_names'][chk_key] = key
                break
    if len(meta_dataset['dataset'+str(i+1)]['var_names']) != len(meta):
        print('not all variables matched for dataset '+str(i+1))

    # for all dimension names, compare strings on chk list and write key to meta dict on first match
    for key in dims:
        for chk_key,chk in chk_list.items():
            dim_match = data_chk(dims,chk,key)
            if dim_match is not None:
                meta_dataset['dataset'+str(i+1)]['dim_names'][chk_key] = key
                break
    if len(meta_dataset['dataset'+str(i+1)]['dim_names']) != len(dims):
        print('not all dimensions matched for dataset '+str(i+1))
    i = i + 1
    # close netcdf file and print meta dict
    F.close()

print(meta_dataset)


