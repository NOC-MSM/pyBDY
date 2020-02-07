##################################################
# Written by John Kazimierz Farey, Sep 2012      #
# Port of Matlab code of James Harle             #
# #                                            # #
# Init with source directory for netcdf files    #
# Method to generates time/file list information #
# for a particular grid                          #
##################################################

from os import listdir

from netCDF4 import Dataset, netcdftime
import logging

class SourceTime:

    def __init__(self, src_dir):
        self.src_dir = src_dir
        self.logger = logging.getLogger(__name__)
    # returns a list of all the relevant netcdf files
    def _get_dir_list(self, grid):
        fend = 'd05%s.nc' %grid.upper()
        dir_list = listdir(self.src_dir)
        for i in range(len(dir_list)):
            if dir_list[i][-7:] != fend:
                dir_list[i] = ''
            else:
                dir_list[i] = self.src_dir + dir_list[i]

        dir_list.sort()
            
        return [_f for _f in dir_list if _f]
    
    # Returns list of dicts of date/time info
    # I assume there is only one date per file
    # Each date is datetime instance. to get day etc use x.day
    # They should be in order
    # Matlab var dir_list is incorporated into src_time    
    def get_source_time(self, grid, t_adjust):
        dir_list = self._get_dir_list(grid)
        src_time = []
        for f in range(len(dir_list)):
            self.logger.debug('get_source_time: %s', dir_list[f])
            nc = Dataset(dir_list[f], 'r')
            varid = nc.variables['time_counter']
            f_time = {}
            f_time['fname'] = dir_list[f]

            # First 2 values are in unicode. Pray.
            f_time['units'] = varid.units
            f_time['calendar'] = varid.calendar
            raw_date = varid[0] + t_adjust
            f_time['date'] = netcdftime.num2date(raw_date, f_time['units'], 
                                                 f_time['calendar'])

            src_time.append(f_time)
        
        return src_time
    

