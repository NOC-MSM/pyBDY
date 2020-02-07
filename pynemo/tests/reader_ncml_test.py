'''
Unit tests for Ncml data reading module using pyjnius

@author: Mr. Srikanth Nagella
'''
import unittest

#from pynemo.reader.ncml_back import init_jnius
#from pynemo.reader.ncml_back import Data
from pynemo.reader.ncml import init_jnius
from pynemo.reader.ncml import Variable as Data2
from pynemo.reader.ncml import GridGroup
from pynemo.reader.ncml import Reader
from pynemo.reader.ncml import NcMLFile

import os
class Test(unittest.TestCase):

#     @unittest.skip("Remote testing skipping")
#     def testDataInit(self):
#         init_jnius()
#         testpath, file_name = os.path.split(__file__)
#         testfile = os.path.join(testpath, "test.ncml")
#         dataset = Data(testfile,"votemper")
#         data = dataset[0,0,0,0:10]
#         self.assertEquals(data.shape[0],10,"Extracted requested dimension of data")
#         self.assertAlmostEquals(data[0],18.945175,6)


                
    def testTimeCounter(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml")
        sd = Reader(testfile,0).grid
        dataset = Data2(sd.dataset,"time_counter")
        self.assertEqual(len(dataset), 8, "There should 8 datasets")
    
    def testVariable(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml")      
        sd = Reader(testfile,0).grid
        dataset = Data2(sd.dataset,"votemper")
        val = dataset[0,0,0,0]
        val2 = dataset[2,10,0,0]
        self.assertAlmostEqual(dataset[0,0,0,0], 18.945175, 6,"First value should be 18.9")
        self.assertAlmostEqual(dataset[2,10,0,0], 20.314891, 5,"2, 10, 0,0  value should be 18.9")
        
    def testNcMLFile(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml")
        sd = NcMLFile(testfile)
        val = sd['votemper'][0,0,0,0]
        self.assertAlmostEqual(val, 18.945175, 6,"First value should be 18.9")

        
    def testSrcDataVariable(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml")
        sd = Reader(testfile,0).grid    
        dataset = sd["votemper"]
        val = dataset[0,0,0,0]
        val2 = dataset[2,10,0,0]        
        self.assertAlmostEqual(dataset[0,0,0,0], 18.945175, 6,"First value should be 18.9")
        self.assertAlmostEqual(dataset[2,10,0,0], 20.314891, 5,"2, 10, 0,0  value should be 18.9")
        
    def testRepoMatching(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml") 
        repo = Reader(testfile,0)
        self.assertAlmostEqual(repo['t']['votemper'][0,0,0,0], 18.945175, 6,"First value should be 18.9")
        self.assertAlmostEqual(repo['t']['votemper'][2,10,0,0], 20.314891, 5,"2, 10, 0,0  value should be 18.9")
        
    def testGridGroupTimeCounter(self):
        init_jnius()
        testpath, file_name = os.path.split(__file__)
        testfile = os.path.join(testpath, "testremote.ncml")
        repo = Reader(testfile,0)
        self.assertEqual(len(repo['t'].time_counter), 8, "Time counter should be 8")
        self.assertEqual(repo['t'].time_counter[0], 691416000, "The first time value doesn't match")
        repo = Reader(testfile,100)
        self.assertEqual(len(repo['t'].time_counter), 8, "Time counter should be 8")
        self.assertEqual(repo['t'].time_counter[0], 691416100, "The first time value doesn't match")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()