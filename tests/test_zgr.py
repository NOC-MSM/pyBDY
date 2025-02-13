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
Created on Mon Feb 03 18:03:00 2025.

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
from src.grid import zgr


def test_depth():
    logger = logging.getLogger(__name__)
    in_file = "test.nc"
    zgr.Depth(in_file, logger)
    assert False


def test_depth_file_z():
    # Test the zgr class on a z grid
    bench_file = "./inputs/benchmark/grid_low_res_C/mesh_zgr.nc"
    in_file = "./tests/test_zgr.nc"

    if not os.path.isfile(bench_file):
        # If the benchmark isn't present we can't test
        warnings.warn(
            Warning("Benchmark data not present so can't test src/grid/zgr.py.")
        )
        assert True
    else:
        variables = ["gdept_0", "mbathy"]
        subprocess.run(
            "ncks -O -v " + ",".join(variables) + " " + bench_file + " " + in_file,
            shell=True,
            check=True,
            text=True,
        )
        logger = logging.getLogger(__name__)
        zg = zgr.H_Grid(in_file, logger)

        nc = GetFile(bench_file)
        e3t = nc.nc["e3t"][:]
        e3w = nc.nc["e3w"][:]
        gdept = nc.nc["gdept"][:]
        gdepw = nc.nc["gdepw"][:]
        nc.close()

        os.remove(in_file)

        errors = []
        if not zg.grid_type == "z":
            errors.append("Grid type not identified correctly.")
        elif not len(zg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif not ((np.sum(np.abs(e3t - zg.grid["e3t"])) / e3t.size) == 0):
            errors.append("e3t does not match.")
        elif not ((np.sum(np.abs(e3w - zg.grid["e3w"])) / e3w.size) == 0):
            errors.append("e3w does not match.")
        elif not (np.sum(np.abs(gdept - zg.grid["gdepu"])) == 0):
            errors.append("gdepu does not match.")
        elif not (np.sum(np.abs(gdepw - zg.grid["gdepw"])) == 0):
            errors.append("gdepw does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_depth_file_zps():
    # Test the zgr class on a zps grid
    bench_file = "./inputs/benchmark/grid_low_res_C/mesh_zgr_zps.nc"
    in_file = "./tests/test_zgr.nc"

    if not os.path.isfile(bench_file):
        # If the benchmark isn't present we can't test
        warnings.warn(
            Warning("Benchmark data not present so can't test src/grid/zgr.py.")
        )
        assert True
    else:
        variables = ["gdept", "mbathy"]
        subprocess.run(
            "ncks -O -v " + ",".join(variables) + " " + bench_file + " " + in_file,
            shell=True,
            check=True,
            text=True,
        )
        logger = logging.getLogger(__name__)
        zg = zgr.H_Grid(in_file, logger)

        nc = GetFile(bench_file)
        e3t = nc.nc["e3t"][:]
        e3w = nc.nc["e3w"][:]
        gdepu = nc.nc["gdepu"][:]
        gdepw = nc.nc["gdepw"][:]
        nc.close()

        os.remove(in_file)

        errors = []
        if not zg.grid_type == "z":
            errors.append("Grid type not identified correctly.")
        elif not len(zg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif not ((np.sum(np.abs(e3t - zg.grid["e3t"])) / e3t.size) == 0):
            errors.append("e3t does not match.")
        elif not ((np.sum(np.abs(e3w - zg.grid["e3w"])) / e3w.size) == 0):
            errors.append("e3w does not match.")
        elif not (np.sum(np.abs(gdepu - zg.grid["gdepu"])) == 0):
            errors.append("gdepu does not match.")
        elif not (np.sum(np.abs(gdepw - zg.grid["gdepw"])) == 0):
            errors.append("gdepw does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_fill_zgrid_vars_regression():
    # Test the variable filling functions using a regression test
    lon_t = np.arange(-10, 1, 1)
    lat_t = np.arange(50, 53, 0.5)
    lon_tg, lat_tg = np.meshgrid(lon_t, lat_t)
    lon_tg = lon_tg[np.newaxis, :, :]
    lat_tg = lat_tg[np.newaxis, :, :]
    gdept = np.arange(5, 55, 10)
    gdept = np.append(gdept, np.array([z + z * 0.2 for z in range(10, 50, 10)]) + 45)
    bathy = np.zeros((1, 1))
    grid = {"gdept": gdept, "mbathy": bathy}
    missing = [
        "glamu",
        "gphiu",
        "glamv",
        "gphiv",
        "e1t",
        "e2t",
        "e1u",
        "e2u",
        "e1v",
        "e2v",
    ]
    hgr_type = "C"

    grid = zgr.fill_hgrid_vars("z", grid, hgr_type, missing)
    summary_grid = {
        "Num_var": len(grid.keys()),
        "Min_glamu": np.min(grid["glamu"]),
        "Min_gphiu": np.min(grid["gphiu"]),
        "Min_glamv": np.min(grid["glamv"]),
        "Min_gphiv": np.min(grid["gphiv"]),
        "Shape_glamu": grid["glamu"].shape,
        "Shape_gphiv": grid["gphiv"].shape,
        "Sum_e1t": np.sum(grid["e1t"]),
        "Sum_e2t": np.sum(grid["e2t"]),
        "Sum_e1u": np.sum(grid["e1u"]),
        "Sum_e2v": np.sum(grid["e2v"]),
    }
    test_grid = {
        "Num_var": 12,
        "Min_glamu": -9.5,
        "Min_gphiu": 50.0,
        "Min_glamv": -10.0,
        "Min_gphiv": 50.25,
        "Shape_glamu": (1, 6, 11),
        "Shape_gphiv": (1, 6, 11),
        "Sum_e1t": 4593222.917238032,
        "Sum_e2t": 3669564.4738020166,
        "Sum_e1u": 4593222.917238034,
        "Sum_e2v": 3669564.473802005,
    }
    assert summary_grid == test_grid
