# pyBDY Documentation

**Welcome to the documentation for pyBDY (NEMO lateral boundary conditions)**

## Introduction

pyBDY is a python package to generate lateral boundary conditions for regional NEMO model configurations.
It has been developed to uses geographical and depth information from an a source data (e.g. a global ocean
simulation) and translate them to a destination NEMO region simulation. It makes use of a kdtree approximate
nearest neighbour algorithm in order to provide a generic method of weighted average interpolation for any
flavour of ocean model. The available options are accessed through a NEMO style namelist.

---

## Contents

- [How to cite :bookmark:](#how-to-cite-bookmark)
- [Change Log :twisted_rightwards_arrows:](#change-log-twisted_rightwards_arrows)
- [Dependencies :globe_with_meridians:](#dependencies-globe_with_meridians)
- [Quick Start Installation :rocket:](#quick-start-installation-rocket)
- [How to use pyBDY :student:](#how-to-use-pybdy-student)
- [Worked Example :mechanical_arm:](#worked-example-mechanical_arm)
- [Tidal Boundary Conditions Generation :sailboat:](#tidal-boundary-conditions-generation-sailboat)
- [Troubleshooting :safety_vest:](#troubleshooting-safety_vest)
- [pyBDY Module Structure :scroll:](#pybdy-module-structure-scroll)

## How to cite :bookmark:

[Back to top](#pybdy-documentation)

Please cite pyBDY version 0.4.0 in your work using:

Harle, J., Barton, B.I., Nagella, S., Crompton, S., Polton J., Patmore, R., Morado, J., Prime, T., Wise, A., De Dominicis, M., Blaker, A. Farey, J.K., (2025). pyBDY - NEMO lateral boundary conditions v0.4.0 [Software]. [https://doi.org](<>)

## Change Log :twisted_rightwards_arrows:

[Back to top](#pybdy-documentation)

The lastes version of pyBDY is version 0.4.0.
The changes relative to the previous version (0.3.0) are:

- Sigma to sigma vertical layer interpolation is now possible.
- Vertical interpolation in pyBDY can now be turned off for zco vertical coodinate data.
- Time input in the namelist has changed to offer more granularity.
- Grid variables names are now specified using a .json file instead of .ncml. Source data is still specified with .nmcl.
- The boundary is split into chunks to allow for processing smaller sections of data.
- Boundaries that cross an east - west wrap in source data can be processed.
- The 1-2-1 horizontal filter has been turned off.
- The *seawater* dependancy updated to *gsw*.
- A plotting masking bug has been fixed.
- There is now horizontal flood filling that will remove zeros from salinity and temperature near land.
- Bug fix for 90 boundaries that meet diagonally to produce a 90 degree corner.
- Some unit tests have been added and full integration tests.
- Documentation has been updated and restructured.

**There is a new library for generating NEMO initial conditions called pyIC.**
pyIC can be found at: [https://github.com/NOC-MSM/pyIC](https://github.com/NOC-MSM/pyIC)

## Dependencies :globe_with_meridians:

[Back to top](#pybdy-documentation)

pyBDY is installed under a conda/mamba environment to aid wider distribution and to facilitate development.
The key dependecies are listed below:

- python=3.9
- netCDF4
- scipy
- numpy
- xarray
- matplotlib
- cartopy
- thredds_crawler
- seawater
- pyqt5
- pyjnius
- cftime
- gsw

A recent JAVA installation is also required.

---

## Quick Start Installation :rocket:

[Back to top](#pybdy-documentation)

To get started, check out and set up an instance of the pyBDY GitHub [repository](https://github.com/NOC-MSM/pyBDY):

```sh
export PYBDY_DIR=$PWD/pyBDY
git clone git@github.com:NOC-MSM/pyBDY.git
```

\*\*Helpful Tip...

```
- **It is not advised to checkout the respository in your home directory.**
```

Creating a specific conda virtual environment is highly recommended ([click here for more about virtual
enviroments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)).
Load conda (e.g. through anaconda/miniforge) and create the environment through the provided `environment.yml` file.

```sh
cd $PYBDY_DIR
conda env create -n pybdy -f environment.yml
```

Activate the new environment

```sh
conda activate pybdy
```

Install pyBDY

```sh
pip install -e .
```

Make sure the Java Runtime Environment is set:

```sh
export JAVA_HOME=path_to_jre
```

Generalised methods for defining paths are as follows:

```
export JAVA_HOME=$(readlink -f $(which java)) # UNIX
export JAVA_HOME=$(/usr/libexec/java_home)    # Mac
```

To check that pyBDY have been correctly installed in the virtual environment,
enter the following command:

```
pybdy -v
```

If it has you should see the help usage prompt:

```
usage: pybdy -g -s <namelist.bdy>
```

If not please see the troubleshooting pages for common causes as
to why the installation may fail.

To deactivate the conda environment:

```
conda deactivate
```

## How to use pyBDY :student:

[Back to top](#pybdy-documentation)

In this documentation "bdy points" refer to the output boundary points generated by pyBDY.
First follow the installation instructions [Quick Start Installation](#quick-start-installation-rocket).

### Step 1: File Preparation

Copy and paste the following files into your working directory:

- `inputs/namelist_local.bdy`

- `inputs/grid_name_map.json`

- `inputs/src_data_local.ncml`

- `namelist.bdy`: Specifies file paths and configuration options.

- `grid_name_map.json`: Defines variable names in horizontal and vertical grid files.

- `src_data.ncml`: Aggregates and remaps source data variables for PyBDY.

### Step 2: Edit the Namelist `namelist_local.bdy`

Descriptions of all required variables are in
[`src/pybdy/variable.info`](https://github.com/NOC-MSM/pyBDY/blob/master/src/pybdy/variable.info).
Here we will summarise the main variables that will need changing to get started.

#### Key Namelist Parameters

- `sn_src_hgr`
- `sn_src_zgr`
- `sn_dst_hgr`
- `sn_dst_zgr`
- `sn_src_msk`
- `sn_bathy`
- `sn_nme_map`
- `sn_src_dir`
- `sn_dst_dir`
- `cn_mask_file`
- `ln_zinterp`
- `nn_rimwidth`

##### File Paths

Directory paths in bdy file can be relative or absolute.
The application picks the relative path from the current working directory.

- **`sn_src_hgr`**: Source horizontal grid file. Should include:

    - Ideal: `glamt`, `gphit`, `glamu`, `e1t`, `e2t`, `e1u`, etc.
    - Minimum: `nav_lat`, `nav_lon` on a 2D grid.
    - Use `ncdump -h` or `ncview` to inspect variables.
    - Map extra variable names in `grid_name_map.json` to avoid recalculation.

- **`sn_src_zgr`**: Source vertical grid file. May be the same as `sn_src_hgr`.

    - Ideal: `gdept`, `e3t`, `mbathy` (aka `bottom_level`)
    - If `mbathy` is missing:
        - Use `gdept_0` (1D depth)
        - Use any 2D field (e.g., `nav_lon`) for `mbathy`
        - **Not recommended for destination**
    - Map variables like `gdepw`, `gdepu`, `e3w` in `grid_name_map.json`
    - **Note**: Time-varying depths are not used in PyBDY.

- **`sn_dst_hgr`, `sn_dst_zgr`**: Destination equivalents of the above.

- **`sn_src_msk`**: Source mask file with variables:

    - `tmask`, `umask`, `vmask`, `fmask`

- **`sn_bathy`**: Destination bathymetry file with variable:

    - `Bathymetry`

    - Used to calculate boundary mask if `ln_mask_file` is unset.

    - Can be computed from `e3w` and `bottom_level`:

        ```python
        gdepw = np.cumsum(e3w, axis=1)
        grid = np.indices(bottom_level.shape)
        bathy = gdepw[bottom_level, grid[0], grid[1]]
        ```

- **`sn_nme_map`**: Path to `grid_name_map.json`

    - **Note**: `ncml` is no longer used for grid input. Use `grid_name_map.json` instead. See [`inputs/grid_name_map_readme.txt`](https://github.com/NOC-MSM/pyBDY/blob/master/inputs/grid_name_map_readme.txt) for variable descriptions.

- **`sn_src_dir`**: Path to `src_data.ncml`

    - This is an xml file that points to source data (not grid) paths. It can also include THREDDS URLs (see `inputs/namelist_remote.bdy` for example).
    - See `inputs` folder for more examples.

    Example structure:

    ```xml
    <ns0:netcdf xmlns:ns0="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2" title="aggregation example">
      <ns0:aggregation type="union">
        <ns0:netcdf>
          <ns0:aggregation type="joinExisting" dimName="time_counter">
            <ns0:scan location="/path_to_src_data/Data/" regExp=".*grid_T.*" />
          </ns0:aggregation>
        </ns0:netcdf>
        <ns0:netcdf>
          <ns0:aggregation type="joinExisting" dimName="time_counter">
            <ns0:scan location="/path_to_src_data/Data/" regExp=".*grid_U.*" />
          </ns0:aggregation>
        </ns0:netcdf>
        <ns0:netcdf>
          <ns0:aggregation type="joinExisting" dimName="time_counter">
            <ns0:scan location="/path_to_src_data/Data/" regExp=".*grid_V.*" />
          </ns0:aggregation>
        </ns0:netcdf>
      </ns0:aggregation>
    </ns0:netcdf>
    ```

    - Regular expression (Regex) is a special text string that can be used in the xml file for describing a search pattern to match against some text. You may compare using regex to filter what files to include in your datasets against using wildcard (\*) to specify a file search pattern in your computer. More information on Regex patterns can be found here [Regex](https://learn.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-language-quick-reference).

- **`sn_dst_dir`**: Output directory for PyBDY data

##### Other Settings

- **`cn_mask_file`** *(optional)*: Used to define open boundaries.

    - Values: `-1` (out-of-domain), `0` (land), `1` (water)
    - If not provided, PyBDY uses bathymetry to infer boundaries

- **`ln_zinterp`**: Disables vertical interpolation if `false` and source uses zco levels.

    - Output will match source vertical levels
    - If source uses zps or sco, this will be set to `true` automatically

- **`nn_rimwidth`**: Number of interior boundary points to generate

    - Typical value: `9`
    - For tidal boundaries: `1`

#### Time Settings

- Ensure `time_counter` exists in source files
- Files must be time-ascending
- NetCDF time metadata must include:
    - `calendar`: `"gregorian"`, `"noleap"`, or `"360_day"`
    - `units`: `"seconds since YYYY-MM-DD hh:mm:ss"`

##### Required Namelist Time Parameters

- **`sn_date_start`**: Start date for output (format: `YYYY-MM-DD`)
- **`sn_date_end`**: End date for output (format: `YYYY-MM-DD`)
    - The start date and end date of output must fall within the source data time range.
- **`sn_dst_calendar`**: Output calendar format
- **`sn_date_origin`**: Time counter reference date for output (format: `YYYY-MM-DD`)
- **`ln_time_interpolation`**: If `true`, interpolate to daily steps.
    - If `false`, output uses source data calendar (monthly steps only)

### Step 3: Running pyBDY

To use pyBDY, the following command is entered: (the example will run a benchmarking test):

```
pybdy -s /path/to/namelist/file (e.g. ./inputs/namelist_remote.bdy)
```

This command line tool reads a BDY file, extracts boundary data and prepares the data for a NEMO simulation.

## Worked Example :mechanical_arm:

[Back to top](#pybdy-documentation)

Here we show a worked example of how to set up the namelist for a different domain than the examples found in the *inputs* folder.
The example child (destination) here is a regional NEMO model that covers the Indian Ocean and the parent (source) used here is a global NEMO model.

### Namelist File

Below is excerpts from an example *namelist.bdy*.

Here the file paths are set. These can be absolute (i.e. starting with "/") or relative (i.e. starting with "./").

```
!------------------------------------------------------------------------------
!  grid information
!------------------------------------------------------------------------------
   sn_src_hgr = '/scratch/India_Test/mesh_mask_ORCA025_light.nc4'
   sn_src_zgr = '/scratch/India_Test/20241211_restart.nc'
   sn_dst_hgr = '/scratch/India_Test/domain_cfg.nc'     ! Expects vars found in domain_cfg.nc
   sn_dst_zgr = '/scratch/India_Test/domain_cfg.nc'     ! Expects vars: {e3u,e3v,e3w,e3t,nav_lat,nav_lon,mbathy}
   sn_src_msk = '/scratch/India_Test/mask_3D.nc'
   sn_bathy   = '/scratch/India_Test/domain_cfg_bathy.nc'    ! dst bathymetry w/o time dimension
                                                                            !Expects vars: {Bathymetry,nav_lat,nav_lon}
   sn_nme_map = './india_test/grid_name_map.json'     ! json file mapping variable names to netcdf vars
```

Here the source (parent) data is specified via the .nmcl file in XML format. The output directory, file name prefix and *\_FillValue* in the netCDF4 file is specified.

```
!------------------------------------------------------------------------------
!  I/O
!------------------------------------------------------------------------------
   sn_src_dir = './india_test/src_data_local.ncml' ! src_files/'
   sn_dst_dir = '/scratch/benbar/India_Test/'
   sn_fn      = 'india'             ! prefix for output files
   nn_fv      = -1e20                 !  set fill value for output files
   nn_src_time_adj = 0                ! src time adjustment
   sn_dst_metainfo = 'India Data'
```

Here some options are set. cn_coords_file is a file that can be output by pybdy.
In this case, the child (destination) data does not have a pre-defined mask file so pybdy will use the bathymetry provided in sn_bathy to calculate the mask. If the mask produced if not giving the correct boundaries you may need to provide a mask.nc file which you generate. This file contains a 2d mask the same shape as the bathymetry where 1 = "water", 0 = "land" and -1 = "out of domain". Boundary points will be generated between water and "out of domain" which can also be where water meets the edge of the defined 2d area.
ln_dyn3d and ln_dyn3d define variables that will be in the output. Here, ln_dyn2d will provide an additon variable in the output for barotropic velocities and ln_dyn3d will not include the barotropic component in the 3d velocities. One or the other should be selected and match options in NEMO.
Here, ln_tra shows temperature and salinity will be output. ln_ice shows ice will not be output. ln_zinterp shows the vertical interpolation is calculated by pybdy (so should be turned off in NEMO).
Here, nn_rimwidth is set to 9 to provide 9 layers of boundary points along all boundaries.

```
!------------------------------------------------------------------------------
!  unstructured open boundaries
!------------------------------------------------------------------------------
    ln_coords_file = .true.               !  =T : produce bdy coordinates files
    cn_coords_file = 'coordinates.bdy.nc' !  name of bdy coordinates files
                                          !  (if ln_coords_file=.TRUE.)
    ln_mask_file   = .false.              !  =T : read mask from file
    cn_mask_file   = 'mask.nc'            !  name of mask file
                                          !  (if ln_mask_file=.TRUE.)
    ln_dyn2d       = .true.               !  boundary conditions for
                                          !  barotropic fields
    ln_dyn3d       = .false.              !  boundary conditions for
                                          !  baroclinic velocities
    ln_tra         = .true.               !  boundary conditions for T and S
    ln_ice         = .false.              !  ice boundary condition
    ln_zinterp     = .true.               !  vertical interpolation
    nn_rimwidth    = 9                    !  width of the relaxation zone
```

In this example we are not producing the tidal forcing on the boundary because ln_tide is set to false. This means the rest of this section does not matter.

```
!------------------------------------------------------------------------------
!  unstructured open boundaries tidal parameters
!------------------------------------------------------------------------------
    ln_tide        = .false.              !  =T : produce bdy tidal conditions
    sn_tide_model  = 'FES2014'            !  Name of tidal model. Accepts FES2014, TPXO7p2, or TPXO9v5
    clname(1)      = 'M2'                 !  constituent name
    clname(2)      = 'S2'
    clname(3)      = 'K2'
    clname(4)      = 'O1'
    clname(5)      = 'P1'
    clname(6)      = 'Q1'
    clname(7)      = 'M4'
    ln_trans       = .true.               !  interpolate transport rather than
                                          !  velocities
    ! location of TPXO7.2 data
    sn_tide_grid_7p2   = './inputs/tpxo7.2/grid_tpxo7.2.nc'
    sn_tide_h          = './inputs/tpxo7.2/h_tpxo7.2.nc'
    sn_tide_u          = './inputs/tpxo7.2/u_tpxo7.2.nc'
    ! location of TPXO9v5 data: single constituents per file
    sn_tide_grid_9p5   = './inputs/TPXO9_atlas_v5_nc/grid_tpxo9_atlas_30_v5.nc'
    sn_tide_dir        = './inputs/TPXO9_atlas_v5_nc/'
    ! location of FES2014 data
    sn_tide_fes        = './inputs/FES2014/'
```

The time step required in output here are 3 days starting on 12th Dec 2024 (which is also used as the reference date).

```
!------------------------------------------------------------------------------
!  Time information for output
!------------------------------------------------------------------------------
    sn_date_start   = '2024-12-12'    !  dst output date start YYYY-MM-DD
    sn_date_end     = '2024-12-15'    !  dst output date end YYYY-MM-DD
    sn_dst_calendar = 'gregorian'     !  output calendar format
    sn_date_origin  = '2024-12-12'    !  reference for time counter YYYY-MM-DD
    ln_time_interpolation = .true. !  set to false to use parent
                                   !  calender for monthly frequency only
```

These parameters can be left unchanged.

```
!------------------------------------------------------------------------------
!  Additional parameters
!------------------------------------------------------------------------------
    nn_wei  = 1                   !  smoothing filter weights
    rn_r0   = 0.041666666         !  decorrelation distance use in gauss
                                  !  smoothing onto dst points. Need to
                                  !  make this a funct. of dlon
    sn_history  = 'Benchmarking test case'
                                  !  history for netcdf file
    ln_nemo3p4  = .true.          !  else presume v3.2 or v3.3
    nn_alpha    = 0               !  Euler rotation angle
    nn_beta     = 0               !  Euler rotation angle
    nn_gamma    = 0               !  Euler rotation angle
    rn_mask_max_depth = 100.0     !  Maximum depth to be ignored for the mask
    rn_mask_shelfbreak_dist = 20000.0 !  Distance from the shelf break
```

### JSON File

The example files name is *grid_name_map.json*.

```
{
    "dimension_map": {
            "t": "t",
            "z": "z",
            "y": "y",
            "x": "x"
    },
    "sc_variable_map": {
            "nav_lon": "nav_lon",
            "nav_lat": "nav_lat",
            "glamt": "glamt",
            "gphit": "gphit",
            "glamf": "glamf",
            "gphif": "gphif",
            "glamu": "glamu",
            "gphiu": "gphiu",
            "glamv": "glamv",
            "gphiv": "gphiv",
            "e1t": "e1t",
            "e2t": "e2t",
            "e1f": "e1f",
            "e2f": "e2f",
            "e1u": "e1u",
            "e2u": "e2u",
            "e1v": "e1v",
            "e2v": "e2v",
            "mbathy": "nav_lon",
            "gdept_0": "nav_lev",
            "gdept": "gdept",
            "gdepu": "gdepu",
            "gdepv": "gdepv",
            "gdepf": "gdepf",
            "gdepw": "gdepw",
            "gdepuw": "gdepuw",
            "gdepvw": "gdepvw",
            "e3t": "e3t",
            "e3w": "e3w",
            "e3u": "e3u",
            "e3v": "e3v",
            "e3f": "e3f",
            "e3uw": "e3uw",
            "e3vw": "e3vw",
            "e3fw": "e3fw"
    },
    "dst_variable_map": {
            "nav_lon": "nav_lon",
            "nav_lat": "nav_lat",
            "glamt": "glamt",
            "gphit": "gphit",
            "glamf": "glamf",
            "gphif": "gphif",
            "glamu": "glamu",
            "gphiu": "gphiu",
            "glamv": "glamv",
            "gphiv": "gphiv",
            "e1t": "e1t",
            "e2t": "e2t",
            "e1f": "e1f",
            "e2f": "e2f",
            "e1u": "e1u",
            "e2u": "e2u",
            "e1v": "e1v",
            "e2v": "e2v",
            "mbathy": "bottom_level",
            "gdept_0": "gdept_0",
            "gdept": "gdept",
            "gdepu": "gdepu",
            "gdepv": "gdepv",
            "gdepf": "gdepf",
            "gdepw": "gdepw",
            "gdepuw": "gdepuw",
            "gdepvw": "gdepvw",
            "e3t": "e3t_0",
            "e3w": "e3w_0",
            "e3u": "e3u_0",
            "e3v": "e3v_0",
            "e3f": "e3f_0",
            "e3uw": "e3uw_0",
            "e3vw": "e3vw_0",
            "e3fw": "e3fw"
    }
}
```

### XML File

This is an example XML file which is used to providing file paths for parent (source) data that pybdy will read in.
The example files name is *src_data_local.ncml*.

```
<?xml version="1.0" encoding="UTF-8"?>
<netcdf title="aggregation example" xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
  <aggregation type="union" >
     <netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
        <aggregation type="joinExisting" dimName="time_counter" >
           <netcdf location="/scratch/benbar/India_Test/mersea.grid_V.nc" />
        </aggregation>
     </netcdf>
     <netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
        <aggregation type="joinExisting" dimName="time_counter" >
           <netcdf location="/scratch/benbar/India_Test/mersea.grid_U.nc" />
        </aggregation>
     </netcdf>
     <netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
        <aggregation type="joinExisting" dimName="time_counter" >
           <netcdf location="/scratch/benbar/India_Test/mersea.grid_T.nc" />
        </aggregation>
     </netcdf>
  </aggregation>
</netcdf>
```

## Tidal Boundary Conditions Generation :sailboat:

[Back to top](#pybdy-documentation)

By providing a global tidal model dataset (TPXO and FES are currently supported) pyBDY can generate boundary conditions for the NEMO configuration supplied using the namelist file.

### Namelist options

To use the namelist needs to be configured with the required options. These are listed below:

```
ln_tide        = .true.              !  =T : produce bdy tidal conditions
sn_tide_model  = 'FES2014'           !  Name of tidal model. Accepts FES2014, TPXO7p2, or TPXO9v5
clname(1)      = 'M2'                !  constituent name
clname(2)      = 'S2'
clname(3)      = 'K2'
clname(4)      = 'O1'
clname(5)      = 'P1'
clname(6)      = 'Q1'
clname(7)      = 'M4'
ln_trans       = .true.              !  interpolate transport rather than velocities
! location of TPXO7.2 data
sn_tide_grid_7p2   = './inputs/tpxo7.2/grid_tpxo7.2.nc'
sn_tide_h          = './inputs/tpxo7.2/h_tpxo7.2.nc'
sn_tide_u          = './inputs/tpxo7.2/u_tpxo7.2.nc'
! location of TPXO9v5 data: single constituents per file
sn_tide_grid_9p5   = './inputs/TPXO9_atlas_v5_nc/grid_tpxo9_atlas_30_v5.nc'
sn_tide_dir        = './inputs/TPXO9_atlas_v5_nc/'
! location of FES2014 data
sn_tide_fes        = './inputs/FES2014/'
```

These options define the location of the tidal model datasets, note this differs depending on model as TPXO has all harmonic constants in one netcdf file whereas FES has three separate netcdf files (one for amplitude two for currents) for each constant. Extra harmonics can be appended to the clname(n) list. FES supports 34 constants and TPXO7.2 has 13 to choose from. Other versions of TPXO should work with pyBDY but have not been yet been tested. NOTE FES dataset filenames must have be in the format of constituent then type. e.g.:

```
M2_Z.nc (for amplitude)
M2_U.nc (for U component of velocity)
M2_V.nc (for V component of velocity)
```

If this is not undertaken the pyBDY will not recognise the files. TPXO data files are specified directly so these can be anyname although it is best to stick with the default names as shown above. So far the tidal model datasets have been downloaded and used locally but could also be stored on a THREDDS server although this has not been tested with the global tide models.

Other options include “ln_tide” a boolean that when set to true will generate tidal boundaries. “sn_tide_model” is a string that defines the model to use, currently only “fes” or “tpxo” are supported. “ln_trans” is a boolean that when set to true will interpolate transport rather than velocities.

### Harmonic Output Checker

There is an harmonic output checker that can be utilised to check the output of pyBDY with a reference tide model. So far the only supported reference model is FES but TPXO will be added in the future. Any tidal output from pyBDY can be checked (e.g. FES and TPXO). While using the same model used as input to check output doesn’t improve accuracy, it does confirm that the output is within acceptable/expected limits of the nearest model reference point.

There are differences as pyBDY interpolates the harmonics and the tidal checker does not, so there can be some difference in the values particularly close to coastlines.

The checker can be enabled by editing the following in the relevent bdy file:

```
ln_tide_checker = .true.                ! run tide checker on pyBDY tide output
sn_ref_model    = 'fes'                 ! which model to check output against (FES only)
```

The boolean determines if to run the checker or not, this takes place after creating the interpolated harmonics and writing them to disk. The string denotes which tide model to use as reference, so far only FES is supported. The string denoting model is not strictly needed, by default fes is used.

The checker will output information regarding the checking to the NRCT log, and also write an spreadsheet to the output folder containing any exceedance values, the closest reference model value and their locations. Amplitude and phase are checked independently, so both have latitude and longitude associated with them. It is also useful to know the amplitude of a exceeded phase to see how much impact it will have so this is also written to the spreadsheet. An example output is shown below, as can be seen the majority of the amplitudes, both the two amplitudes exceedances and the ones associated with the phase exceedances are low (~0.01), so can most likely be ignored. There a few phase exceedances that have higher amplitudes (~0.2) which would potentially require further investigation. A common reason for such an exceedance is due to coastlines and the relevant point being further away from an FES data point.

The actual thresholds for both amplitude and phase are based on the amplitude of the output or reference, this is due to different tolerances based on the amplitude. e.g. high amplitudes should have lower percentage differences to the FES reference, than lower ones simply due to the absolute amount of the ampltiude itself, e.g. a 0.1 m difference for a 1.0 m amplitude is acceptable but not for a 0.01 m amplitude. The smaller amplitudes contribute less to the overall tide height so larger percentage differences are acceptable. The same also applies to phases, where large amplitude phases have little room for differences but at lower amplitudes this is less critical so a higher threshold is tolerated.

The following power functions are used to determine what threshold to apply based on the reference model amplitude.

#### Amplitude Threshold

```
Percentage Exceedance = 26.933 * Reference Amplitude ^ -0.396’
```

#### Phases Threshold

```
Phase Exceedance = 5.052 * pyBDY Amplitude ^ -0.60
```

## Troubleshooting :safety_vest:

[Back to top](#pybdy-documentation)

Always check the pyBDY log file. This is usually saved in the working directory of pyBDY as nrct.log. It gives helpful information which may help to diagnose issues. E.g. ValueErrors that are result of a THREDDS server being down and unable to provide data files.

If you get the error message "Destination touches source i-edge but source is not cylindrical" or you get the error message "Destination touches source j-edge but North Fold is not implemented". There is a plot you can uncomment in pybdy.nemo_bdy_chunk.chunk_bdy() that will show you where pyBDY is attempting to place bdy points.

- For "Destination touches source i-edge but source is not cylindrical", you may have an open boundary in your mask or bathymetry file that is not inside the domain of the source data. If this is the case you need to edit your mask to be land (i.e. zeros) to block the incorrect open boundary.
- For "Destination touches source j-edge but North Fold is not implemented", your domain probably touches the Arctic North Fold and pyBDY is trying to put an open boundary there. If this is the case you need to edit your mask to be land (i.e. zeros) to block the incorrect open boundary along the north edge of the domain. Do not attept to have a regional model with a boundary crossing the North Fold, this has not be implemented yet.

If you have time interpolation problems read the section [Time Settings](#time-settings).

## pyBDY Module Structure :scroll:

[Back to top](#pybdy-documentation)

Here is a list of all the classes, methods and functions in pyBDY.
