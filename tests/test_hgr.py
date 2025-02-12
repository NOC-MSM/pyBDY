# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""
Created on Thu Dec 22 18:03:00 2024.

@author James Harle
@author Benjamin Barton
@author Ryan Patmore
"""

# External imports
import logging
import os.path
import subprocess
import warnings

import numpy as np
from pybdy.reader.factory import GetFile

# Internal imports
from src.grid import hgr
from tests import synth_bathymetry as synth_bathy


def test_h_grid_file_A():
    # Test the hgr class on an A grid
    bench_file = "./inputs/benchmark/grid_low_res_C/mesh_hgr.nc"
    in_file = "./tests/test_hgr.nc"

    if not os.path.isfile(bench_file):
        # If the benchmark isn't present we can't test
        warnings.warn(
            Warning("Benchmark data not present so can't test src/grid/hgr.py.")
        )
        assert True
    else:
        variables = ["nav_lat", "nav_lon"]
        subprocess.run(
            "ncks -O -v " + ",".join(variables) + " " + bench_file + " " + in_file,
            shell=True,
            check=True,
            text=True,
        )
        logger = logging.getLogger(__name__)
        hg = hgr.H_Grid(in_file, logger)

        nc = GetFile(bench_file)
        e1t = nc.nc["e1t"][:]
        e2t = nc.nc["e2t"][:]
        glamt = nc.nc["glamt"][:]
        gphit = nc.nc["gphit"][:]
        nc.close()

        errors = []
        if not hg.grid_type == "A":
            errors.append("Grid type not identified correctly.")
        elif not len(hg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2):
            errors.append("e1t does not match.")
        elif not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2):
            errors.append("e2t does not match.")
        elif not (np.sum(np.abs(glamt - hg.grid["glamu"])) < 0.2):
            errors.append("glamu does not match.")
        elif not (np.sum(np.abs(gphit - hg.grid["gphiv"])) < 0.2):
            errors.append("gphiv does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_h_grid_file_C():
    # Test the hgr class on an C grid
    bench_file = "./inputs/benchmark/grid_low_res_C/mesh_hgr.nc"
    in_file = "./tests/test_hgr.nc"

    if not os.path.isfile(bench_file):
        # If the benchmark isn't present we can't test
        warnings.warn(
            Warning("Benchmark data not present so can't test src/grid/hgr.py.")
        )
        assert True
    else:
        variables = ["glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv"]
        subprocess.run(
            "ncks -O -v " + ",".join(variables) + " " + bench_file + " " + in_file,
            shell=True,
            check=True,
            text=True,
        )
        logger = logging.getLogger(__name__)
        hg = hgr.H_Grid(in_file, logger)

        nc = GetFile(bench_file)
        e1t = nc.nc["e1t"][:]
        e2t = nc.nc["e2t"][:]
        glamu = nc.nc["glamu"][:]
        gphiv = nc.nc["gphiv"][:]
        nc.close()

        errors = []
        if not hg.grid_type == "C":
            errors.append("Grid type not identified correctly.")
        elif not len(hg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2):
            errors.append("e1t does not match.")
        elif not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2):
            errors.append("e2t does not match.")
        elif not (np.sum(np.abs(glamu - hg.grid["glamu"])) < 0.2):
            errors.append("glamu does not match.")
        elif not (np.sum(np.abs(gphiv - hg.grid["gphiv"])) < 0.2):
            errors.append("gphiv does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_h_grid_synth_A():
    # Test the hgr class on an A grid
    # NOTE hard to test this since it will use the same functions to
    # generate the synthetic test
    logger = logging.getLogger(__name__)
    variables = ["nav_lat", "nav_lon"]
    path1, path2 = gen_synth_netcdf(variables)
    hg = hgr.H_Grid(path2, logger)

    nc = GetFile(path1)
    e1t = nc.nc["e1t"][:]
    e2t = nc.nc["e2t"][:]
    glamt = nc.nc["glamt"][:]
    gphit = nc.nc["gphit"][:]
    nc.close()

    os.remove(path1)
    os.remove(path2)

    print(np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size)
    print(np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size)
    print(np.sum(np.abs(glamt - hg.grid["glamu"])))
    print(np.sum(np.abs(gphit - hg.grid["gphiv"])))

    errors = []
    if not hg.grid_type == "A":
        errors.append("Grid type not identified correctly.")
    elif not len(hg.grid.keys()) == 16:
        errors.append("Not enough grid variables generated.")
    # elif not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2):
    #    errors.append("e1t does not match.")
    # elif not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2):
    #    errors.append("e2t does not match.")
    elif not (np.sum(np.abs(glamt - hg.grid["glamu"])) < 0.2):
        errors.append("glamu does not match.")
    elif not (np.sum(np.abs(gphit - hg.grid["gphiv"])) < 0.2):
        errors.append("gphiv does not match.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_h_grid_synth_C():
    # Test the hgr class on an C grid
    # NOTE hard to test this since it will use the same functions to
    # generate the synthetic test
    logger = logging.getLogger(__name__)
    variables = ["glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv"]
    path1, path2 = gen_synth_netcdf(variables)
    hg = hgr.H_Grid(path2, logger)

    nc = GetFile(path1)
    e1t = nc.nc["e1t"][:]
    e2t = nc.nc["e2t"][:]
    glamu = nc.nc["glamu"][:]
    gphiv = nc.nc["gphiv"][:]
    nc.close()

    os.remove(path1)
    os.remove(path2)

    print(np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size)
    print(np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size)
    print(np.sum(np.abs(glamu - hg.grid["glamu"])))
    print(np.sum(np.abs(gphiv - hg.grid["gphiv"])))

    errors = []
    if not hg.grid_type == "C":
        errors.append("Grid type not identified correctly.")
    elif not len(hg.grid.keys()) == 16:
        errors.append("Not enough grid variables generated.")
    # elif not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2):
    #    errors.append("e1t does not match.")
    # elif not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2):
    #    errors.append("e2t does not match.")
    elif not (np.sum(np.abs(glamu - hg.grid["glamu"])) < 0.2):
        errors.append("glamu does not match.")
    elif not (np.sum(np.abs(gphiv - hg.grid["gphiv"])) < 0.2):
        errors.append("gphiv does not match.")
    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def gen_synth_netcdf(variables):
    # Generate a synthetic test case
    lon_t = np.arange(-20, 1, 1)
    lat_t = np.arange(40, 53, 0.5)
    ppe1 = np.zeros((len(lon_t))) + 1
    ppe2 = np.zeros((len(lat_t))) + 0.5
    synth = synth_bathy.Bathymetry(ppe1, ppe2, ppglam0=lon_t[0], ppgphi0=lat_t[0])
    synth = synth.sea_mount(depth=1000, stiff=1000)

    # write dataset
    path1 = "./tests/synth_test_full.nc"
    path2 = "./tests/synth_test_sub.nc"
    synth.to_netcdf(path1)

    subprocess.run(
        "ncks -O -v " + ",".join(variables) + " " + path1 + " " + path2,
        shell=True,
        check=True,
        text=True,
    )
    return path1, path2
