Installation
============
This page provides a guide to installing pyNEMO. 

Dependencies
^^^^^^^^^^^^
anaconda:
  - basemap=1.2.0
  - netcdf4=1.5.3
  - pyqt=5.9.2
  - scipy=1.2.1
  - python=3.7.6
  - pip=20.0.2
  - pandas=1.0.1
  - pytest=5.3.5
  - xarray=0.15.0

pip:
    - idna==2.9
    - lxml==4.5.0
    - pyjnius==1.2.1
    - seawater==3.3.4
    - thredds-crawler==1.5.4
    - motuclient==1.8.4
    - sphinx==3.0.2
    - sphinx-rtd-theme==0.4.3

How do I install PyNEMO?
------------------------

Steps to take to install PyNEMO, creating a specific conda virtual environment is highly recommended.
`click here for more about virtual enviroments <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html/>`_

- Install Git (outside scope of this guide)
- Clone PyNEMO repository::

    $ git clone https://github.com/NOC-MSM/PyNEMO.git

- Install Conda, either Anaconda or Miniconda (outside scope of this guide)
- Create conda environment for PyNEMO::

    $ cd PyNEMO
    $ conda env create -f pynemo_37.yml

- Activate the new virtual environment::

   $ source activate pynemo3

- Install Jave JDK (outside scope of this guide) and link Java Home to conda environment::

    $ export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-13.0.2.jdk/Contents/Home # see notes below

**NOTE** this link has to be set everytime the enviornment is activated. It can be automated using the .bashrc file or by
setting environment hooks in the conda activate and deactivate files.

- Install PyNEMO::

    $ cd /location/of/pynemo/repo
    $ python setup.py build
    $ python setup.py install

This should result in PyNEMO being installed in the virtual environment, and can be checked by entering::

    $ pynemo -h

Resulting in a help usage prompt::

    $ usage: pynemo [-g] -s -d <namelist.bdy>
       -g (optional) will open settings editor before extracting the data
       -s <bdy filename> file to use
       -d (optional) will download CMEMS data using provided bdy file

The virtual environment can be deactivated to return you to the normal prompt by typing::

    $ conda deactivate

To reactivate, the following needs to be typed::

    $ source activate pynemo3


Jave Home Environment path
--------------------------

The above path for Java Home was valid for a Macbook Pro 2015 with macOS Catalina and Java SDK 13.0.2
however for different java versions, operating systems etc this may be different

The conda environment yaml file has been tested with miniconda 3.7 and found to install the environment correctly.

Bench Marking Tests
-------------------

The PyNEMO module can be tested using the bench marking namelist bdy file in the inputs folder. To check the outputs of the benchmark test, these can be visualised using the plotting script within the test_scripts folder. The following steps are required,

- Run PyNEMO using the namelist file in the inputs folder (namelist_remote.bdy) e.g.::

    $ pynemo -s /path/to/namelist/file

- This will create two output files coordinates.bdy.nc and NNA_R12_bdyT_y1979)m11.nc in an outputs folder

- To check the coordinates.bdy.nc has the correct boundary points, the script bdy_coords_plot.py will plot the domain boundaries and shown the different locations of the rim width (increasing number should go inwards) This script is located in the test_scripts folder.

- The result should look like this (if using the current benchmark data)

.. image:: /_static/example_bdy_coords.png
  :width: 800
  :alt: Example BDY coords output

Unit Tests
-----------

To test operation of the PyNEMO module, running the PyTest script in the unit tests folder will perform a range of tests on different child grids,
e.g. checking the interpolation of the source data on to the child grid. To do this the following command is required::

    $ pytest -v pynemo/pynemo_unit_test.py

The results of the test will show if all tests pass or the errors that result from failed tests.

Currently **(26/03/2020)** there are 7 tests that cover checking the interpolation results of different child grids. The input data is generated as part of the
test and is removed afterwards. The number of tests will be increased in the future to cover more PyNEMO functionality.

For more information regarding the use and development of PyNEMO see: [PyNEMO Wiki](https://github.com/jdha/PyNEMO/wiki)


