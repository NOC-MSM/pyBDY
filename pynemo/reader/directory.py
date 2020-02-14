'''
This is an abstraction for the data repository
@author: Mr. Srikanth Nagella
'''
from os import listdir
import numpy as np
from netCDF4 import Dataset
from cftime import utime 
import copy
import logging
class Reader(object):
    '''
    This provides a reader for all the files in the directory as one
    single object.
    Usage:
        >>> reader = Reader("Folder path")
        >>> reader['t']['votemper'][:,:,:,:]
    '''
    grid_type_list = ['t','u','v','i']
    def __init__(self, directory, time_adjust):
        '''
        This takes in directory path as input and returns the required information to the
        bdy.
        Keyword arguments:
        directory -- The directory in which to look for the files
        time_adjust -- amount of time to be adjusted to the time read from file.
        '''
        self.directory = directory
        self.day_interval = 1
        self.hr_interval = 0
        self.grid_source_data = {}
        for grid_type in self.grid_type_list:
            self.grid_source_data[grid_type] = self._get_source_timedata(grid_type, time_adjust)
        if self.grid_type_list is not None and len(self.grid_source_data) != 0:
            self._calculate_time_interval()

    def _get_dir_list(self, grid):
        """
        This method scans the directory for a input grid related netcdf files. i.e ending with
        the grid name.
        Keyword arguments:
        grid -- grid name eg. 't','v','u','i'
        """
        fend = '%s.nc' %grid.upper()
        dir_list = listdir(self.directory)
        for i in range(len(dir_list)):
            if dir_list[i][-4:] != fend:
                dir_list[i] = ''
            else:
                dir_list[i] = self.directory + dir_list[i]

        dir_list.sort()
        return [_f for _f in dir_list if _f]

    def _delta_time_interval(self, time1, time2):
        """ Get the difference between the two times in days and hours"""
        timedif = time2 - time1
        days = timedif / (60 * 60 * 24)
        hrs = timedif % (60 * 60 * 24)
        hrs = hrs / (60 * 60)
        return days, hrs
    
    def _get_source_timedata(self, grid, t_adjust):
        """ Get the source time data information. builds up sourcedata objects of a given grid """
        dir_list = self._get_dir_list(grid)
        group = GridGroup()
        group.data_list = []
        group.time_counter = []        
        group.date_counter = []
        for filename in dir_list:   
            nc = Dataset(filename, 'r')
            varid = nc.variables['time_counter'] 
            for index in range(0,len(varid)):
                x = [filename, index]
                group.data_list.append(x)
                group.time_counter.append(varid[index]+t_adjust)
                group.date_counter.append(utime(varid.units,
                                                           varid.calendar).num2date(varid[index]+t_adjust))
            group.units = varid.units
            group.calendar = varid.calendar
            nc.close()
        tmp_data_list = copy.deepcopy(group.data_list)
        tmp_time_counter = copy.deepcopy(group.time_counter)
        for index in range(len(group.time_counter)):
            tmp_data_list[index] = group.data_list[index]
            tmp_time_counter[index] = group.time_counter[index]
        group.data_list = tmp_data_list
        group.time_counter = tmp_time_counter
        return group

    def _calculate_time_interval(self):
        """ This method will calculate the time interval of the each grid. If all the grids
        get the same interval then it sets it to the days and hours otherwise it throws an
        error"""
        days = set()
        hrs = set()
        for grid_type in list(self.grid_source_data.keys()):
            day, hr = self._delta_time_interval(self.grid_source_data[grid_type].time_counter[0],
                                                self.grid_source_data[grid_type].time_counter[1])
            days.add(day)
            hrs.add(hr)
        if len(days) != 1 or len(hrs) != 1:
            raise Exception('All the Grid time interval is not same')
        self.day_interval = list(days)[0]
        self.hr_interval = list(hrs)[0] 
        
    def __getitem__(self,val):
        if val in self.grid_type_list:
            return self.grid_source_data[val]
        else:
            return None
    
