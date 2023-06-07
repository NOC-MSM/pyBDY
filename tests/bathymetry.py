"""Module to generate datasets for testing."""

from typing import Any, Callable, Optional, TypeVar

import numpy as np
import xarray as xr
from xarray import DataArray, Dataset

F = TypeVar("F", bound=Callable[..., Any])


class Bathymetry:
    """Class to generate idealized test bathymetry datasets."""

    def __init__(self, *args, **kwargs):
        """
        Initialize class generating a NEMO style grid.

        Parameters
        ----------
        *args
            Arguments passed on to :py:func:`_generate_grid`
        *kwargs
            Keyword arguments passed on to
            :py:func:`_generate_grid`.
        """
        self._coords = _generate_grid(*args, **kwargs)

    def flat(self, depth: float) -> Dataset:
        """
        Flat bottom case.

        Parameters
        ----------
        depth: float
            Bottom depth (units: m).

        Returns
        -------
        Dataset.
        """
        ds = self._coords
        ds["Bathymetry"] = xr.full_like(ds["glamt"], depth)
        return _add_attributes(_add_mask(ds))

    def sea_mount(self, depth: float, stiff: float = 1) -> Dataset:
        """
        Channel with seamount case.

        Produces bathymetry of a channel with a Gaussian seamount in order to
        simulate an idealised test case. Based on Marsaleix et al., 2009
        doi:10.1016/j.ocemod.2009.06.011 Eq. 15.

        Parameters
        ----------
        depth: float
            Bottom depth (units: m).
        stiff: float
            Scale factor for steepness of seamount (units: None)

        Returns
        -------
        Dataset.
        """
        ds = self._coords

        # Find half way point for sea mount location
        half_way = {k: v // 2 for k, v in ds.sizes.items()}
        glamt_mid, gphit_mid = (g.isel(half_way) for g in (ds.glamt, ds.gphit))

        # Define sea mount bathymetry
        ds["Bathymetry"] = depth * (
            1.0
            - 0.9
            * np.exp(
                -(
                    stiff
                    / 40.0e3**2
                    * ((ds.glamt - glamt_mid) ** 2 + (ds.gphit - gphit_mid) ** 2)
                )
            )
        )

        ds["rmax"] = _calc_rmax(ds["Bathymetry"])

        return _add_attributes(_add_mask(ds))


def _add_mask(ds: Dataset) -> Dataset:
    """
    Infer sea mask from bathymetry.

    Parameters
    ----------
    ds: Dataset
        Dataset with Bathymetry variable

    Returns
    -------
    Dataset.
    """
    # ds["tmask"] = xr.where(ds["Bathymetry"] > 0, 1, 0).expand_dims(
    # dim={"z": np.arange(len(50))}, axis=0)  # TODO: should this be bool?
    ds_tmp = xr.where(ds["Bathymetry"] > 0, 1, 0).values
    ds_tmp = np.tile(ds_tmp, (50, 1, 1))

    ds["tmask"] = (("z", "y", "x"), ds_tmp)

    return ds


def _add_attributes(ds: Dataset) -> Dataset:
    """
    Add CF attributes to bathymetry and mask variables.

    Parameters
    ----------
    ds: Dataset
        Dataset with bathymetry and mask variables [and rmax].

    Returns
    -------
    Dataset.
    """
    attrs_dict: dict = {
        "Bathymetry": dict(standard_name="sea_floor_depth_below_geoid", units="m"),
        "tmask": dict(standard_name="sea_binary_mask", units="1"),
    }

    if "rmax" in ds:
        attrs_dict["rmax"] = dict(standard_name="rmax", units="1")

    for varname, attrs in attrs_dict.items():
        ds[varname].attrs = attrs
        ds[varname].attrs["coordinates"] = "glamt gphit"
    return ds


def _calc_rmax(depth):
    """
    Calculate rmax: measure of steepness.

    This function returns the slope steepness criteria rmax, which is simply
    |H[0] - H[1]| / (H[0] + H[1]).

    Parameters
    ----------
    depth: float
        Bottom depth (units: m).

    Returns
    -------
    rmax: float
        Slope steepness value (units: None)

    Notes
    -----
    This function uses a "conservative approach" and rmax is overestimated.
    rmax at T points is the maximum rmax estimated at any adjacent U/V point.
    """
    # Mask land
    depth = depth.where(depth > 0)

    # Loop over x and y
    both_rmax = []
    for dim in depth.dims:
        # Compute rmax
        rolled = depth.rolling({dim: 2}).construct("window_dim")
        diff = rolled.diff("window_dim").squeeze("window_dim")
        rmax = np.abs(diff) / rolled.sum("window_dim")

        # Construct dimension with velocity points adjacent to any T point
        # We need to shift as we rolled twice
        rmax = rmax.rolling({dim: 2}).construct("vel_points")
        rmax = rmax.shift({dim: -1})

        both_rmax.append(rmax)

    # Find maximum rmax at adjacent U/V points
    rmax = xr.concat(both_rmax, "vel_points")
    rmax = rmax.max("vel_points", skipna=True)

    # Mask halo points
    for dim in rmax.dims:
        rmax[{dim: [0, -1]}] = 0

    return rmax.fillna(0)


def _rotate(lon, lat, origin=(0, 0), degrees=0):
    """
    Rotation of coordinates.

    Parameters
    ----------
    lon: float
        longitude (units: deg), 2D array-like of size x/y.
    lat: float
        latitude (units: deg), 2D array-like of size x/y.
    origin: tuple
        (lon,lat) (units: deg), point of rotation.
    degrees: float
        angle (units: deg) by which to rotate.

    Returns
    -------
    lon: float
        longitude (units: deg), 2D array-like of size x/y.
    lat: float
        latitude (units: deg), 2D array-like of size x/y.
    """
    # Formatting
    lon_rav = lon.ravel()
    lat_rav = lat.ravel()
    pos_rav = np.stack((lon_rav, lat_rav), axis=1)
    ang_rad = np.deg2rad(degrees)

    # Rotation matirx
    R = np.array(
        [[np.cos(ang_rad), -np.sin(ang_rad)], [np.sin(ang_rad), np.cos(ang_rad)]]
    )
    origin = np.atleast_2d(origin)

    # Rotate
    rot_rav = np.squeeze((R @ (pos_rav.T - origin.T) + origin.T).T)

    # Pass back to arrays
    lon_rav[:] = rot_rav[:, 0]
    lat_rav[:] = rot_rav[:, 1]

    return lon, lat


def _generate_grid(
    ppe1_m,
    ppe2_m,
    jpiglo: Optional[int] = None,
    jpjglo: Optional[int] = None,
    ppglam0: float = 0,
    ppgphi0: float = 0,
    degrees: float = 0,
    chunks: Optional[dict] = None,
) -> Dataset:
    """
    Generate coordinates and spacing of a NEMO style grid.

    Parameters
    ----------
    ppe1_m, ppe2_m: float, 1D array-like
        Grid spacing along x/y axis (units: deg).
    jpiglo, jpjglo: int, optional
        Size of x/y dimension.
    ppglam0, ppgphi0: float
        x/y coordinate of first T-point (units: deg).
    chunks: dict, optional
         Chunk sizes along each dimension (e.g., ``{"x": 5, "y": 5}``).
         Requires ``dask`` installed.

    Returns
    -------
    Dataset
        Equivalent of NEMO coordinates file.

    Raises
    ------
    ValueError
        If ``ppe{1,2}_m`` is a vector and ``jp{i,j}glo`` is specified, or viceversa.

    Notes
    -----
    Vectors are loaded into memory. If ``chunks`` is specified, 2D arrays are coerced
    into dask arrays before broadcasting.
    """
    ds = Dataset()
    for dim, ppe, jp, ppg in zip(
        ["x", "y"], [ppe1_m, ppe2_m], [jpiglo, jpjglo], [ppglam0, ppgphi0]
    ):
        # Check and convert ppe to numpy array
        ppe = np.asarray(ppe, dtype=float)
        if (ppe.shape and jp) or (not ppe.shape and not jp):
            raise ValueError(
                "`jp{i,j}glo` must be specified"
                " if and only if `ppe{1,2}_m` is not a vector."
            )

        # c: center f:face
        delta_c = DataArray(ppe if ppe.shape else ppe.repeat(jp), dims=dim)
        coord_f = delta_c.cumsum(dim) + (ppg - 0.5 * delta_c[0])
        coord_c = coord_f.rolling({dim: 2}).mean().fillna(ppg)
        delta_f = coord_c.diff(dim).pad({dim: (0, 1)}, constant_values=delta_c[-1])

        # Add attributes
        for da in [coord_c, coord_f]:
            da.attrs = dict(
                units="m", long_name=f"{dim}-coordinate in Cartesian system"
            )
        for da in [delta_c, delta_f]:
            da.attrs = dict(units="m", long_name=f"{dim}-axis spacing")

        # Fill dataset
        eprefix = "e" + ("1" if dim == "x" else "2")
        gprefix = "g" + ("lam" if dim == "x" else "phi")
        nav_coord = "nav_" + ("lon" if dim == "x" else "lat")
        vel_c = "v" if dim == "x" else "u"
        vel_f = "v" if dim == "y" else "u"
        ds[nav_coord] = ds[gprefix + "t"] = ds[gprefix + vel_c] = coord_c
        ds[gprefix + "f"] = ds[gprefix + vel_f] = coord_f
        ds[eprefix + "t"] = ds[eprefix + vel_c] = delta_c  # TODO convert to metres
        ds[eprefix + "f"] = ds[eprefix + vel_f] = delta_f  # TODO convert to metres

        # Upgrade dimension to coordinate so we can add CF-attributes
        ds[dim] = ds[dim]
        ds[dim].attrs = dict(axis=dim.upper(), long_name=f"{dim}-dimension index")

    # Generate 2D coordinates (create dask arrays before broadcasting).
    # Order dims (y, x) for convenience (e.g., for plotting).
    (ds,) = xr.broadcast(ds if chunks is None else ds.chunk(chunks))
    ds = ds.transpose(*("y", "x"))

    # Rotate grid?
    if degrees != 0:
        origin = (np.mean(ds.glamt.values.ravel()), np.mean(ds.gphit.values.ravel()))

        np.stack((ds.glamt.values.ravel(), ds.gphit.values.ravel()), axis=1)
        lon, lat = _rotate(
            ds["glamt"].values.copy(),
            ds["gphit"].values.copy(),
            origin=origin,
            degrees=degrees,
        )
        ds["glamt"] = ds["glamt"].copy(data=lon)
        ds["gphit"] = ds["gphit"].copy(data=lat)

        np.stack((ds.glamt.values.ravel(), ds.gphit.values.ravel()), axis=1)
        lon, lat = _rotate(
            ds["glamu"].values.copy(),
            ds["gphiu"].values.copy(),
            origin=origin,
            degrees=degrees,
        )
        ds["glamu"] = ds["glamu"].copy(data=lon)
        ds["gphiu"] = ds["gphiu"].copy(data=lat)

        np.stack((ds.glamt.values.ravel(), ds.gphit.values.ravel()), axis=1)
        lon, lat = _rotate(
            ds["glamv"].values.copy(),
            ds["gphiv"].values.copy(),
            origin=origin,
            degrees=degrees,
        )
        ds["glamv"] = ds["glamv"].copy(data=lon)
        ds["gphiv"] = ds["gphiv"].copy(data=lat)

        np.stack((ds.glamt.values.ravel(), ds.gphit.values.ravel()), axis=1)
        lon, lat = _rotate(
            ds["glamf"].values.copy(),
            ds["gphif"].values.copy(),
            origin=origin,
            degrees=degrees,
        )
        ds["glamf"] = ds["glamf"].copy(data=lon)
        ds["gphif"] = ds["gphif"].copy(data=lat)

    return ds.set_coords(ds.variables)


def merge_z3_and_e3(
    ds_bathy, z3t: DataArray, z3w: DataArray, e3t: DataArray, e3w: DataArray
) -> Dataset:
    """
    Merge {z,e}3{t,w} with ds_bathy, broadcasting and adding CF attributes.

    {z,e}3{t,w} are coordinates of the returned dataset.
    """
    # Merge computed variables with bathymetry
    ds = xr.Dataset({"gdept_0": z3t, "gdeptw_0": z3w, "e3t": e3t, "e3w": e3w})
    ds = ds.broadcast_like(ds_bathy["Bathymetry"])
    ds = ds.set_coords(ds.variables)
    ds = ds.merge(ds_bathy)

    # Merge 1d variables with bathymetry
    ds_1d = xr.Dataset(
        {"gdept_1d": z3t, "gdeptw_1d": z3w, "e3t_1d": e3t, "e3w_1d": e3w}
    )
    ds_1d = ds_1d.set_coords(ds_1d.variables)
    ds = ds_1d.merge(ds)

    # Add CF attributes
    ds["z"] = ds["nav_lev"] = ds["z"]
    ds["z"].attrs = dict(axis="Z", long_name="z-dimension index")
    for var in ["gdept_0", "gdeptw_0", "gdept_1d", "gdeptw_1d"]:
        ds[var].attrs = dict(
            standard_name="depth", long_name="Depth", units="m", positive="down"
        )
    for var in ["gdept_0", "gdeptw_0", "gdept_1d", "gdeptw_1d"]:
        ds[var].attrs = dict(
            standard_name="cell_thickness", long_name="Thickness", units="m"
        )
    ds = ds.transpose("z", "y", "x")

    return _add_mbathy(ds)


def _add_mbathy(ds: Dataset) -> Dataset:
    """
    Infer sea mask from bathymetry.

    Parameters
    ----------
    ds: Dataset
        Dataset with Bathymetry variable

    Returns
    -------
    Dataset.
    """
    ds["mbathy"] = xr.where(
        ds["Bathymetry"] > 0, ds.z.size, 0
    )  # TODO: should this be bool?
    return ds


def generate_variables(
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
    ds["uvel"] = uvel
    ds["vvel"] = vvel
    ds["ssh"] = ssh

    # Add t dim
    # times = pd.date_range("2020","2023",freq='Y')+ DateOffset(months=6)
    times = xr.cftime_range("2000", periods=3, freq="A-JUN", calendar="standard")
    da_t = xr.DataArray(times, [("t", times)])
    ds = ds.expand_dims(dim={"t": da_t})
    ds = ds.transpose("t", "z", "y", "x")
    ds["t"] = ds["t"]

    return ds
