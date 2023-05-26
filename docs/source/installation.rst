Installation
============
This page provides a guide to installing pyNEMO.

Dependencies
^^^^^^^^^^^^

1. Python 2.7 (Not tested with 3.x)
2. scipy
3. netCDF4-python
4. numpy
5. matplotlib
6. basemap
7. thredds_crawler
8. seawater
9. pyjnius (optional)

Anaconda
^^^^^^^^

Using conda: pyNEMO supports Win64, OSX and Linux. for other operating systems please build from source.

.. note:: It is recommended to create a seperate virtual environment for pyNEMO.
          Please follow the instructions on doing this at http://www.continuum.io/blog/conda

::

   conda install -c https://conda.anaconda.org/srikanthnagella pynemo

This will install pynemo and its dependencies. This build is generally outdated as development and
bug fixes to the source are a regular occurrence. It may be better to install from source until a beta
release is available.

From Source
^^^^^^^^^^^

Installing pyNEMO using other flavours of software or from source. Install all the dependencies and
download the source code from svn and install.

::

   svn checkout http://ccpforge.cse.rl.ac.uk/svn/pynemo/trunk/Python/
   python setup.py install

.. note:: If building from source in the Anaconda environment all dependencies can
          be installed using conda apart from thredds_crawler and pyjnius which can
          be installed using the following Anaconda channel:

::

   conda install -c https://conda.anaconda.org/srikanthnagella thredds_crawler
   conda install -c https://conda.anaconda.org/srikanthnagella pyjnius
