Tidal Boundary Conditions Generation
====================================

By providing a global tidal model dataset (TPXO and FES are currently supported) PyNEMO can generate boundary conditions for the
NEMO configuration supplied using the namelist file.

Namelist options
----------------

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
constants in one netcdf file whereas FES has three separate netcdf files (one for amplitude two for currents) for each constant. Extra harmonics can be appended
to the clname(n) list. FES supports 34 constants and TPXO7.2 has 13 to choose from. Other versions of TPXO should work with PyNEMO
but have not been yet been tested. **NOTE** FES dataset filenames must have be in the format of constituent then type. e.g.::

    M2_Z.nc (for amplitude)
    M2_U.nc (for U component of velocity)
    M2_V.nc (for V component of velocity)

If this is not undertaken the PyNEMO will not recognise the files. TPXO data files are specified directly so these can be anyname although it is best to stick with the default
names as shown above. So far the tidal model datasets have been downloaded and used locally but could also be stored on a THREDDS server although this has
not been tested with the global tide models.

Other options include "ln_tide" a boolean that when set to true will generate tidal boundaries. "sn_tide_model" is a string that defines the model to use, currently only
"fes" or "tpxo" are supported. "ln_trans" is a boolean that when set to true will interpolate transport rather than velocities.

Future work
-----------

Create options of harmonic constants to request rather than manually specifying a list. These could be based on common requirements
and/or based on the optimal harmonics to use for a specified time frame.


