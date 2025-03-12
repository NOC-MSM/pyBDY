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
Created on Thu Feb 13 18:03:00 2025.

@author James Harle
@author Benjamin Barton

Called test_zz_end_to_end so it is the last unit test to run.
"""

# External imports
import datetime as dt
import os
import subprocess

import numpy as np
import xarray as xr
from grid import hgr, zgr

# Internal imports
from tests.synth import synth_bathymetry, synth_temp_sal, synth_zgrid


def test_zco_zco():
    """
    Test the full pybdy processing using a regression test.

    This test is for dst in zco and sc in zco vertical coordinates
    """
    path1, path2, path3 = generate_sc_test_case(zco=True)
    path4 = generate_dst_test_case(zco=True)
    name_list_path = modify_namelist(path1, path3, path4)

    # Run pybdy
    subprocess.run(
        "pybdy -s " + name_list_path,
        shell=True,
        check=True,
        text=True,
    )

    coords = "./tests/data/coordinates.bdy.nc"
    output_t = "./tests/data/data_output_bdyT_y1979m11.nc"
    output_u = "./tests/data/data_output_bdyU_y1979m11.nc"
    output_v = "./tests/data/data_output_bdyV_y1979m11.nc"

    # Check output
    ds_t = xr.open_dataset(output_t)
    ds_u = xr.open_dataset(output_u)
    ds_v = xr.open_dataset(output_v)
    temp = ds_t["votemper"].to_masked_array()

    summary_grid = {
        "Num_var_t": len(ds_t.keys()),
        "Min_gdept": float(ds_t["gdept"].min().to_numpy()),
        "Max_gdept": float(ds_t["gdept"].max().to_numpy()),
        "Shape_temp": ds_t["votemper"].shape,
        "Shape_ssh": ds_t["sossheig"].shape,
        "Shape_mask": ds_t["bdy_msk"].shape,
        "Mean_temp": float(ds_t["votemper"].mean().to_numpy()),
        "Mean_sal": float(ds_t["vosaline"].mean().to_numpy()),
        "Sum_unmask": np.ma.count(temp),
        "Sum_mask": np.ma.count_masked(temp),
        "Shape_u": ds_u["vozocrtx"].shape,
        "Shape_v": ds_v["vomecrty"].shape,
        "Mean_u": float(ds_u["vozocrtx"].mean().to_numpy()),
        "Mean_v": float(ds_v["vomecrty"].mean().to_numpy()),
    }

    # Clean up files
    os.remove(path1)
    os.remove(path2)
    os.remove(path4)
    os.remove(coords)
    os.remove(output_t)
    os.remove(output_u)
    os.remove(output_v)

    print(summary_grid)
    test_grid = {
        "Num_var_t": 11,
        "Min_gdept": 41.66666793823242,
        "Max_gdept": 1041.6666259765625,
        "Shape_temp": (30, 25, 1, 1584),
        "Shape_ssh": (30, 1, 1584),
        "Shape_mask": (60, 50),
        "Mean_temp": 16.437015533447266,
        "Mean_sal": 30.8212833404541,
        "Sum_unmask": 495030,
        "Sum_mask": 692970,
        "Shape_u": (30, 25, 1, 1566),
        "Shape_v": (30, 25, 1, 1566),
        "Mean_u": 0.9023050665855408,
        "Mean_v": 0.8996582627296448,
    }

    assert summary_grid == test_grid, "May need to update regression values."


def test_sco_sco():
    """
    Test the full pybdy processing using a regression test.

    This test is for dst in sco and sc in sco vertical coordinates
    """
    path1, path2, path3 = generate_sc_test_case(zco=False)
    path4 = generate_dst_test_case(zco=False)
    name_list_path = modify_namelist(path1, path3, path4)

    # Run pybdy
    subprocess.run(
        "pybdy -s " + name_list_path,
        shell=True,
        check=True,
        text=True,
    )

    coords = "./tests/data/coordinates.bdy.nc"
    output_t = "./tests/data/data_output_bdyT_y1979m11.nc"
    output_u = "./tests/data/data_output_bdyU_y1979m11.nc"
    output_v = "./tests/data/data_output_bdyV_y1979m11.nc"

    # Check output
    ds_t = xr.open_dataset(output_t)
    ds_u = xr.open_dataset(output_u)
    ds_v = xr.open_dataset(output_v)
    temp = ds_t["votemper"].to_masked_array()

    summary_grid = {
        "Num_var_t": len(ds_t.keys()),
        "Min_gdept": float(ds_t["gdept"].min().to_numpy()),
        "Max_gdept": float(ds_t["gdept"].max().to_numpy()),
        "Shape_temp": ds_t["votemper"].shape,
        "Shape_ssh": ds_t["sossheig"].shape,
        "Shape_mask": ds_t["bdy_msk"].shape,
        "Mean_temp": float(ds_t["votemper"].mean().to_numpy()),
        "Mean_sal": float(ds_t["vosaline"].mean().to_numpy()),
        "Sum_unmask": np.ma.count(temp),
        "Sum_mask": np.ma.count_masked(temp),
        "Shape_u": ds_u["vozocrtx"].shape,
        "Shape_v": ds_v["vomecrty"].shape,
        "Mean_u": float(ds_u["vozocrtx"].mean().to_numpy()),
        "Mean_v": float(ds_v["vomecrty"].mean().to_numpy()),
    }

    # Clean up files
    os.remove(path1)
    os.remove(path2)
    os.remove(path4)
    os.remove(coords)
    os.remove(output_t)
    os.remove(output_u)
    os.remove(output_v)

    print(summary_grid)
    test_grid = {
        "Num_var_t": 11,
        "Min_gdept": 3.8946874141693115,
        "Max_gdept": 991.9130859375,
        "Shape_temp": (30, 15, 1, 1584),
        "Shape_ssh": (30, 1, 1584),
        "Shape_mask": (60, 50),
        "Mean_temp": 17.26908302307129,
        "Mean_sal": 31.9005126953125,
        "Sum_unmask": 712800,
        "Sum_mask": 0,
        "Shape_u": (30, 15, 1, 1566),
        "Shape_v": (30, 15, 1, 1566),
        "Mean_u": 0.7552474737167358,
        "Mean_v": 0.7674047350883484,
    }

    assert summary_grid == test_grid, "May need to update regression values."


def generate_sc_test_case(zco):
    """
    Generate a synthetic test case for source.

    Parameters
    ----------
    zco (bool) : if true generate zco vertical coordinates, if false sco

    Returns
    -------
    path1 (str)        : path to netcdf file for testing
    """
    path1 = "./tests/data/mesh_synth_sc.nc"
    path2 = "./tests/data"
    path3 = "./tests/data/sc_test.ncml"
    fname = "/data_synth_sc.nc"

    if not os.path.exists(path2):
        os.makedirs(path2)

    dx = 0.5
    dy = 0.25
    lon_t = np.arange(-20, 8, dx)
    lat_t = np.arange(39, 56, dy)
    ppe1 = np.zeros((len(lon_t))) + dx
    ppe2 = np.zeros((len(lat_t))) + dy

    # Generate an A-Grid
    synth = synth_bathymetry.Bathymetry(ppe1, ppe2, ppglam0=lon_t[0], ppgphi0=lat_t[0])
    synth = synth.sea_mount(depth=1000, stiff=1)

    # These are garbage let grid.hgr calculate them
    synth = synth.drop_vars(["e1t", "e2t", "e1v", "e2v", "e1u", "e2u", "e1f", "e2f"])

    # Generate depth array
    if zco:
        max_depth = 2000
        n_zlevel = 20
        gdept, gdepw = synth_zgrid.synth_zco(max_depth, n_zlevel)
        gdept = np.tile(gdept, (len(lon_t), len(lat_t), 1)).T
        gdepw = np.tile(gdepw, (len(lon_t), len(lat_t), 1)).T
    else:
        n_zlevel = 20
        gdept, gdepw = synth_zgrid.synth_sco(synth["Bathymetry"], n_zlevel)

    synth["gdept"] = xr.DataArray(gdept, dims=["z", "y", "x"], name="gdept").copy()
    synth["gdepw"] = xr.DataArray(gdepw, dims=["z", "y", "x"], name="gdepw").copy()

    # Add data
    data_vars = synth_bathymetry.generate_variables(synth)

    # Add mbathy
    synth["gdept"] = xr.DataArray(
        gdept[np.newaxis, ...], dims=["t", "z", "y", "x"], name="gdept"
    ).copy()
    synth["gdepw"] = xr.DataArray(
        gdepw[np.newaxis, ...], dims=["t", "z", "y", "x"], name="gdepw"
    ).copy()
    gdept = synth["gdept"].to_numpy()
    b_tile = np.tile(synth["Bathymetry"], (1, n_zlevel, 1, 1))
    mbathy = np.argmax(gdept > b_tile, axis=1)
    synth["mbathy"] = xr.DataArray(mbathy, dims=["t", "y", "x"], name="mbathy")

    # Add tmask, umask, vmask, fmask (0 for land, 1 for ocean)
    tmask = np.zeros((b_tile.shape)) + 1
    tmask[gdept > b_tile] = 0
    umask = tmask.copy()
    vmask = tmask.copy()
    fmask = tmask.copy()
    synth["tmask"] = xr.DataArray(tmask, dims=["t", "z", "y", "x"], name="tmask")
    synth["umask"] = xr.DataArray(umask, dims=["t", "z", "y", "x"], name="umask")
    synth["vmask"] = xr.DataArray(vmask, dims=["t", "z", "y", "x"], name="vmask")
    synth["fmask"] = xr.DataArray(fmask, dims=["t", "z", "y", "x"], name="fmask")

    # Compute profiles
    depth = xr.DataArray(gdept[0, :, :, :], dims=["z", "y", "x"], name="gdept").copy()
    # times = xr.cftime_range("2000", periods=3, freq="A-JUN", calendar="standard")
    ref = dt.datetime(1960, 1, 1)
    st = dt.datetime(1979, 11, 1)
    date_list = [st + dt.timedelta(days=i) for i in range(31)]
    tdelta_d = np.array([(date_list[i] - ref).days for i in range(len(date_list))])
    tdelta_s = np.array([(date_list[i] - ref).seconds for i in range(len(date_list))])
    tdelta = (tdelta_d * 24 * 60 * 60) + tdelta_s
    da_t = xr.DataArray(tdelta, [("time_counter", tdelta)])
    da_t = da_t.assign_attrs(
        units="seconds since " + ref.strftime("%Y-%m-%d %H:%M:%S"), calendar="gregorian"
    )

    depth = depth.expand_dims(dim={"time_counter": da_t})
    depth = depth.transpose("time_counter", "z", "y", "x")

    data_vars["votemper"] = synth_temp_sal.temperature_profile(depth)
    data_vars["vosaline"] = synth_temp_sal.salinity_profile(depth)
    uvel = np.ones_like(data_vars["vozocrtx"])
    uvel[:, -10:, :, :] = 0.5
    data_vars["vozocrtx"] = xr.DataArray(
        uvel, dims=["time_counter", "z", "y", "x"], name="vozocrtx"
    ).copy()
    uvel[:, :, -10:, :] = 0.25
    data_vars["vomecrty"] = xr.DataArray(
        uvel, dims=["time_counter", "z", "y", "x"], name="vomecrty"
    ).copy()
    data_vars["time_counter"] = da_t

    data_vars["votemper"] = data_vars["votemper"].assign_attrs(units="C")
    data_vars["vosaline"] = data_vars["vosaline"].assign_attrs(units="PSU")
    data_vars["vozocrtx"] = data_vars["vozocrtx"].assign_attrs(units="m/s")  # u
    data_vars["vomecrty"] = data_vars["vomecrty"].assign_attrs(units="m/s")  # v
    data_vars["sossheig"] = data_vars["sossheig"].assign_attrs(units="m")
    data_vars["x"] = data_vars["x"].assign_attrs(units="unitless")
    data_vars["y"] = data_vars["y"].assign_attrs(units="unitless")

    synth.to_netcdf(path1)
    data_vars.to_netcdf(path2 + fname)

    return path1, path2 + fname, path3


def generate_dst_test_case(zco):
    """
    Generate a synthetic test case for destination.

    Parameters
    ----------
    zco (bool) : if true generate zco vertical coordinates, if false sco

    Returns
    -------
    path1 (str)        : path to netcdf file for testing
    """
    path1 = "./tests/data/mesh_synth_dst.nc"

    dx = 0.3
    dy = 0.1
    lon_t = np.arange(-12, 3, dx)
    lat_t = np.arange(45, 51, dy)
    ppe1 = np.zeros((len(lon_t))) + dx
    ppe2 = np.zeros((len(lat_t))) + dy
    synth = synth_bathymetry.Bathymetry(ppe1, ppe2, ppglam0=lon_t[0], ppgphi0=lat_t[0])
    synth = synth.sea_mount(depth=1000, stiff=1)

    # These are garbage let grid.hgr calculate them
    e_grid_vars = ["e1t", "e2t", "e1v", "e2v", "e1u", "e2u", "e1f", "e2f"]
    synth = synth.drop_vars(e_grid_vars)

    # Add time dimension to glam gphi
    g_vars = ["glamt", "gphit", "glamu", "gphiu", "glamv", "gphiv", "glamf", "gphif"]
    for i in range(len(g_vars)):
        synth[g_vars[i]] = xr.DataArray(
            synth[g_vars[i]].to_numpy()[np.newaxis, ...],
            dims=["t", "y", "x"],
            name=g_vars[i],
        )

    if zco:
        max_depth = 2000
        n_zlevel = 25
        gdept, gdepw = synth_zgrid.synth_zco(max_depth, n_zlevel)
        gdept = np.tile(gdept, (len(lon_t), len(lat_t), 1)).T
        gdepw = np.tile(gdepw, (len(lon_t), len(lat_t), 1)).T
    else:
        n_zlevel = 15
        gdept, gdepw = synth_zgrid.synth_sco(synth["Bathymetry"], n_zlevel)

    synth["gdept"] = xr.DataArray(
        gdept[np.newaxis, ...], dims=["t", "z", "y", "x"], name="gdept"
    ).copy()
    synth["gdepw"] = xr.DataArray(
        gdepw[np.newaxis, ...], dims=["t", "z", "y", "x"], name="gdepw"
    ).copy()
    gdept = synth["gdept"].to_numpy()
    b_tile = np.tile(synth["Bathymetry"], (1, n_zlevel, 1, 1))
    mbathy = np.argmax(gdept > b_tile, axis=1)
    synth["mbathy"] = xr.DataArray(mbathy, dims=["t", "y", "x"], name="mbathy").copy()

    # Add tmask, umask, vmask, fmask (0 for land, 1 for ocean)
    tmask = np.zeros((b_tile.shape)) + 1
    tmask[gdept > b_tile] = 0
    umask = tmask.copy()
    vmask = tmask.copy()
    fmask = tmask.copy()
    synth["tmask"] = xr.DataArray(tmask, dims=["t", "z", "y", "x"], name="tmask")
    synth["umask"] = xr.DataArray(umask, dims=["t", "z", "y", "x"], name="umask")
    synth["vmask"] = xr.DataArray(vmask, dims=["t", "z", "y", "x"], name="vmask")
    synth["fmask"] = xr.DataArray(fmask, dims=["t", "z", "y", "x"], name="fmask")

    # Fill in horizontal and vertical variables
    grid = {}
    grid["glamt"] = synth["glamt"].to_numpy()
    grid["gphit"] = synth["gphit"].to_numpy()
    grid["glamu"] = synth["glamu"].to_numpy()
    grid["gphiu"] = synth["gphiu"].to_numpy()
    grid["glamv"] = synth["glamv"].to_numpy()
    grid["gphiv"] = synth["gphiv"].to_numpy()
    grid["glamf"] = synth["glamf"].to_numpy()
    grid["gphif"] = synth["gphif"].to_numpy()

    hgrid_type = "A"
    grid = hgr.fill_hgrid_vars(hgrid_type, grid, e_grid_vars)
    for i in range(len(e_grid_vars)):
        synth[e_grid_vars[i]] = xr.DataArray(
            grid[e_grid_vars[i]], dims=["t", "y", "x"], name=e_grid_vars[i]
        )

    if zco:
        zgrid_type = "zco"
    else:
        zgrid_type = "sco"

    grid = {}
    grid["gdept"] = synth["gdept"].to_numpy()
    grid["gdepw"] = synth["gdepw"].to_numpy()

    e3_grid_vars = ["gdepu", "gdepv", "gdepf", "e3t", "e3w", "e3u", "e3v", "e3f"]
    hgrid = zgr.fill_zgrid_vars(zgrid_type, grid, hgrid_type, synth, e3_grid_vars)
    for i in range(len(e3_grid_vars)):
        synth[e3_grid_vars[i]] = xr.DataArray(
            hgrid[e3_grid_vars[i]], dims=["t", "z", "y", "x"], name=e3_grid_vars[i]
        ).copy()

    synth.to_netcdf(path1)
    return path1


def modify_namelist(path_src, path_sc_data, path_dst):
    # Modify paths in a namelist file for testing.

    namelist_file = "./tests/data/namelist_zz_end_to_end.bdy"

    with open(namelist_file, "r") as f:
        lines = f.readlines()
        for li in range(len(lines)):
            if "sn_src_hgr" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_src + "' !" + en
            if "sn_src_zgr" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_src + "' !" + en
            if "sn_src_msk" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_src + "' !" + en

            if "sn_dst_hgr" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_dst + "' !" + en
            if "sn_dst_zgr" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_dst + "' !" + en
            if "sn_bathy" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_dst + "' !" + en

            if "sn_src_dir" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = st + "= '" + path_sc_data + "' !" + en
            if "sn_dst_dir" in lines[li]:
                st = lines[li].split("=")[0]
                en = lines[li].split("!")[-1]
                lines[li] = (
                    st + "= '" + "/".join(path_sc_data.split("/")[:-1]) + "' !" + en
                )

    with open(namelist_file, "w") as f:
        for li in range(len(lines)):
            f.write(lines[li])

    return namelist_file
