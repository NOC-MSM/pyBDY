"""Module that tests the Bathymetry class."""

import os
import shutil
import subprocess
from typing import Tuple, Union

import numpy as np
import pytest
import xarray as xr

from .bathymetry import Bathymetry, generate_variables, merge_z3_and_e3


@pytest.fixture
def create_temp_dir(tmp_path_factory) -> str:
    """Create a temporary directory."""
    path = tmp_path_factory.mktemp("temp_dir", numbered=True)

    return path


def _create_bathymetry(
    dlon: Union[float, int],
    dlat: Union[float, int],
    parent_coords: Tuple[Union[float, int]],
    child_coords: Tuple[Union[float, int]],
    depth_coords: Tuple[Union[float, int]],
    degrees_parent: Union[float, int],
    degrees_child: Union[float, int],
    path: str,
) -> None:
    """
    Create coordinates and bathymetry of parent and child.

    Parameters
    ----------
    dlon:
        Longitude step (units: degrees).
    dlat:
        Latitude step (units: degrees).
    parent_coords:
        Geotic coordinates of parent grid (lon_i_parent, lon_f_parent, lat_i_parent, lat_f_parent)
        Tuple with starting longitude (W->E), final longitude (W->E),
        starting latitude (S->N), final latitude (S->N)
    child_coords:
        Geotic coordinates of child grid (lon_i_child, lon_f_child, lat_i_child, lat_f_child)
        Tuple with starting longitude (W->E), final longitude (W->E),
        starting latitude (S->N), final latitude (S->N)
    depth_coords:
        Tuple with starting depth, final depth, and depth tickness (depth_i, depth_f, depth_thickness)
    degrees_parent:
        Angle of parent grid (units: degrees).
    degrees_child:
        Angle of child grid (units: degrees).
    path:
        Path to temporary directory where parent.nc, child.nc and variables.nc will be saved.

    Returns
    -------
    None
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
    ds_var = generate_variables(
        ds_domcfg_parent,
    )

    # Save to file
    ds_domcfg_parent.to_netcdf(os.path.join(path, "parent.nc"))
    ds_domcfg_child.to_netcdf(os.path.join(path, "child.nc"))
    ds_var.to_netcdf(os.path.join(path, "variables.nc"))


def test_child_grid_as_colocated_subregion(tmpdir) -> None:
    """
    Test the case where the child grid is as a 1:1 sub region of the parent grid.

    Notes
    -----
    For this case, longitude, latitude, depth grid points are all colocated in both parent and child grids.
    """
    # Create a temporary directory
    temp_path = os.path.join("tests", "temp_test_001")
    # temp_path = tmpdir.mkdir(temp_path) # created
    os.mkdir(temp_path)

    # Create coordinates and bathymetry of parent and child
    _create_bathymetry(
        1.0,
        1.0,
        (-20.0, 10.0, 45.0, 65.0),
        (-10.0, 0.0, 50.0, 60.0),
        (50.0, 5000.0, 100.0),
        0.0,
        0.0,
        temp_path,
    )

    # Run pybdy
    subprocess.run(
        ["pybdy", "-s", os.path.join("tests", "namelists", "namelist_test_001.bdy")]
    )

    # Remove dir
    shutil.rmtree(temp_path)
