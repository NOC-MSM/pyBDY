'''
NcML reading implementation using pyjnius
@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
#Loading of NCML jar file
import os
import string
import logging
import numpy as np
import jnius_config
from netCDF4 import netcdftime


ncmlpath, file_name = os.path.split(__file__)
ncmlpath = os.path.join(ncmlpath, "jars", "netcdfAll-4.6.jar") 
jnius_config.set_classpath('.',ncmlpath)

try:
    if os.environ['http_proxy'] is not None:
        #split the proxy name and port
        proxylist = string.split(os.environ['http_proxy'],':')
        proxy_host = proxylist[0]
        proxy_port = proxylist[1]        
        jnius_config.add_options('-Dhttp.proxyHost='+proxy_host,'-Dhttp.proxyPort='+proxy_port)
except:
    print "Didn't find a proxy environment variable"
NetcdfDataset = None
NcMLReader = None
Section = None
try:
    from jnius import autoclass
    def init_jnius():
        global NetcdfDataset
        global NcMLReader
        global Section
        NetcdfDataset = autoclass('ucar.nc2.dataset.NetcdfDataset')
        NcMLReader = autoclass('ucar.nc2.ncml.NcMLReader')
        Section = autoclass('ucar.ma2.Section')
    init_jnius()
except ImportError:
    print 'Warning: Please make sure pyjnius is installed and jvm.dll/libjvm.so/libjvm.dylib is in the path'

# TODO: sort out time variable initalisation below (hacked to work with CMEMS and NEMO benchmark)

import sys
from pynemo import nemo_bdy_setup as setup
Setup = setup.Setup(sys.argv[2]) # default settings file
settings = Setup.settings
if 'use_cmems' in settings:
    if settings['use_cmems'] == True:
        time_counter_const = "time"
    if settings['use_cmems'] == False:
        time_counter_const = "time_counter"
if 'use_cmems' not in settings:
    time_counter_const = "time_counter"
del settings, Setup


class Reader(object):
    """ This class is the high level of object for the NCML reader, from here using grid type
    will return the grid data
    usage: 
        >>> reader = Reader("NCML Filename")
        >>> reader['t']['votemper'][:,:,:,:]
    """
    grid_type_list = ['t','u','v','i']
    time_counter = time_counter_const
    def __init__(self, uri, time_adjust):
        self.uri = uri
        self.time_adjust = time_adjust
        try:
            self.dataset = NetcdfDataset.openFile(self.uri, None)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.uri)
        self.grid = GridGroup(self.uri,self.dataset)
        self._get_source_timedata(self.grid,self.time_adjust)
    def __del__(self):
        """ Destructor close the netcdf file """
        if self.dataset is not None:
            self.dataset.close()
                    
    def __getitem__(self,val):
        """ Returns the grid. it doesn't matter what type of grid is requested all the
        variables are in the same object. This is to keep it consistent with the Local directory
        reader"""
        if val in self.grid_type_list:
            return self.grid
        else:
            return None    
        
    def _get_source_timedata(self, grid, t_adjust):
        """ Get the source time data information. builds up sourcedata objects of a given grid """
        timevar = grid[self.time_counter]
        grid.time_counter = timevar[:]+t_adjust
        grid.date_counter = []
        for index in range(0,len(grid.time_counter)):            
            grid.date_counter.append(netcdftime.utime(grid.units,
                                                      grid.calendar).num2date(grid.time_counter[index])) 

    def close(self):
        """ This is not yet implemented. TODO: keep the netcdf file open until its expicitly 
        closed """
        pass 
    
class GridGroup(object):
    """ This class is to provide an indirection to the grid type. since ncml
    file has aggregation of all the variables this is just a place holder"""
    logger = logging.getLogger(__name__)
    def __init__(self, filename, dataset):
        """ This class is the source data that holds the dataset information """
        self.file_name = filename
        self.units = None
        self.calendar = None
        self.date_counter = None
        self.seconds = None
        self.time_counter = None
        self.dataset = dataset
        self.update_atrributes()

    def __del__(self):
        self.dataset = None
            
    def __getitem__(self, val):
        """ Returns the data requested """
        try:
            return Variable(self.dataset, val)
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_name)
        return None
       
    def get_meta_data(self, variable, source_dic):
        """ Returns a dictionary with meta data information correspoinding to the variable """
        #source_dic = {}
        try:
            dvar = self.dataset.findVariable(variable)
            if dvar is None:
                raise KeyError()
            source_dic['sf'] = 1
            source_dic['os'] = 0
            mv_attr = dvar.findAttributeIgnoreCase('missing_value')
            if mv_attr is not None:
                source_dic['mv'] = mv_attr.getValues().copyToNDJavaArray()
            sf_attr = dvar.findAttributeIgnoreCase('scale_factor')
            if sf_attr is not None:
                source_dic['sf'] = sf_attr.getValues().copyToNDJavaArray()
            os_attr = dvar.findAttributeIgnoreCase('add_offset')
            if os_attr is not None:
                source_dic['os'] = os_attr.getValues().copyToNDJavaArray()
            fv_attr = dvar.findAttributeIgnoreCase('_FillValue')
            if fv_attr is not None:
                source_dic['mv'] = fv_attr.getValue(0)
            return source_dic            
        except KeyError:
            self.logger.error('Cannot find the requested variable '+variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_name)
        return None          

    def update_atrributes(self):
        """ Updates the units and calendar information for the grid """        
        try:
            var =  Variable(self.dataset, time_counter_const)
            self.units = var.get_attribute_value("units")
            self.calendar = var.get_attribute_value("calendar")
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_name)
        return None
       
class Variable(object):

    def __init__(self, dataset, variable):
        self.logger = logging.getLogger(__name__)
        self.dataset = dataset
        self.variable = variable
        
    def __str__(self):        
        return "PyNEMO NcML Object from file: %s and variable %s" % self.file_name, self.variable

    def __len__(self):
        """ Returns the length of the variable """
        try:
            dvar = self.dataset.findVariable(self.variable) 
            if dvar is None:
                raise KeyError()
            val  = dvar.getDimension(0).getLength()
            return val
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        return None
            
    def __getitem__(self, val):
        """ Returns the data requested """
        if type(val) != tuple:
            val = (val,)
        try:
            dvar = self.dataset.findVariable(self.variable)
            if dvar is None:
                raise KeyError()
            dims = dvar.getShape()
            # get the requested slice and extract that information from jnius
            # Check if the request data is with in the dataset dimensions
            start = [0]*len(dims)
            stop = dims
            stride = [1]*len(dims)
            new_dims = tuple()
            np_input = False
            for idx in range(0,len(dims)):
                try:
                    if val[idx].start is not None:
                        start[idx] = val[idx].start
                    if val[idx].step is not None:
                        stride[idx] = val[idx].step
                    if val[idx].stop is not None:
                        if val[idx].stop == -1:
                            val[idx] = stop[idx] - 1
                        elif val[idx].stop > stop[idx]:
                            val[idx].stop = stop[idx]
                        stop[idx] = (val[idx].stop - start[idx])//stride[idx]
                        if (val[idx].stop - start[idx])%stride[idx] != 0:
                            stop[idx] = stop[idx] + 1
                    new_dims = new_dims+(stop[idx],)
                except IndexError:
                    pass
                except AttributeError:
                    if isinstance(val[idx],int):
                        start[idx] = val[idx]
                        stop[idx] = 1
                    elif isinstance(val[idx],np.ndarray):
                        new_dims = new_dims+(val[idx].shape)
                        np_input = True
            # Create a section object that represents the requested slice 
            start = [int(i) for i in start]
            stop = [int(i) for i in stop]
            stride = [int(i) for i in stride]
            selected_section = Section(start,stop,stride)
            data_array = dvar.read(selected_section)
            retval = data_array.copyToNDJavaArray() 
            #TODO: copy it into numpy instead of Java array and then convert to numpy
            # convert to numpy array
            retval = np.asarray(retval, dtype='float')
            self.logger.info(retval.shape)
            if np_input: #if an array is passed as selection
                ret_dim_list = ()
                for idx in range(0,len(dims)):
                    if isinstance(val[idx], np.ndarray): 
                        ret_dim_list2 = ret_dim_list+(val[idx],)
                        # can't do all the reductions at once due to Index Error: shape mismatch
                        retval = retval[ret_dim_list2]  
                    ret_dim_list = ret_dim_list+(slice(None,None,None),)
                self.logger.info(ret_dim_list)                        
                self.logger.info(retval.shape)
                self.logger.info(ret_dim_list)
            # reshape to reflect the request
            retval = np.reshape(retval, new_dims)
            return retval
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_name)
        return None
         
    def _get_dimensions(self):
        """ Returns the dimensions of the variables """
        try:
            dvar = self.dataset.findVariable(self.variable)
            if dvar is None:
                raise KeyError()
            retval = tuple(dvar.getDimensionsString().split(' '))
            return retval
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        return None     
    
    def get_attribute_value(self, attr_name):
        """ Returns the attribute value of the variable """
        try:
            dvar = self.dataset.findVariable(self.variable)
            if dvar is None:
                raise KeyError()
            attr = dvar.findAttributeIgnoreCase(attr_name)
            if attr is not None:
                retval = attr.getValue(0)            
            return retval
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        return None  
    
    
class NcMLFile(object):
    def __init__(self,filename):
        self.dataset = None
        try:
            self.dataset = NetcdfDataset.openFile(filename, None)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+filename)
    
    def __getitem__(self,val):
        return Variable(self.dataset,val)
    
    def close(self):
        if self.dataset is not None:
            self.dataset.close()
