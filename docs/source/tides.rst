Tidal Boundary Conditions Generation
====================================

By providing a global tidal model dataset (TPXO and FES are currently supported) PyNEMO can generate boundary conditions for the
NEMO configuration supplied using the namelist file.

To use the namelist needs to be configured with the required options. These are listed below::

    ln_tide        = .true.              !  =T : produce bdy tidal conditions
    sn_tide_model  = 'fes'                !  Name of tidal model (fes|tpxo)
    clname(1)      = 'M2'                 !  constituent name
    clname(2)      = 'S2'
    clname(3)      = 'O1'
    clname(4)      = 'K1'
    clname(5)      = 'N2'
    ln_trans       = .false.               !  interpolate transport rather than velocities
    ! TPXO file locations
    sn_tide_grid   = './grid_tpxo7.2.nc'
    sn_tide_h      = './h_tpxo7.2.nc'
    sn_tide_u      = './u_tpxo7.2.nc'
    ! location of FES data
    sn_tide_fes      = './FES/'

these options define the location of the tidal model datasets, note this differs depending on model as TPXO has all harmonic
constants in one netcdf file whereas FES has three separate netcdf files for each constant. Extra harmonics can be appended
to the clname(n) list FES supports 34 constants and TPXO7.2 has 13 to choose from. Other versions of TPXO should work with PyNEMO
but have not been yet been tested.

So far the tidal model datasets have been downloaded and used locally but could also be stored on a TREDDS server although this has
not been tested to generate tidal boundaries

Future work
-----------

Create options of harmonic constants to request rather than manually specifying a list. These could be based on common requirements
and/or based on the optimal harmonics to use for a specified time frame.


