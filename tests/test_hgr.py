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

# Internal imports
from grid import hgr
from pybdy.reader.factory import GetFile

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

        os.remove(in_file)

        errors = []
        if not hg.grid_type == "A":
            errors.append("Grid type not identified correctly.")
        elif not len(hg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif (
            not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2)
            or not (
                np.abs(np.sum(e1t, axis=2) - np.sum(hg.grid["e1t"], axis=2)) < 25
            ).all()
        ):
            errors.append("e1t does not match.")
        elif (
            not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2)
            or not (
                np.abs(np.sum(e2t, axis=1) - np.sum(hg.grid["e2t"], axis=1)) < 25
            ).all()
        ):
            errors.append("e2t does not match.")
        elif not (np.sum(np.abs(glamt - hg.grid["glamu"])) == 0):
            errors.append("glamu does not match.")
        elif not (np.sum(np.abs(gphit - hg.grid["gphiv"])) == 0):
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

        os.remove(in_file)

        errors = []
        if not hg.grid_type == "C":
            errors.append("Grid type not identified correctly.")
        elif not len(hg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif (
            not ((np.sum(np.abs(e1t - hg.grid["e1t"])) / e1t.size) < 0.2)
            or not (
                np.abs(np.sum(e1t, axis=2) - np.sum(hg.grid["e1t"], axis=2)) < 25
            ).all()
        ):
            errors.append("e1t does not match.")
        elif (
            not ((np.sum(np.abs(e2t - hg.grid["e2t"])) / e2t.size) < 0.2)
            or not (
                np.abs(np.sum(e2t, axis=1) - np.sum(hg.grid["e2t"], axis=1)) < 25
            ).all()
        ):
            errors.append("e2t does not match.")
        elif not (np.sum(np.abs(glamu - hg.grid["glamu"])) == 0):
            errors.append("glamu does not match.")
        elif not (np.sum(np.abs(gphiv - hg.grid["gphiv"])) == 0):
            errors.append("gphiv does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_fill_hgrid_vars_regression():
    # Test the variable filling functions using a regression test
    lon_t = np.arange(-10, 1, 1)
    lat_t = np.arange(50, 53, 0.5)
    lon_tg, lat_tg = np.meshgrid(lon_t, lat_t)
    lon_tg = lon_tg[np.newaxis, :, :]
    lat_tg = lat_tg[np.newaxis, :, :]
    grid = {"glamt": lon_tg, "gphit": lat_tg}
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

    grid = hgr.fill_hgrid_vars("C", grid, missing)
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
    assert summary_grid == test_grid, "May need to update regression values."


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
    elif not (np.sum(np.abs(glamt - hg.grid["glamu"])) == 0):
        errors.append("glamu does not match.")
    elif not (np.sum(np.abs(gphit - hg.grid["gphiv"])) == 0):
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
    elif not (np.sum(np.abs(glamu - hg.grid["glamu"])) == 0):
        errors.append("glamu does not match.")
    elif not (np.sum(np.abs(gphiv - hg.grid["gphiv"])) == 0):
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
