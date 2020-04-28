CMEMS downloader usage
=======================

**IMPORTANT** The CMEMS downloader has only been tested with the GLOBAL_ANALYSIS_FORECAST_PHY_001_024 model and specifcally
the hourly SSH and U V product. This also has temperature stored within it, but not salinity. Other models and products should work but are
currently likely to need some changes to the code to cope with different variable names within the data. This will be fixed
in a later release of PyNEMO that is able to handle different variable and tracer names.

PyNEMO has a CMEMS downloading function incorporated within it, this will download a section of the CMEMS global model (more models to be added)
'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS' for the defined time period in the namelist file

To use the downloading function, the following command is used::

    $ pynemo -d namelist.bdy

Where the -d flag tells PyNEMO to use the CMEMS downloader and download data as specified in the namelist file. The log file
that PyNEMO produces provides a log of what the downloader does. The CMEMS MOTU system is prone to disconnects and failure
so there is download retry and error handling built in. Most of the options required should not need editing and are there for
future use in case URL's and filenames on CMEMS change.

The options that can be configured are described in further detail below::

    !------------------------------------------------------------------------------
    !  I/O
    !------------------------------------------------------------------------------
       sn_src_dir = '/Users/thopri/Projects/PyNEMO/inputs/CMEMS.ncml' ! src_files/'
       sn_dst_dir = '/Users/thopri/Projects/PyNEMO/outputs'

       sn_fn      = 'NNA_R12'             ! prefix for output files
       nn_fv      = -1e20                 !  set fill value for output files
       nn_src_time_adj = 0                ! src time adjustment
       sn_dst_metainfo = 'CMEMS example'

    !------------------------------------------------------------------------------
    !  CMEMS Data Source Configuration
    !------------------------------------------------------------------------------
       ln_use_cmems             = .true.
       ln_download_cmems        = .true.
       sn_cmems_dir             = '/Users/thopri/Projects/PyNEMO/inputs/' ! where to download CMEMS input files (static and variable)
       ln_download_static       = .true.
       ln_subset_static         = .true.
       nn_num_retry             = 4 ! how many times to retry CMEMS download after non critical errors?
    !------------------------------------------------------------------------------
    !  CMEMS MOTU Configuration (for Boundary Data)
    !------------------------------------------------------------------------------
       sn_motu_server           = 'http://nrt.cmems-du.eu/motu-web/Motu'
       sn_cmems_config_template = '/Users/thopri/Projects/PyNEMO/pynemo/config/motu_config_template.ini'
       sn_cmems_config          = '/Users/thopri/Projects/PyNEMO/pynemo/config/motu_config.ini'
       sn_cmems_model           = 'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS'
       sn_cmems_product         = 'global-analysis-forecast-phy-001-024'
       sn_dl_prefix             = 'subset'
    !------------------------------------------------------------------------------
    !  CMEMS FTP Configuration (for Static Files)
    !------------------------------------------------------------------------------
        sn_ftp_server            = 'nrt.cmems-du.eu'
        sn_static_dir            = '/Core/GLOBAL_ANALYSIS_FORECAST_PHY_001_024/global-analysis-forecast-phy-001-024-statics'
        sn_static_filenames      = 'GLO-MFC_001_024_coordinates.nc GLO-MFC_001_024_mask_bathy.nc GLO-MFC_001_024_mdt.nc'
        sn_cdo_loc               = '/opt/local/bin/cdo' ! location of cdo executable can be found by running "where cdo"
    !------------------------------------------------------------------------------
    !  CMEMS Extent Configuration
    !------------------------------------------------------------------------------
        nn_latitude_min          = 40
        nn_latitude_max          = 66
        nn_longitude_min         = -22
        nn_longitude_max         = 16
        nn_depth_min             = 0.493
        nn_depth_max             = 5727.918000000001

Some of the options define the behaviour of the downloader, others define locations to save files and others detail models
and grid files to download. Finally the spatial extent to download is also required.

I/O and NCML file
-------------------------

The location of the NCML file is listed a string defining the source directory or "sn_src_dir". The output folder is also
defined here as "sn_dst_dir", **NOTE** if this directory does not exist it will need to be created and permissoned correctly
for PyNEMO to run properly. The NCML file details the input files to agregate and what the variable names are. This file
can be generated using the ncml_generator, with variable names found using the CMEMS catalogue. https://resources.marine.copernicus.eu/?option=com_csw&task=results
For more information please read the ncml generator page. The example CMEMS.ncml file includes: temperature, SSH and U and V components of ocean currents.

Firstly, the string "sn_fn" defines the prefix for the output files. The number "nn_fv" defines the fill value, and the number
"nn_src_time_adj" defines the source time adjustment. The rest of the boxes are CMEMS specific.

Data Source Configuration
--------------------------

The first section defines the CMESM data source configuration. The boolean "ln_use_cmems" when set to true will use the
CMEMS downloader function to download the requested data, this is defined in the ncml file which can be generated using the
NCML generator. Among other things this file defines what data variables to download. This term also changes the variable
names to CMEMS specific ones e.g. thetao for temperature and so for salinity. This is in contrast to the NEMO specific ones
such as Votemper and Vosaline. When set to false no download occurs and variable names are kept to NEMO specific.

MOTU Configuration
-------------------

In the next section when set to true "ln_download_cmems" will download the boundary tracer data, e.g. time series of temperature and saliniy.
When set to false PyNEMO will skip this download. The string "sn_cmems_dir" defines where to save these downloaded files.
PyNEMO requires grid data, this isn't possible to download using the same method as the tracer data which uses the MOTU
python client. To get the grid data, an ftp request is made to download the global grids which are then subset to the relevent
size. The booleans "ln_downlad_static" and "ln_subset_static" determine this behavior. Finally there is an int named
"nn_num_retry" this defines the number of times to retry downloading the CMEMS data. The data connections are prone to failure
so if a non critical error occurs the function will automatically try to redownload. This int defines how many times it will
try to do this. Typically this static data and subsetting are only required once so these can be set to true for first download
and then set to false when more time series data is required.

As mentioned previously, the time series boundary data is downloaded using MOTU, this is an efficent and robust web server that
handles, extracts and transforms oceanographic data. By populating a configuration file, this can be sent to the MOTU server
which will return the requested data in the requested format. The section CMEMS MOTU configuration sets this up. Most of these
options should not need changing. The location of the MOTU server for CMEMS is defined here, and the location of the config
template file and also the location of the config file to submit. The only options that should require changing are the model,
product and prefix options. These define which CMEMS model and product to download and the prefix is a user defined string to prefix
the downloads. A catalogue of the CMEMS model and products can be found at https://resources.marine.copernicus.eu/?option=com_csw&task=results
Currently PyNEMO has only been tested using the physical global forecast model although the downloader should be able to download
other models and products, it has not been tested and their are known issues with other products that restrict seamless download.
e.g. the NorthWest Atlantic model is not currently compatable due to differences in how the model variables are stored.

FTP Configuration for Static and Grid files
--------------------------------------------

The next section CMEMS FTP configuration, defines which FTP server, remote directory and files to download. This should require
modification unless CMEMS changes the file structure or names. Note it is important that the filenames are separated by a space
as this is what PyNEMO is expecting. Finally the location of CDO executable which should be installed to enable subsetting to occur.
This can be found by running::

    $ where cdo


Extent configuration
---------------------

Finally the last box, this is where the extent to download is configured, it is up to the user to decide but it is suggested this
is at least 1 degree wider than the destination or child configuration. The depth range to request is also defined here. This information can
be extracted from the CMEMS catalogue. Once set for a given configuration this will not need to be edited.



