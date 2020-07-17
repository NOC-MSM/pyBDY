'''
Mask Class to hold the mask information and operation on mask

@author: Mr. Srikanth Nagella
'''

# pylint: disable=E1103
# pylint: disable=no-name-in-module
import numpy as np
from netCDF4 import Dataset
import logging
from scipy import ndimage
import matplotlib.pyplot as plt
from pynemo.utils import gcoms_break_depth
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore

class Mask(object):
    """This is a Mask holder. which reads from a netCDF bathymetry file and
    stores it in 'data' member variable"""

    min_depth = 200.0
    shelfbreak_dist = 200.0
    mask_type = 0

    
    def __init__(self, bathymetry_file=None, mask_file=None, min_depth = 200.0, shelfbreak_dist = 200.0):
        """Initialises the Mask data"""
        self.data = None
        self.bathy_data = None
        self.mask_file = None
        self.logger = logging.getLogger(__name__)
        self.set_mask_file(mask_file)
        self.set_bathymetry_file(bathymetry_file)
        self.min_depth = min_depth
        self.shelfbreak_dist = shelfbreak_dist


    def set_mask_file(self, mask_file):
        """
	Reads the mask data from the mask file
	Assumes the mask file is 2D
	"""
        self.mask_file = mask_file
        #if mask file is not set then reset the data
        if self.mask_file == None:
            self.data = None
            return

        try:
            mask_nc = Dataset(str(self.mask_file), mode="r")
            data = mask_nc.variables['mask']
            self.data = data[:,:]
        except KeyError:
            self.logger.error('Mask file missing have mask variable')
            raise
        except (IOError, RuntimeError):
            self.logger.error('Cannot open mask file '+self.mask_file)
            self.data = None
            raise

    def set_bathymetry_file(self, bathy_file):
        """ This reads the bathymetry file and sets the land to 0 and ocean to 1 """
        if bathy_file == None:
            return

        try:
            self.bathymetry_file = str(bathy_file)
            #open the bathymetry file
            self.bathy_nc = Dataset(self.bathymetry_file)
            try:
                self.lon = np.asarray(self.bathy_nc.variables['nav_lon'])
                self.lat = np.asarray(self.bathy_nc.variables['nav_lat'])
            except:
                self.lon = np.asarray(self.bathy_nc.variables['longitude'])
                self.lat = np.asarray(self.bathy_nc.variables['latitude'])
                # expand lat and lon 1D arrays into 2D array matching nav_lat nav_lon
                self.lon = np.tile(self.lon, (np.shape(self.lat)[0], 1))
                self.lat = np.tile(self.lat, (np.shape(self.lon)[1], 1))
                self.lat = np.rot90(self.lat)

            try:
                self.bathy_data = self.bathy_nc.variables['Bathymetry'][:,:]
                self.data_units = self.bathy_nc.variables['Bathymetry'].units
            except KeyError:
                self.bathy_data = self.bathy_nc.variables['deptho'][:,:]
                self.data_units = self.bathy_nc.variables['deptho'].units
            except AttributeError:
                self.logger.warning('Bathymetry Units unknown....')
                self.data_units = "unknown"
            if self.data is None:
                try:
                    self.data = self.bathy_nc.variables['Bathymetry']
                except:
                    self.data = self.bathy_nc.variables['deptho']
                if sum(self.data[:, 0]) + sum(self.data[0, :]) + sum(self.data[:, -1]) + sum(self.data[-1, :]) == 0:
                    raise BaseException('zeros around boundaries of bathymetry is not supported by PyNEMO mask generator')
                self.data = np.asarray(self.data[:, :])
                self.data = np.around((self.data + .5).clip(0, 1))
                #apply default 1px border
                self.apply_border_mask(1)
        except KeyError:
            self.logger.error('Bathymetry file does not have Bathymetry variable')
            raise
        except (IOError, RuntimeError):
            self.logger.error('Cannot open bathymetry file '+self.bathymetry_file)
            raise



    def save_mask(self, mask_file):
        """Reads the mask data from the mask file"""
        if mask_file == None:
            mask_file = self.mask_file

        try:
            self.logger.info('Writing mask data to %s' % mask_file)            
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Saving....")
            msgbox.setText("Writing mask data to file, please wait...")
            msgbox.setWindowModality(QtCore.Qt.NonModal)
            msgbox.show()           
            mask_nc = Dataset(str(mask_file), mode="w")
            mask_nc.createDimension('y', size=len(self.bathy_nc.dimensions['y']))
            mask_nc.createDimension('x', size=len(self.bathy_nc.dimensions['x']))
            nav_lat = mask_nc.createVariable('nav_lat', 'f4', ('y','x',))
            nav_lon = mask_nc.createVariable('nav_lon', 'f4', ('y','x',))
            mask_var = mask_nc.createVariable('mask', 'f4', ('y','x',))            
            mask_var[...] = self.data
            nav_lat[...] = self.lat
            nav_lon[...] = self.lon
            msgbox.close()
        except (IOError, RuntimeError):
            QMessageBox.information(None,"pyNEMO","Failed to write the mask file, please check the permissions")            
            self.logger.info('Cannot open mask file for writing '+mask_file)
            raise

    def apply_border_mask(self, pixels):
        """ pixels is number of pixels in the border that need applying mask"""
        if self.data is not None and pixels < self.data.shape[0] and pixels < self.data.shape[1]:
            if pixels != 0:
                tmp = np.ones(self.data.shape, dtype=bool)
                tmp[pixels:-pixels, pixels:-pixels] = False
            else:
                tmp = np.zeros(self.data.shape, dtype=bool)
            self.reset_mask()
            self.data = self.data * -1
            self.data[tmp] = -1
            self.select_the_largest_region()

    def add_mask(self, index, roi):
        """ Adds the masks for the given index values depending on the type of mask selected"""
        out_index = None
        if self.mask_type == None or self.mask_type == 0:
            out_index = index
        elif self.mask_type == 1: #maximum depth
            out_index = self._get_bathy_depth_index(index,self.min_depth)            
            out_index = self.remove_small_regions(out_index)
            out_index = self.fill_small_regions(out_index)
        elif self.mask_type == 2: # shelf break
            #dummy, shelf_break = gcoms_break_depth.gcoms_break_depth(self.bathy_data[index])
            #out_index = self._get_bathy_depth_index(index, shelf_break)
            out_index = gcoms_break_depth.polcoms_select_domain(self.bathy_data, self.lat,
                                                                self.lon, roi, self.shelfbreak_dist)
            out_index = np.logical_and(index, out_index)
            out_index = self.remove_small_regions(out_index)   
            #out_index = self.fill_small_regions(out_index)                    
        #if index is not empty        
        if out_index is not None:                       
            tmp = self.data[out_index]
            tmp[tmp == -1] = 1
            self.data[out_index] = tmp  
        self.select_the_largest_region()         
                
        
    def _get_bathy_depth_index(self, index, depth):
        """ returns the indices from the input field `index` which have bathymetry depth greater
	    than the input field `depth`
	"""
        output_index = self.bathy_data < depth
        output_index = np.logical_and(index,output_index)
        return output_index
    
    def remove_mask(self,index,roi):
        """ Removes the mask for the given index values depending on the type of mask selected """
        out_index = None
        if self.mask_type == None or self.mask_type == 0:
            out_index = index
        elif self.mask_type == 1: #minimum depth
            out_index = self._get_bathy_depth_index(index,self.min_depth)
            out_index = self.remove_small_regions(out_index)
            out_index = self.fill_small_regions(out_index)            
        elif self.mask_type == 2: # shelf break
