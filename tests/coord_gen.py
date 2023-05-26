"""
Created on Wed Mar 11 11:16:57 2020.

example grid set up

@author: jdha
"""
import numpy as np
from netCDF4 import Dataset


def set_hgrid(dx, dy, jpi, jpj, zoffx, zoffy, nghost):
    # Set grid positions [km]
    latt = np.zeros((jpi, jpj))
    lont = np.zeros((jpi, jpj))
    lonu = np.zeros((jpi, jpj))
    latu = np.zeros((jpi, jpj))
    lonv = np.zeros((jpi, jpj))
    latv = np.zeros((jpi, jpj))
    lonf = np.zeros((jpi, jpj))
    latf = np.zeros((jpi, jpj))

    for i in range(0, jpi):
        lont[i, :] = zoffx * dx * 1.0e-3 + dx * 1.0e-3 * np.float(i)
        lonu[i, :] = zoffx * dx * 1.0e-3 + dx * 1.0e-3 * (np.float(i) + 0.5)

    for j in range(0, jpj):
        latt[:, j] = zoffy * dy * 1.0e-3 + dy * 1.0e-3 * float(j)
        latv[:, j] = zoffy * dy * 1.0e-3 + dy * 1.0e-3 * (float(j) + 0.5)

    lonv = lont
    lonf = lonu
    latu = latt
    latf = latv

    e1t = np.ones((jpi, jpj)) * dx
    e2t = np.ones((jpi, jpj)) * dy
    e1u = np.ones((jpi, jpj)) * dx
    e2u = np.ones((jpi, jpj)) * dy
    e1v = np.ones((jpi, jpj)) * dx
    e2v = np.ones((jpi, jpj)) * dy
    e1f = np.ones((jpi, jpj)) * dx
    e2f = np.ones((jpi, jpj)) * dy

    # Set bathymetry [m]:
    batt = 500.0 + 0.5 * 1500.0 * (1.0 + np.tanh((lont - 40.0) / 7.0))

    # Set surface mask:
    ktop = np.zeros((jpi, jpj))
    ktop[1 : jpi - 1, nghost + 1 : jpj - nghost - 1] = 1
    batt = np.where((ktop == 0.0), 0.0, batt)

    # Set coriolis parameter:
    ff_t = np.zeros((jpi, jpj))
    ff_f = np.zeros((jpi, jpj))

    return (
        lont,
        latt,
        lonu,
        latu,
        lonv,
        latv,
        lonf,
        latf,
        e1t,
        e2t,
        e1u,
        e2u,
        e1v,
        e2v,
        e1f,
        e2f,
        batt,
        ktop,
        ff_f,
        ff_t,
    )


def write_coord(
    fileout,
    lont,
    latt,
    lonu,
    latu,
    lonv,
    latv,
    lonf,
    latf,
    e1t,
    e2t,
    e1u,
    e2u,
    e1v,
    e2v,
    e1f,
    e2f,
):
    """
    Writes out a NEMO formatted coordinates file.

    Parameters
    ----------
        fileout         (string): filename
        lon[t/u/v/f](np.ndarray): longitude array at [t/u/v/f]-points (2D)
        lat[t/u/v/f](np.ndarray): latitude array at [t/u/v/f]-points (2D)
        e1[t/u/v/f] (np.ndarray): zonal scale factors at [t/u/v/f]-points
        e2[t/u/v/f] (np.ndarray): meridional scale factors at [t/u/v/f]-points

    Returns
    -------
        None
    """
    # Open pointer to netcdf file
    dataset = Dataset(fileout, "w", format="NETCDF4_CLASSIC")

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nx, ny = np.shape(lont)
    dataset.createDimension("x", nx)
    dataset.createDimension("y", ny)

    # Create Variables
    nav_lon = dataset.createVariable("nav_lon", np.float32, ("y", "x"))
    nav_lat = dataset.createVariable("nav_lat", np.float32, ("y", "x"))

    glamt = dataset.createVariable("glamt", np.float64, ("y", "x"))
    glamu = dataset.createVariable("glamu", np.float64, ("y", "x"))
    glamv = dataset.createVariable("glamv", np.float64, ("y", "x"))
    glamf = dataset.createVariable("glamf", np.float64, ("y", "x"))
    gphit = dataset.createVariable("gphit", np.float64, ("y", "x"))
    gphiu = dataset.createVariable("gphiu", np.float64, ("y", "x"))
    gphiv = dataset.createVariable("gphiv", np.float64, ("y", "x"))
    gphif = dataset.createVariable("gphif", np.float64, ("y", "x"))

    ge1t = dataset.createVariable("e1t", np.float64, ("y", "x"))
    ge1u = dataset.createVariable("e1u", np.float64, ("y", "x"))
    ge1v = dataset.createVariable("e1v", np.float64, ("y", "x"))
    ge1f = dataset.createVariable("e1f", np.float64, ("y", "x"))
    ge2t = dataset.createVariable("e2t", np.float64, ("y", "x"))
    ge2u = dataset.createVariable("e2u", np.float64, ("y", "x"))
    ge2v = dataset.createVariable("e2v", np.float64, ("y", "x"))
    ge2f = dataset.createVariable("e2f", np.float64, ("y", "x"))

    nav_lon.units, nav_lon.long_name = "km", "X"
    nav_lat.units, nav_lat.long_name = "km", "Y"

    # Populate file with input data
    # TODO: do we need to transpose?
    nav_lon[:, :] = lont.T
    nav_lat[:, :] = latt.T

    glamt[:, :] = lont.T
    glamu[:, :] = lonu.T
    glamv[:, :] = lonv.T
    glamf[:, :] = lonf.T
    gphit[:, :] = latt.T
    gphiu[:, :] = latu.T
    gphiv[:, :] = latv.T
    gphif[:, :] = latf.T

    ge1t[:, :] = e1t.T
    ge1u[:, :] = e1u.T
    ge1v[:, :] = e1v.T
    ge1f[:, :] = e1f.T
    ge2t[:, :] = e2t.T
    ge2u[:, :] = e2u.T
    ge2v[:, :] = e2v.T
    ge2f[:, :] = e2f.T

    # Close off pointer
    dataset.close()


