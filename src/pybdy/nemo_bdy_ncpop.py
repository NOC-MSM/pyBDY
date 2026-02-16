# ===================================================================
# Copyright 2025 National Oceanography Centre
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================

"""
Created on 3 Oct 2014.

@author: Mr. Srikanth Nagella
Netcdf writer for the bdy output
"""
import numpy as np
from netCDF4 import Dataset


def write_data_to_file(filename, variable_name, data):
    """
    Write the data to the netcdf templete file.

    Parameters
    ----------
    filename -- output filename
    variable_name -- variable name into which the data is written to.
    data -- data that will be written to variable in netcdf.
    """
    ncid = Dataset(filename, "a", clobber=False, format="NETCDF4")
    count = data.shape

    three_dim_variables = ["votemper", "vosaline", "N1p", "N3n", "N5s"]
    two_dim_variables = [
        "sossheig",
        "vobtcrtx",
        "vobtcrty",
        "ice1",
        "ice2",
        "ice3",
    ]
    # print(filename)
    # print(variable_name)
    if variable_name in three_dim_variables:
        if len(count) == 3:
            count += (1,)
        ncid.variables[variable_name][:, :, :, :] = np.reshape(data, count)[:, :, :, :]
    elif variable_name in two_dim_variables:
        if len(count) == 2:
            count += (1,)
        elif len(count) == 1:
            count += (
                1,
                1,
            )
        ncid.variables[variable_name][:, :, :] = np.reshape(data, count)[:, :, :]
    elif variable_name == "time_counter":
        ncid.variables[variable_name][:] = data[:]
    else:
        if len(count) == 1:
            ncid.variables[variable_name][:] = data[:]
        elif len(count) == 2:
            ncid.variables[variable_name][:, :] = data[:, :]
        elif len(count) == 3:
            ncid.variables[variable_name][:, :, :] = data[:, :, :]

    ncid.close()
