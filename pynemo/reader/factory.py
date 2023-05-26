"""
Generic file loader factory.

@author: Mr. Srikanth Nagella
"""

# Global Imports
import os

from netCDF4 import Dataset

from pynemo.reader.directory import Reader as DirectoryReader
from pynemo.reader.ncml import NcMLFile

# Local Imports
from pynemo.reader.ncml import Reader as NcMLReader


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
