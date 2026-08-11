"""Module to generate datasets for testing."""

from typing import Any, Callable, Optional, TypeVar

import numpy as np
import xarray as xr
from xarray import DataArray, Dataset

F = TypeVar("F", bound=Callable[..., Any])


class Variables:
    """Class to generate idealized variable datasets."""

    def __init__(self, *args, **kwargs):
        """
        Initialize class generating a NEMO style variable datasets.

        Parameters
        ----------
        *args
            Arguments passed on to :py:func:`_generate_grid`
        *kwargs
            Keyword arguments passed on to
            :py:func:`_generate_grid`.
        """
        self._vars = _generate_variables(*args, **kwargs)

    def const(self, var, value) -> Dataset:
        """
        Produce a constant variable field..

        Parameters
        ----------
        var: string
           variable name
        value: float
           constant value for the field

        Returns
        -------
        Dataset.
        """
        ds = self._vars
        print(var)
        print(value)
        return ds

    def lin_grad(self, var, direction) -> Dataset:
        """
        Generate linear gradient in variable field.

        Produces ...

        Parameters
        ----------
        var: string
            variable name
        direction: string
            i,j,k,t

        Returns
        -------
        Dataset.
        """
        ds = self._vars
        print(var)
        print(direction)
        return ds

    def real_grad(self, var, direction) -> Dataset:
        """
        Generate realistic gradient in variable field.

        Produces ...

        Parameters
        ----------
        var: string
            variable name
        direction: string
            i,j,k,t

        Returns
        -------
        Dataset.
        """
        ds = self._vars
        print(var)
        print(direction)
        return ds

def _generate_variables(
    ds_domcfg,
) -> Dataset:
    """
    Generate a Dataset of T/S/U/V given a NEMO bathy Dataset.

    Parameters
    ----------
    ds_domcfg: Dataset

    Returns
    -------
    Dataset
        Equivalent of NEMO output file.

    Raises
    ------
    ValueError
    """
    ds = Dataset()

    # Define variables
    temp = xr.full_like(ds_domcfg.e3t, 20.0, dtype=np.double)
    salt = xr.full_like(ds_domcfg.e3t, 35.0, dtype=np.double)
    uvel = xr.full_like(ds_domcfg.e3t, 1.0, dtype=np.double)
    vvel = xr.full_like(ds_domcfg.e3t, 1.0, dtype=np.double)
    ssh = xr.full_like(ds_domcfg.e2t, 0.0, dtype=np.double)

    # Add attributes
    temp.attrs = dict(units="C", long_name="Temperature (degrees centigrade)")
    salt.attrs = dict(units="", long_name="Salinity (unitless)")
    uvel.attrs = dict(units="m/s", long_name="Zonal Velocity (m/s)")
    vvel.attrs = dict(units="m/s", long_name="Meridional Velocity (m/s)")
    ssh.attrs = dict(units="m", long_name="Sea Surface Height (m)")

    # Add to ds
    ds["votemper"] = temp
    ds["vosaline"] = salt
    ds["vozocrtx"] = uvel
    ds["vomecrty"] = vvel
    ds["sossheig"] = ssh

    # Add t dim
    # times = pd.date_range("2020","2023",freq='Y')+ DateOffset(months=6)
    # TODO: add input to adjust frequency of data
    times = xr.cftime_range("2000", periods=3, freq="A-JUN", calendar="standard")
    da_t = xr.DataArray(times, [("t", times)])
    ds = ds.expand_dims(dim={"t": da_t})
    ds = ds.transpose("t", "z", "y", "x")
    ds["t"] = ds["t"]

    return ds
