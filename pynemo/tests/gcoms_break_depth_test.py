'''
This is unit test for gcoms_break_depth

@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
import unittest
from pynemo.utils import gcoms_break_depth
from netCDF4 import Dataset
import numpy as np
class Test(unittest.TestCase):


    def setUp(self):
        self.nc = Dataset('data/gebco_1.nc')
        self.bathy = self.nc.variables['topo'][2::6,2::6]
        self.lat = self.nc.variables['latitude'][2::6]
        self.lon = self.nc.variables['longitude'][2::6]

        self.lat = self.lat
        self.lon = self.lon
        self.lon,self.lat = np.meshgrid(self.lon, self.lat)
        #gcoms_break_depth.gcoms_boundary_masks(self.bathy, -1, 0)
        
        print(self.bathy.shape)
        print(self.bathy)
        pass


    def tearDown(self):
        self.nc.close()
        pass


    def testPolcoms_select_domain(self):
        roi = [1045, 1537, 975, 1328]
        self.bathy = self.bathy[...]
        self.bathy[self.bathy>=0] = 0
        self.bathy = self.bathy*-1        
        tmp  = gcoms_break_depth.polcoms_select_domain(self.bathy, self.lat, self.lon, roi, 200)
        self.assertEqual(tmp[32,0],1,"Set the break select correctly")
        self.assertEqual(tmp[40,0],1,"Set the break select correctly 40")        
        self.assertEqual(tmp[50,0],1,"Set the break select correctly 50")        
        self.assertEqual(tmp[60,0],1,"Set the break select correctly 60")        
                
    def testGcomsBreakDepth(self):
        r = 18        
        self.bathy = self.bathy[991-r:1295+r,1556-r:1801+r]
        self.bathy[self.bathy>=0]=0        
        self.bathy = -1*self.bathy
        self.bathy[np.isnan(self.bathy)] = -1
        self.lat = self.lat[1556-r:1801+r]
        self.lon = self.lon[991-r:1295+r]        
        gcoms_break_depth.gcoms_break_depth(self.bathy)

        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()