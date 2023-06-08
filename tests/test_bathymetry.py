"""Module that tests the Bathymetry class."""

import functools
import os
import shutil
import subprocess
from typing import Tuple, Union

import numpy as np
import pytest
import xarray as xr
from _pytest.fixtures import SubRequest
from pybdy.utils.nemo_bdy_lib import sub2ind

from .bathymetry import Bathymetry, generate_variables, merge_z3_and_e3


@pytest.fixture(scope="function")
def handle_temp_dir(request: SubRequest) -> str:
    """
    Create and remove a temporary directory.

    Parameters
    ----------
    request
        Fixture request.

    Returns
    -------
    Path to the temporary directory.
    """

    def rm_temp_dir(dir_to_rm: str) -> None:
        """
        Remove a temporary directory.

        Parameters
        ----------
        dir_to_rm
            Directory to remove.
        """
        shutil.rmtree(dir_to_rm)

    # Create a temporary directory
    temp_path = os.path.join("tests", request.param)
    os.mkdir(temp_path)

    # Add a finalizer that removes the temporary directory
    request.addfinalizer(functools.partial(rm_temp_dir, temp_path))

    return temp_path


def _create_bathymetry(
    dlon: Union[float, int],
    dlat: Union[float, int],
    parent_coords: Tuple[Union[float, int]],
    child_coords: Tuple[Union[float, int]],
    depth_coords: Tuple[Union[float, int]],
    degrees_parent: Union[float, int],
    degrees_child: Union[float, int],
    path: str,
) -> Tuple[xr.Dataset, xr.Dataset, xr.Dataset]:
    """
    Create coordinates and bathymetry of parent and child.

    Parameters
    ----------
    dlon
        Longitude step (units: degrees).
    dlat
        Latitude step (units: degrees).
    parent_coords
        Geotic coordinates of parent grid (lon_i_parent, lon_f_parent, lat_i_parent, lat_f_parent)
        Tuple with starting longitude (W->E), final longitude (W->E),
        starting latitude (S->N), final latitude (S->N)
    child_coords
        Geotic coordinates of child grid (lon_i_child, lon_f_child, lat_i_child, lat_f_child)
        Tuple with starting longitude (W->E), final longitude (W->E),
        starting latitude (S->N), final latitude (S->N)
    depth_coords
        Tuple with starting depth, final depth, and depth tickness (depth_i, depth_f, depth_thickness)
    degrees_parent
        Angle of parent grid (units: degrees).
    degrees_child
        Angle of child grid (units: degrees).
    path
        Path to temporary directory where parent.nc, child.nc and variables.nc will be saved.

    Returns
    -------
    ds_domcfg_parent, ds_domcfg_child, ds_var_parent
        Datasets with bathymetry of parent and child, and variables of parent.
    """
    lon_i_parent, lon_f_parent, lat_i_parent, lat_f_parent = parent_coords
    lon_i_child, lon_f_child, lat_i_child, lat_f_child = child_coords
    depth_i, depth_f, depth_thickness = depth_coords

    # Calculate number of grid points
    nlon_parent = int((lon_f_parent - lon_i_parent) / dlon) + 1
    nlat_parent = int((lat_f_parent - lat_i_parent) / dlat) + 1
    nlon_child = int((lon_f_child - lon_i_child) / dlon) + 1
    nlat_child = int((lat_f_child - lat_i_child) / dlat) + 1

    # Generate coordinates and bathymetry of parent and child - flat bottom case
    ds_bathy_child = Bathymetry(
        dlon,
        dlat,
        nlon_child,
        nlat_child,
        lon_i_child,
        lat_i_child,
        degrees=degrees_child,
    ).flat(depth_f)

    ds_bathy_parent = Bathymetry(
        dlon,
        dlat,
        nlon_parent,
        nlat_parent,
        lon_i_parent,
        lat_i_parent,
        degrees=degrees_parent,
    ).flat(depth_f)

    # Create the vertical grid information
    z3t = xr.DataArray(np.arange(depth_i, depth_f, depth_thickness), dims=("z",))
    z3w = xr.DataArray(np.arange(depth_i, depth_f, depth_thickness), dims=("z",))
    e3t = xr.full_like(z3t, depth_thickness)
    e3w = xr.full_like(z3t, depth_thickness)

    # Merge the vertical grid information with coordinates and bathymetry
    ds_domcfg_parent = merge_z3_and_e3(ds_bathy_parent, z3t, z3w, e3t, e3w)
    ds_domcfg_child = merge_z3_and_e3(ds_bathy_child, z3t, z3w, e3t, e3w)

    # Generate variables to use as source data
    ds_var_parent = generate_variables(
        ds_domcfg_parent,
    )

    # Save to file
    ds_domcfg_parent.to_netcdf(os.path.join(path, "parent.nc"))
    ds_domcfg_child.to_netcdf(os.path.join(path, "child.nc"))
    ds_var_parent.to_netcdf(os.path.join(path, "variables.nc"))

    return ds_domcfg_parent, ds_domcfg_child, ds_var_parent