def write_domcfg(
    fileout,
    ln_zco,
    ln_zps,
    ln_sco,
    ln_isfcav,
    jperio,
    bat,
    lont,
    latt,
    lonu,
    latu,
    lonv,
    latv,
    lonf,
    latf,
    e1t,
    e2t,
    e1u,
    e2u,
    e1v,
    e2v,
    e1f,
    e2f,
    ff_f,
    ff_t,
    dept_1d,
    e3t_1d,
    e3w_1d,
    e3t,
    e3u,
    e3v,
    e3f,
    e3w,
    e3uw,
    e3vw,
    ktop,
    kbot,
):
    """
    Writes out a NEMO formatted domcfg file.

    Parameters
    ----------
        fileout         (string): filename
        ln_zco         (logical): vertical coordinate flag [z-level]
        ln_zps         (logical): vertical coordinate flag [z-partial-step]
        ln_sco         (logical): vertical coordinate flag [sigma]
        ln_isfcav      (logical): ice cavity flag
        jperio             (int): domain type
        bat         (np.ndarray): bathymetry array at t-points (2D)
        lon[t/u/v/f](np.ndarray): longitude array at [t/u/v/f]-points (2D)
        lat[t/u/v/f](np.ndarray): latitude array at [t/u/v/f]-points (2D)
        e1[t/u/v/f] (np.ndarray): zonal scale factors at [t/u/v/f]-points
        e2[t/u/v/f] (np.ndarray): meridional scale factors at [t/u/v/f]-points
        ff_[f/t]    (np.ndarray): coriolis parameter at [t/f]-points
        dept_1d     (np.ndarray): 1D depth levels at t-points
        e3[t/w]_1d  (np.ndarray): 1D vertical scale factors at [t/w]-points
        e3[t/u/v/f] (np.ndarray): vertcal scale factors at [t/u/v/f]-points
        e3[w/uw/vw] (np.ndarray): vertcal scale factors at [w/uw/vw]-points
        ktop        (np.ndarray): upper most wet point
        kbot        (np.ndarray): lower most wet point

    Returns
    -------
        None
    """
    # Open pointer to netcdf file
    dataset = Dataset(fileout, "w", format="NETCDF4_CLASSIC")

    # Get input size and create appropriate dimensions
    # TODO: add some sort of error handling
    nx, ny, nz = np.shape(e3t)
    dataset.createDimension("x", nx)
    dataset.createDimension("y", ny)
    dataset.createDimension("z", nz)

    # create Variables
    nav_lon = dataset.createVariable("nav_lon", np.float32, ("y", "x"))
    nav_lat = dataset.createVariable("nav_lat", np.float32, ("y", "x"))
    nav_lev = dataset.createVariable("nav_lev", np.float32, "z")

    giglo = dataset.createVariable("jpiglo", "i4")
    gjglo = dataset.createVariable("jpjglo", "i4")
    gkglo = dataset.createVariable("jpkglo", "i4")

    gperio = dataset.createVariable("jperio", "i4")

    gzco = dataset.createVariable("ln_zco", "i4")
    gzps = dataset.createVariable("ln_zps", "i4")
    gsco = dataset.createVariable("ln_sco", "i4")
    gcav = dataset.createVariable("ln_isfcav", "i4")

    ge3t1d = dataset.createVariable("e3t_1d", np.float64, "z")
    ge3w1d = dataset.createVariable("e3w_1d", np.float64, "z")
    gitop = dataset.createVariable("top_level", "i4", ("y", "x"))
    gibot = dataset.createVariable("bottom_level", "i4", ("y", "x"))
    gbat = dataset.createVariable("Bathymetry", np.float64, ("y", "x"))
    glamt = dataset.createVariable("glamt", np.float64, ("y", "x"))
    glamu = dataset.createVariable("glamu", np.float64, ("y", "x"))
    glamv = dataset.createVariable("glamv", np.float64, ("y", "x"))
    glamf = dataset.createVariable("glamf", np.float64, ("y", "x"))
    gphit = dataset.createVariable("gphit", np.float64, ("y", "x"))
    gphiu = dataset.createVariable("gphiu", np.float64, ("y", "x"))
    gphiv = dataset.createVariable("gphiv", np.float64, ("y", "x"))
    gphif = dataset.createVariable("gphif", np.float64, ("y", "x"))
    ge1t = dataset.createVariable("e1t", np.float64, ("y", "x"))
    ge1u = dataset.createVariable("e1u", np.float64, ("y", "x"))
    ge1v = dataset.createVariable("e1v", np.float64, ("y", "x"))
    ge1f = dataset.createVariable("e1f", np.float64, ("y", "x"))
    ge2t = dataset.createVariable("e2t", np.float64, ("y", "x"))
    ge2u = dataset.createVariable("e2u", np.float64, ("y", "x"))
    ge2v = dataset.createVariable("e2v", np.float64, ("y", "x"))
    ge2f = dataset.createVariable("e2f", np.float64, ("y", "x"))
    gfff = dataset.createVariable("ff_f", np.float64, ("y", "x"))
    gfft = dataset.createVariable("ff_t", np.float64, ("y", "x"))
    ge3t = dataset.createVariable("e3t_0", np.float64, ("z", "y", "x"))
    ge3w = dataset.createVariable("e3w_0", np.float64, ("z", "y", "x"))
    ge3u = dataset.createVariable("e3u_0", np.float64, ("z", "y", "x"))
    ge3v = dataset.createVariable("e3v_0", np.float64, ("z", "y", "x"))
    ge3f = dataset.createVariable("e3f_0", np.float64, ("z", "y", "x"))
    ge3uw = dataset.createVariable("e3uw_0", np.float64, ("z", "y", "x"))
    ge3vw = dataset.createVariable("e3vw_0", np.float64, ("z", "y", "x"))

    nav_lon.units, nav_lon.long_name = "km", "X"
    nav_lat.units, nav_lat.long_name = "km", "Y"

    # Populate file with input data
    giglo[:] = nx
    gjglo[:] = ny
    gkglo[:] = nz

    gzco[:] = ln_zco
    gzps[:] = ln_zps
    gsco[:] = ln_sco
    gcav[:] = ln_isfcav

    gperio[:] = jperio

    # TODO: do we need to transpose?
    nav_lon[:, :] = lont.T
    nav_lat[:, :] = latt.T
    nav_lev[:] = dept_1d

    ge3t1d[:] = e3t_1d
    ge3w1d[:] = e3w_1d

    gitop[:, :] = ktop.T
    gibot[:, :] = kbot.T

    gbat[:, :] = bat.T

    glamt[:, :] = lont.T
    glamu[:, :] = lonu.T
    glamv[:, :] = lonv.T
    glamf[:, :] = lonf.T
    gphit[:, :] = latt.T
    gphiu[:, :] = latu.T
    gphiv[:, :] = latv.T
    gphif[:, :] = latf.T

    ge1t[:, :] = e1t.T
    ge1u[:, :] = e1u.T
    ge1v[:, :] = e1v.T
    ge1f[:, :] = e1f.T
    ge2t[:, :] = e2t.T
    ge2u[:, :] = e2u.T
    ge2v[:, :] = e2v.T
    ge2f[:, :] = e2f.T
    gfff[:, :] = ff_f.T
    gfft[:, :] = ff_t.T

    ge3t[:, :, :] = e3t.T
    ge3w[:, :, :] = e3w.T
    ge3u[:, :, :] = e3u.T
    ge3v[:, :, :] = e3v.T
    ge3f[:, :, :] = e3f.T
    ge3uw[:, :, :] = e3uw.T
    ge3vw[:, :, :] = e3vw.T

    # Close off pointer
    dataset.close()
