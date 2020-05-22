'''
Created on 3 Oct 2014

@author: Mr. Srikanth Nagella
Netcdf writer for the bdy output
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
from netCDF4 import Dataset
import numpy as np
def write_data_to_file(filename, variable_name, data):
    """ Writes the data to the netcdf templete file.
    Keyword arguments:
    filename -- output filename
    variable_name -- variable name into which the data is written to.
    data -- data that will be written to variable in netcdf.
    """
    ncid = Dataset(filename, 'a', clobber=False, format='NETCDF4')
    count = data.shape

    three_dim_variables = ['votemper', 'vosaline', 'N1p', 'N3n', 'N5s','vobtcrtx','vozocrtx','vobtcrty','vomecrty']
    two_dim_variables = ['sossheig', 'iicethic', 'ileadfra', 'isnowthi']

    if variable_name in three_dim_variables:
        if len(count) == 3:
            count += (1, )
        ncid.variables[variable_name][:, :, :, :] = np.reshape(data, count)[:, :, :, :]
    elif variable_name in two_dim_variables:
        if len(count) == 2:
            count += (1, )
        elif len(count) == 1:
            count += (1, 1, )
        ncid.variables[variable_name][:, :, :] = np.reshape(data, count)[:, :, :]
    elif variable_name == 'time_counter':
        ncid.variables[variable_name][:] = data[:]
    else:
        if len(count) == 1:
            ncid.variables[variable_name][:] = data[:]
        elif len(count) == 2:
            ncid.variables[variable_name][:, :] = data[:, :]
        elif len(count) == 3:
            ncid.variables[variable_name][:, :, :] = data[:, :, :]

    ncid.close()