@pytest.mark.parametrize("handle_temp_dir", ["temp_test_001"], indirect=True)
def test_child_grid_colocated(handle_temp_dir) -> None:
    """
    Test the case where the child grid is as a 1:1 sub region of the parent grid.

    Notes
    -----
    Longitude, latitude, depth grid points are all colocated in both parent and child grids.
    """
    # Define lat and lon boundaries of parent and child grids
    dlon, dlat = (1.0, 1.0)
    lon_i_offset, lon_f_offset, lat_i_offset, lat_f_offset = (10, -10, 5, -5)
    lon_i_parent, lon_f_parent, lat_i_parent, lat_f_parent = (-20.0, 10.0, 45.0, 65.0)
    lon_i_child, lon_f_child, lat_i_child, lat_f_child = (
        lon_i_parent + dlon * lon_i_offset,
        lon_f_parent + dlon * lon_f_offset,
        lat_i_parent + dlat * lat_i_offset,
        lat_f_parent + dlat * lat_f_offset,
    )
    depth_i, depth_f, depth_thickness = (50.0, 5000.0, 100.0)
    parent_rotation, child_rotation = (0.0, 0.0)

    # Create coordinates and bathymetry of parent and child
    ds_domcfg_parent, ds_domcfg_child, ds_var_parent = _create_bathymetry(
        dlon,
        dlat,
        (lon_i_parent, lon_f_parent, lat_i_parent, lat_f_parent),
        (lon_i_child, lon_f_child, lat_i_child, lat_f_child),
        (depth_i, depth_f, depth_thickness),
        parent_rotation,
        child_rotation,
        handle_temp_dir,
    )

    # Run pybdy
    result = subprocess.run(
        ["pybdy", "-s", os.path.join("tests", "namelists", "namelist_test_001.bdy")]
    )

    # Assert pybdy run successfully
    assert result.returncode == 0

    # Load NetCDF files produced by pybdy
    ds_coords_bdy = xr.open_dataset(os.path.join(handle_temp_dir, "coordinates.bdy.nc"))
    ds_var_child = xr.open_dataset(
        os.path.join(handle_temp_dir, "child_bdyT_y2001m01.nc")
    )

    # Subsample parent variables
    votemper_parent_sub = ds_var_parent["votemper"][
        :, :, slice(lat_i_offset, lat_f_offset), slice(lon_i_offset, lon_f_offset)
    ]
    vosaline_parent_sub = ds_var_parent["vosaline"][
        :, :, slice(lat_i_offset, lat_f_offset), slice(lon_i_offset, lon_f_offset)
    ]

    # Extract votemper and vosaline along the boundary from the subsampled parent
    nbit = ds_coords_bdy.nbit.values.squeeze() - 1
    nbjt = ds_coords_bdy.nbjt.values.squeeze() - 1
    votemper_parent_bdy = votemper_parent_sub[:, :, nbit, nbjt].values
    vosaline_parent_bdy = vosaline_parent_sub[:, :, nbit, nbjt].values

    assert np.min(nbit) == 1
    assert np.min(nbjt) == 1
    assert np.max(nbit) == int(ds_var_child.dims["x"]) - 2
    assert np.max(nbjt) == int(ds_var_child.dims["x"]) - 2

    # Reshape the bdy of the subsampled parent grid
    votemper_parent_bdy = votemper_parent_bdy.reshape(
        votemper_parent_bdy.shape[0],
        votemper_parent_bdy.shape[1],
        votemper_parent_bdy.shape[2] * votemper_parent_bdy.shape[3],
    )

    vosaline_parent_bdy = vosaline_parent_bdy.reshape(
        vosaline_parent_bdy.shape[0],
        vosaline_parent_bdy.shape[1],
        vosaline_parent_bdy.shape[2] * vosaline_parent_bdy.shape[3],
    )

    # Extract only the correct combination of nbit and nbjt indices
    one_dim_idx = sub2ind(nbit.shape, nbit, nbjt)
    votemper_parent_bdy = votemper_parent_bdy[:, :, one_dim_idx]
    vosaline_parent_bdy = vosaline_parent_bdy[:, :, one_dim_idx]

    # Difference between parent and child temperature and salinity
    diff_votemper = (
        votemper_parent_bdy[0, :-1, :] - ds_var_child["votemper"][0, :-1, 0, :]
    )
    diff_vosaline = (
        vosaline_parent_bdy[0, :-1, :] - ds_var_child["vosaline"][0, :-1, 0, :]
    )

    # Compare values on the boundary of the subsampled parent grid and child grid
    assert np.all(np.abs(diff_votemper) < 1e-8)
    assert np.all(np.abs(diff_vosaline) < 1e-8)
