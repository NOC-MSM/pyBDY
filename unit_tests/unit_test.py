# -*- coding: utf-8 -*-
"""
Set of test functions to test PyNEMO functionality.

"""
from subprocess import Popen, PIPE
from netCDF4 import Dataset
import numpy as np
import glob
import os

# generate test data by import test gen script and executing main function
import unit_tests.test_gen as tg
gen_data = tg._main()
if gen_data != 0:
    raise Exception('DONT PANIC: Input data generation failed')

# TODO: run different bdy files or change bdy file for different grid types for testing.

# run PyNEMO with test data
namelist_files = glob.glob('unit_tests/namelist*')
for n in namelist_files:
    stdout, stderr = Popen(['pynemo', '-s', n], stdout=PIPE, stderr=PIPE,
                       universal_newlines=True).communicate()
if 'Execution Time' not in stdout:
    raise Exception('DONT PANIC: Test Run Failed')

# TODO: Learn about parameterising the tests so that different parameters can be checked
#       with same code. Rather than having similar test functions repeated.

# perform tests
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

def test_salinty():
    test_files = glob.glob('unit_tests/test_outputs/unit_test*')
    for t in test_files:
        results = Dataset(t)  # open results
        sal = results['so'][:]
        results.close()
        sal_ = np.ma.masked_array(sal,sal == -32767.0)
        assert abs(sal_[sal_!=0.0].mean() - 35) <= 0.001
        assert abs(sal_[sal_ != 0.0].max() - 35) <= 0.001
        assert abs(sal_[sal_ != 0.0].min() - 35) <= 0.001

# clean up test I/O
files = glob.glob('unit_tests/test_outputs/*')
for f in files:
    os.remove(f)
files = glob.glob('unit_tests/test_outputs/*')
if len(files) != 0:
    raise Exception('DONT PANIC: output folder not cleaned')

files = glob.glob('unit_tests/test_data/*')
for f in files:
    os.remove(f)
files = glob.glob('unit_tests/test_data/*')
if len(files) != 0:
    raise Exception('DONT PANIC: input folder not cleaned')

