'''
Unit test to nemo_bdy_msk_c

@author: Srikanth Nagella
'''
import unittest
from pynemo.gui.nemo_bdy_mask import * 

class Test(unittest.TestCase):


    def testMaskData(self):
        mask = Mask('data/grid_C/NNA_R12_bathy_meter_bench.nc')
        print(mask.data.shape)
        self.assertEqual(mask.data.shape,(401,351),'Mask reading failed')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()