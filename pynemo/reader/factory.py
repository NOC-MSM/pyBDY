'''
This is generic file loader factory.

@author: Mr. Srikanth Nagella
'''

#Global Imports
import os
#Local Imports
from pynemo.reader.ncml import Reader as NcMLReader
from pynemo.reader.ncml import NcMLFile
#from pynemo.reader.directory import Reader as DirectoryReader
import logging

from netCDF4 import Dataset
logger = logging.getLogger(__name__)
def GetReader(uri, t_adjust, reader_type=None):
    if reader_type is None:
        logger.info(uri)
        if uri.endswith(".ncml"):
            reader_type = "NcML"
        elif os.path.isdir(uri):
            # directory reading directly is no longer supported please use NCML file to define directory
            #reader_type = "Directory"
            logger.error("Directory Reading is no longer supported without using NCML file to define location")
            raise Exception("Directory Reading is no longer supported without using NCML file to define location")
        else:
            logger.error("Error input: should be a NcML file")
            raise Exception("Error input: should be a NcML file")
    if reader_type == "NcML":
        return NcMLReader(uri,t_adjust)
    else:
        logger.error("Directory Reading is no longer supported without using NCML file to define location")
        raise Exception("Directory Reading is no longer supported without using NCML file to define location")
        #return DirectoryReader(uri, t_adjust)
    
    
class NetCDFFile(object):
    def __init__(self, filename):
        self.nc = Dataset(filename)
    
    def __getitem__(self,val):
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