#            dummy, shelf_break = gcoms_break_depth.gcoms_break_depth(self.bathy_data[index])
#            out_index = self._get_bathy_depth_index(index, shelf_break)
            out_index = gcoms_break_depth.polcoms_select_domain(self.bathy_data, self.lat,
                                                                self.lon, roi, self.shelfbreak_dist)
            out_index = np.logical_and(index, out_index)
            out_index = self.remove_small_regions(out_index)  
            #out_index = self.fill_small_regions(out_index)  
        tmp = self.data[out_index]
        tmp[tmp == 1] = -1
        self.data[out_index] = tmp
        self.select_the_largest_region()
    
    def set_minimum_depth_mask(self, depth):
        self.min_depth = depth

    def set_mask_type(self, mask_type):
        """ Sets the mask type """
        self.mask_type = mask_type
        
    def remove_small_regions(self, index):
        """ Removes the small regions in the selection area and takes only the largest area
            for mask"""
        #prepare the regions
        mask_data = np.zeros(self.data.shape)
        mask_data[index] = self.data[index]        
        #connected components
        label_mask, num_labels = ndimage.label(mask_data)
        mean_values = ndimage.sum(np.ones(self.data.shape),label_mask,list(range(1, num_labels+1)))
        max_area_mask = None
        if mean_values.size != 0:
            max_area_index = np.argmax(mean_values)+1
            max_area_mask = label_mask == max_area_index
        return max_area_mask
    
    def fill_small_regions(self, index):
        """ This method fills the small regions of the selection area and fills them up """
        #prepare the region with mask and land as 0, ocean as 1
        mask_data = np.zeros(self.data.shape)
        mask_data[index] = 1
        #remove the small unmask holes
        mask_withoutholes = ndimage.binary_fill_holes(mask_data)
        return np.where(mask_withoutholes==1)
        
    def reset_mask(self):
        """ This method resets the data back to no mask with land fill """
        self.data = np.around((self.bathy_data + .5).clip(0, 1))*-1
        
    def select_the_largest_region(self):
        """ This method tidies up the mask by selecting the largest masked region. this is to avoid two disconnected masked regions """
        mask_data = np.zeros(self.data.shape)
        mask_data[:,:] = self.data[:,:]
        mask_data[mask_data == -1] = 0
        #connected components
        label_mask, num_labels = ndimage.label(mask_data)
        if num_labels == 0: #if mask is empty/clear
            return
        mean_values = ndimage.sum(np.ones(self.data.shape),label_mask,list(range(1, num_labels+1)))
        max_area_mask = None
        if mean_values.size != 0:
            max_area_index = np.argmax(mean_values)+1
            max_area_mask = label_mask == max_area_index
        self.data = np.around((self.bathy_data + .5).clip(0, 1))
        self.data[self.data == 1] = -1
        self.data[max_area_mask] = self.data[max_area_mask] * -1
    
    def apply_mediterrian_mask(self):
        """ This is mediterrian mask specific for the test bathymetry file """
        tmp = self.data[0:59, 280:350]
        tmp[tmp == 1] = -1
        self.data[0:59, 280:350] = tmp
