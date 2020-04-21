Usage
=====
There are four tools available in pyNEMO. These are "boundary file generation" where boundary data files are generated from a
parent grid along the boundary of a child grid. Boundary data can comprise of tracers such as temperature and salinity. Or
tidal data from global tide models. Sea surface height and ocean currents are also supported. PyNEMO now has an integrated
CMEMS repository downloaded. Invoking this option will download data of interest for a region of interest. PyNEMO uses NCML
files to define variable names and data location. this allows multiple netcdf input files to appear as one. This commonmly used
on THREDDS servers but is also used locally for CMEMS boundary data input. The GUI allows this NCML files to be generated.
Finally there is a settings editor that allows you to edit the pynemo configuration file (BDY file)

Boundary file generation
------------------------
This command line tool reads a BDY file, extracts boundary data and prepares the data for a NEMO simulation. The bdy file
is a plain text file containing key value pairs. Please look at the sample namelists in the github repository. They are
stored in the inputs directory. There are three different examples, they all use the same child grid but ultilise different
data sources. One uses local data, the other uses data hosted on a THREDDS server. The last one is configured to download
CMEMS data first and then run using the downloaded data. The namelist file shares common syntax with the NEMO simulation namelist input file.

.. note:: Directory paths in bdy file can be relative or absolute.
          The application picks the relative path from the current working
          directory.

Syntax for pynemo command is

::

   > pynemo [-g] -s <bdy file>

For help

::

   > pynemo -h
   > usage: pynemo [-g] -s -d <namelist.bdy>
   >        -g (optional) will open settings editor before extracting the data
   >        -s <bdy filename> namelist file to use to generate boundary data
   >        -d <bdy filename> namelist file to use to download CMEMS data

Example comamnd

::

   > pynemo -g -s namelist.bdy

CMEMS data download
-------------------
To download CMEMS data, the flag -d needs to be specified when running pynemo. This will use the specified namelist file and
download the relevent CMEMS data. Once successful the same namelist file can be used to generate the boundary conditions by
running PyNEMO with the -s flag. Example command.::

    $ pynemo -d /PyNEMO/inputs/namelist_cmems.bdy

To use the CMEMS download service an account needs to be created at http://marine.copernicus.eu/services-portfolio/access-to-products/
Once created the user name and password need to be added to PyNEMO. To do this a file with the name CMEMS_cred.py in the utils folder
needs to be created with two defined strings one called user and the other called pwd to define the user name and password.::

    $ touch pynemo/utils/CMEMS_cred.py
    $ vim pynemo/utils/CMEMS_cred.py
    press i
    user='username goes here'
    pwd='password goes here'
    press esc and then :wq

**IMPORTANT** This will create a py file in the right place with the parameters required to download CMEMS, the password is stored as plain text so please
do not reuse any existing password you use!

The CMEMS download usage page has more information about how to configure the namelist file.

GUI NCML Generator
------------------
This GUI tool facilitates the creation of a virtual dataset for input into PyNEMO. The virtual dataset is defined using NetCDF Markup Language (NcML ).

Using NcML, it is possible to:

- modify metadata
- modify and restructure variables
- combine or aggregate data from multiple datasets. The datasets may reside in the local file system or in a remote OPeNDAP (http://www.opendap.org/) server.

Please see NcML generator usage page for more information in using the GUI.

pynemo settings editor
----------------------

This tool will open a window where you can edit the mask and change the values of bdy parameters.

Syntax for pynemo_settings_editor command is

::

   > pynemo_settings_editor [-s <bdy filename>]

.. note:: If no file name is specified then a file dialog box will open to select a file.

For help

::

   > pynemo_settings_editor -h
   > usage: pynemo_settings_editor -s <namelist.bdy>

Example:

::

   pynemo_settings_editor -s namelist.bdy
