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
from grid import hgr, zgr
from pybdy.reader.factory import GetFile


def test_depth_file_zps():
    # Test the zgr class on a zps grid
    bench_file = "./inputs/benchmark/grid_low_res_C/mesh_zgr.nc"
    in_file = "./tests/test_zgr.nc"
    bench_file_h = "./inputs/benchmark/grid_low_res_C/mesh_hgr.nc"

    if not ((os.path.isfile(bench_file_h) & os.path.isfile(bench_file))):
        # If the benchmark isn't present we can't test
        warnings.warn(
            Warning("Benchmark data not present so can't test src/grid/zgr.py.")
        )
        assert True
    else:
        variables = ["gdept", "mbathy", "nav_lat", "nav_lon"]
        subprocess.run(
            "ncks -O -v " + ",".join(variables) + " " + bench_file + " " + in_file,
            shell=True,
            check=True,
            text=True,
        )
        logger = logging.getLogger(__name__)

        # e1 and e2 data
        hg = hgr.H_Grid(bench_file_h, logger)
        keys = ["e1t", "e2t", "e1u", "e2u", "e1v", "e2v", "e1f", "e2f"]
        e_dict = {k: hg.grid[k] for k in keys}

        # calc vertical grid
        zg = zgr.Z_Grid(in_file, hg.grid_type, e_dict, logger)

        nc = GetFile(bench_file)
        e3t = nc.nc["e3t"][:]
        e3w = nc.nc["e3w"][:]
        e3u = nc.nc["e3u"][:]
        e3v = nc.nc["e3v"][:]
        nc.nc["gdept"][:]
        gdepu = nc.nc["gdepu"][:]
        gdepw = nc.nc["gdepw"][:]
        nc.nc["mbathy"][:]
        nc.close()

        os.remove(in_file)

        # Mask below bathy starting from 2 levels above bathy
        # because we don't know depth of bathy for gdepw

        z_ind = np.indices(zg.grid["gdept"].shape)[1]
        m_tile = (
            np.tile(zg.grid["mbathy"], (zg.grid["gdept"].shape[1], 1, 1))[
                np.newaxis, ...
            ]
            - 2
        )
        m_tile[:, :, :-1, :] = np.minimum(m_tile[:, :, :-1, :], m_tile[:, :, 1:, :])
        m_tile[:, :, :, :-1] = np.minimum(m_tile[:, :, :, :-1], m_tile[:, :, :, 1:])
        for vi in zg.var_list:
            if vi in ["gdept", "gdepw", "gdepu", "gdepv", "e3t", "e3u", "e3v", "e3w"]:
                zg.grid[vi] = np.ma.masked_where(z_ind >= m_tile, zg.grid[vi])
        no_mask = zg.grid["gdepw"].mask is False

        errors = []
        if not zg.grid_type == "zps":
            errors.append("Grid type not identified correctly.")
        elif not len(zg.grid.keys()) == 16:
            errors.append("Not enough grid variables generated.")
        elif not (
            np.isclose(gdepw[no_mask], zg.grid["gdepw"][no_mask], atol=1e0)
        ).all():
            errors.append("gdepw does not match.")
        elif not (
            np.isclose(gdepu[no_mask], zg.grid["gdepu"][no_mask], atol=1e-2)
        ).all():
            errors.append("gdepu does not match.")
        elif not (np.isclose(e3t[no_mask], zg.grid["e3t"][no_mask], atol=1e1)).all():
            errors.append("e3t does not match.")
        elif not (np.isclose(e3w[no_mask], zg.grid["e3w"][no_mask], atol=1e1)).all():
            errors.append("e3w does not match.")
        elif not (np.isclose(e3v[no_mask], zg.grid["e3v"][no_mask], atol=1e1)).all():
            errors.append("e3v does not match.")
        elif not (np.isclose(e3u[no_mask], zg.grid["e3u"][no_mask], atol=1e1)).all():
            errors.append("e3u does not match.")
        # assert no error message has been registered, else print messages
        assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_fill_zgrid_vars_regression():
    # Test the variable filling functions using a regression test
    lon_t = np.arange(-10, 1, 1)
    lat_t = np.arange(50, 53, 0.5)
    lon_tg, lat_tg = np.meshgrid(lon_t, lat_t)
    bathy_t = np.floor((1 - lon_tg / 2.0 + lon_tg**5 + lat_tg**3) / 2000)
    bathy_t[bathy_t <= 25] = 0
    gdept_0 = np.arange(5, 55, 10)
    gdept_0 = np.append(
        gdept_0, np.array([z + z * 0.2 for z in range(10, 50, 10)]) + 45
    )
    gbathy = np.tile(
        gdept_0,
        (bathy_t.shape[1], bathy_t.shape[0], 1),
    ).T
    mbathy = np.argmax(gbathy > np.tile(bathy_t, (len(gdept_0), 1, 1)), axis=0)[
        np.newaxis, ...
    ]
    lon_tg = lon_tg[np.newaxis, ...]
    lat_tg = lat_tg[np.newaxis, ...]

    grid = {
        "glamt": lon_tg,
        "gphit": lat_tg,
        "glamu": lon_tg + 0.5,
        "gphiu": lat_tg,
        "glamv": lon_tg,
        "gphiv": lat_tg + 0.25,
        "glamf": lon_tg + 0.5,
        "gphif": lat_tg + 0.25,
    }
    missing = [
        "e1t",
        "e2t",
        "e1u",
        "e2u",
        "e1v",
        "e2v",
        "e1f",
        "e2f",
    ]
    h_grid = hgr.fill_hgrid_vars("C", grid, missing)

    grid = {"gdept_0": gdept_0, "mbathy": mbathy}
    missing = [
        "gdept",
        "gdepu",
        "gdepv",
        "gdepw",
        "e3t",
        "e3u",
        "e3v",
        "e3w",
    ]
    hgr_type = "C"

    grid = zgr.fill_zgrid_vars("z", grid, hgr_type, h_grid, missing)
    summary_grid = {
        "Num_var": len(grid.keys()),
        "Min_gdepw": np.min(grid["gdepw"]),
        "Max_gdepw": np.max(grid["gdepw"]),
        "Shape_gdepu": grid["gdepu"].shape,
        "Shape_gdepw": grid["gdepw"].shape,
        "Sum_e3t": np.sum(grid["e3t"]),
        "Sum_e3w": np.sum(grid["e3w"]),
        "Sum_e3u": np.sum(grid["e3u"]),
        "Sum_e3v": np.sum(grid["e3v"]),
    }
    print(summary_grid)
    test_grid = {
        "Num_var": 10,
        "Min_gdepw": 0.0,
        "Max_gdepw": 87.0144230769231,
        "Shape_gdepu": (1, 9, 6, 11),
        "Shape_gdepw": (1, 9, 6, 11),
        "Sum_e3t": 6533.048076923075,
        "Sum_e3w": 6468.0,
        "Sum_e3u": 6533.048076923075,
        "Sum_e3v": 6533.048076923075,
    }

    assert summary_grid == test_grid, "May need to update regression values."
