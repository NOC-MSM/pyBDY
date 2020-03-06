# -*- coding: utf-8 -*-
"""
Set of test functions to test PyNEMO functionality.

"""
from subprocess import Popen, PIPE
from netCDF4 import Dataset
import numpy as np
import glob
import os

def test_run():
    stdout, stderr = Popen(['pynemo','-s','unit_tests/namelist_unit_test.bdy'], stdout=PIPE, stderr=PIPE,
                           universal_newlines=True).communicate()
    assert 'Execution Time' in stdout

def test_temp():
    test_files = glob.glob('unit_tests/test_outputs/unit_test*')
    for t in test_files:
        results = Dataset(t) # open results
        temp = results['thetao'][:]
        results.close()
        temp_ = np.ma.masked_array(temp,temp == -32767.0)
        assert abs(temp_[temp_!=0.0].mean() - 15) <= 0.001
        assert abs(temp_[temp_ != 0.0].max() - 15) <= 0.001
        assert abs(temp_[temp_ != 0.0].min() - 15) <= 0.001

#def test_salinty():
#    test_files = glob.glob('unit_tests/test_outputs/unit_test*')
#    for t in test_files:
#        results = Dataset(t)  # open results
#        sal = results['so'][:]
#        results.close()
#        sal_ = np.ma.masked_array(sal,sal == -32767.0)
#        assert abs(sal_[sal_!=0.0].mean() - 35) <= 0.001
#        assert abs(sal_[sal_ != 0.0].max() - 35) <= 0.001
#        assert abs(sal_[sal_ != 0.0].min() - 35) <= 0.001

def test_rm_output():
    files = glob.glob('unit_tests/test_outputs/*')
    for f in files:
        os.remove(f)
    files = glob.glob('unit_tests/test_outputs/*')
    assert len(files) == 0