class GridGroup:
    def __init__(self):
        pass
    def __getitem__(self,val):
        return Variable(self.data_list, val)
    
    def get_meta_data(self, variable, source_dic):
        """ Returns a dictionary with meta data information correspoinding to the variable """
        #source_dic = {}
        try:
            var = self.__getitem__(variable)
            attrs = var.get_attribute_values(['missing_value','scale_factor', 'add_offset', '_FillValue'])
            source_dic['sf'] = 1
            source_dic['os'] = 0
            if attrs['missing_value'] is not None:            
                source_dic['mv'] = attrs['missing_value']
            if attrs['scale_factor'] is not None:
                source_dic['sf'] = attrs['scale_factor']
            if attrs['add_offset'] is not None:                            
                source_dic['os'] = attrs['add_offset']
            if attrs['_FillValue'] is not None:                
                source_dic['fv'] = attrs['_FillValue']
            return source_dic            
        except KeyError:
            self.logger.error('Cannot find the requested variable '+variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_name)
        return None  
    
class Variable(object):
    time_counter_const = "time_counter"
    def __init__(self, filenames, variable):
        self.variable = variable
        self.file_names = filenames
        self.dimensions = self._get_dimensions()
        self._set_time_dimension_index()
        self.logger = logging.getLogger(__name__)
        
    def __str__(self):
        return "PyNEMO Data Object from files: %s and variable %s" % self.file_names, self.variable
    
    def __len__(self):
        """ Returns the length of the variable """
        try:
            dataset = Dataset(self.file_names[0], 'r')
            dvar = dataset.variables[self.variable]
            val  = len(dvar)
            dataset.close()
            return val
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_names[0])
        return None
            
    def __getitem__(self, val):
        """ Returns the data requested """
        try:
            if self.time_dim_index == -1:
                dataset = Dataset(self.file_names[0][0], 'r')
                dvar = dataset.variables[self.variable]
                retval  = dvar[val]
                dataset.close()
                return retval
            else:
                # select all the files that are required for the selected range
                # read the data and merge them
                val = list(val)
                for index in range(len(val)):
                    if type(val[index]) is not slice: 
                        if type(val[index]) is not np.ndarray:
                                val[index] = slice(val[index], val[index] + 1)
                val = tuple(val)
                start = val[self.time_dim_index].start
                stop = val[self.time_dim_index].stop
                step = val[self.time_dim_index].step
                if step is None:
                    step = 1
                if start is None:
                    start = 0
                if stop is None:
                    stop = len(self.file_names)
                finalval = None
                for index in range(start, stop, step):
                    dataset = Dataset(self.file_names[index][0], 'r')
                    val = list(val)
                    val[self.time_dim_index] = slice(self.file_names[index][1], self.file_names[index][1] + 1)
                    val = tuple(val)
                    dvar = dataset.variables[self.variable]
                    retval = dvar[val]
                    if finalval is None:
                        finalval = retval
                    else:
                        finalval = np.concatenate((finalval, retval), axis=self.time_dim_index)
                    dataset.close()
                return finalval

        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_names)
        return None
      
    def get_attribute_values(self, attr_name):
        """ Returns the attribute value of the variable """
        try:
            dataset = Dataset(self.file_names[0][0], 'r')
            dvar = dataset.variables[self.variable]
            ret_val = {}
            for name in attr_name:
                try:
                    val = dvar.getncattr(name)
                    ret_val[name]=val
                except AttributeError:
                    ret_val[name] = None
            dataset.close()
            return ret_val
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_names[0])
        return None
            
    def _get_dimensions(self):
        """ Returns the dimensions of the variables """
        try:        
            dataset = Dataset(self.file_names[0][0], 'r')
            dvar = dataset.variables[self.variable]
            return dvar.dimensions
        except KeyError:
            self.logger.error('Cannot find the requested variable '+self.variable)
        except (IOError, RuntimeError):
            self.logger.error('Cannot open the file '+self.file_names[0])
        return None
    
    def _set_time_dimension_index(self):
        """ Sets the time dimension index """
        self.time_dim_index = -1
        for index in range(len(self.dimensions)):
            if self.dimensions[index] == self.time_counter_const:
                self.time_dim_index = index
        

