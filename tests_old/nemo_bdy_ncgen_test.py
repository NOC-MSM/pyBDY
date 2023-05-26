"""
Created on 6 Oct 2014.

@author: sn65
"""
import os
import unittest

from pynemo.nemo_bdy_ncgen import CreateBDYNetcdfFile


class Test(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def testCreateNCFileMain(self):
        CreateBDYNetcdfFile(
            "Test.nc",
            7699,
            351,
            401,
            75,
            9,
            "EB bdy files produces by jdha from ORCA0083-N001 global run provided by acc",
            "1960-01-01 00:00:00",
            -1e20,
            "gregorian",
            "T",
        )

    def tearDown(self):
        os.remove("Test.nc")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testCreateNCFileMain']
    unittest.main()
