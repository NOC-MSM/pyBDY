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
Generic file loader factory.

@author: Mr. Srikanth Nagella
"""

# Global Imports
import os

from netCDF4 import Dataset

from pybdy.reader.directory import Reader as DirectoryReader
from pybdy.reader.ncml import NcMLFile

# Local Imports
from pybdy.reader.ncml import Reader as NcMLReader


def GetReader(uri, t_adjust, reader_type=None):
    if reader_type is None:
        print(uri)
        if uri.endswith(".ncml"):
            reader_type = "NcML"
        elif os.path.isdir(uri):
            reader_type = "Directory"
        else:
            print("Error input should be a NcML file or URL or a Local directory")
            return None
    if reader_type == "NcML":
        return NcMLReader(uri, t_adjust)
    else:
        return DirectoryReader(uri, t_adjust)


class NetCDFFile(object):
    def __init__(self, filename):
        self.nc = Dataset(filename)

    def __getitem__(self, val):
        return self.nc.variables[val]

    def close(self):
        self.nc.close()


def GetFile(uri):
    if uri.endswith(".ncml"):
        return NcMLFile(uri)
    else:
        return NetCDFFile(uri)


# from netcdf import GetFile as netcdf_get_file
# from netcdf import GetRepository as netcdf_repository
# from ncml import GetFile as ncml_get_file
# from ncml import GetRepository as ncml_repository
#
#
#
# import os
# def GetRepository(src_dir, grid, t_adjust, reader_type="netcdf"):
#     """ Generic method to return the repository either netcdf or ncml based on some
#     logic, now passing as reader_type to choose """
#     if reader_type == "netcdf":
#         return netcdf_repository(src_dir, grid, t_adjust)
#     elif reader_type == "ncml":
#         return ncml_repository(src_dir, grid, t_adjust)
#
# def GetFile(file_path, reader_type="netcdf"):
#     """ Generic method to return the file object either netcdf or ncml based on some
#     logic, now passing as reader_type to choose"""
#     if reader_type == "netcdf":
#         return netcdf_get_file(file_path)
#     elif reader_type == "ncml":
#         return ncml_get_file(file_path)
