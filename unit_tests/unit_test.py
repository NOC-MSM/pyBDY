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
# TODO: Maybe simplify this, as this import imports other scripts and is abit clunky.
import unit_tests.test_gen as tg
gen_data = tg._main()
# if a non zero is return than the grid and data generation has failed.
if gen_data != 0:
    raise Exception('DONT PANIC: Input grid and boundary data generation failed')

# run PyNEMO with test data
# generate list of namelist.bdy files to run
namelist_files = glob.glob('unit_tests/namelist*')
for n in namelist_files:
    # run each of the namelist files
    stdout, stderr = Popen(['pynemo', '-s', n], stdout=PIPE, stderr=PIPE,
                       universal_newlines=True).communicate()
    # check to see if PyNEMO ran correctly, no execution time in stdout is indication of this.
    if 'Execution Time' not in stdout:
        print(stderr)
        raise Exception('DONT PANIC: Test Run '+str(n)+'  Failed')

# TODO: Learn about parameterising the tests so that different parameters can be checked
#       with same code. Rather than having similar test functions repeated.

# perform tests
def test_temp():
    test_files = glob.glob('unit_tests/test_outputs/*bdyT*')
    if len(test_files) == 0:
        raise Exception('DONT PANIC: no temperature test files found')
    for t in test_files:
        results = Dataset(t) # open results
        temp = results['thetao'][:]
        results.close()
        temp_ = np.ma.masked_array(temp,temp == -32767.0)
        assert abs(temp_[temp_!=0.0].mean() - 15) <= 0.001
        assert abs(temp_[temp_ != 0.0].max() - 15) <= 0.001
        assert abs(temp_[temp_ != 0.0].min() - 15) <= 0.001

def test_salinty():
    test_files = glob.glob('unit_tests/test_outputs/*bdyT*')
    if len(test_files) == 0:
        raise Exception('DONT PANIC: no salinity test files found')
    for t in test_files:
        results = Dataset(t)  # open results
        sal = results['so'][:]
        results.close()
        sal_ = np.ma.masked_array(sal,sal == -32767.0)
        assert abs(sal_[sal_!=0.0].mean() - 35) <= 0.001
        assert abs(sal_[sal_ != 0.0].max() - 35) <= 0.001
        assert abs(sal_[sal_ != 0.0].min() - 35) <= 0.001

def test_ssh():
    test_files = glob.glob('unit_tests/test_outputs/*bdyT*')
    if len(test_files) == 0:
        raise Exception('DONT PANIC: no SSH test files found')
    for t in test_files:
        results = Dataset(t)  # open results
        ssh = results['zos'][:]
        results.close()
        ssh_ = np.ma.masked_array(ssh,ssh == -32767.0)
        assert abs(ssh_[ssh_!=0.0].mean() - 1.0) <= 0.001
        assert abs(ssh_[ssh_ != 0.0].max() - 1.0) <= 0.001
        assert abs(ssh_[ssh_ != 0.0].min() - 1.0) <= 0.001

def test_U():
    test_files = glob.glob('unit_tests/test_outputs/*bdyU*')
    if len(test_files) == 0:
        raise Exception('DONT PANIC: no U current test files found')
    for t in test_files:
        results = Dataset(t)  # open results
        U = results['uo'][:]
        results.close()
        U_ = np.ma.masked_array(U,U == -32767.0)
        assert abs(U_[U_!=0.0].mean() - 0.5) <= 0.001
        assert abs(U_[U_ != 0.0].max() - 0.5) <= 0.001
        assert abs(U_[U_ != 0.0].min() - 0.5) <= 0.001

def test_V():
    test_files = glob.glob('unit_tests/test_outputs/*bdyV*')
    if len(test_files) == 0:
        raise Exception('DONT PANIC: no V current test files found')
    for t in test_files:
        results = Dataset(t)  # open results
        V = results['vo'][:]
        results.close()
        V_ = np.ma.masked_array(V,V == -32767.0)
        assert abs(V_[V_!=0.0].mean() - 0.5) <= 0.001
        assert abs(V_[V_ != 0.0].max() - 0.5) <= 0.001
        assert abs(V_[V_ != 0.0].min() - 0.5) <= 0.001

# clean up test I/O
def test_rm_out():
    files = glob.glob('unit_tests/test_outputs/*')
    for f in files:
        os.remove(f)
    files = glob.glob('unit_tests/test_outputs/*')
    assert len(files) == 0


def test_rm_in():
    files = glob.glob('unit_tests/test_inputs/*')
    for f in files:
        os.remove(f)
    files = glob.glob('unit_tests/test_inputs/*')
    assert len(files) == 0
