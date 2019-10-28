# PyNEMO
 
To be udated soon. This work springboards from the [PyNEMO](http://pynemo.readthedocs.io/en/latest/index.html) Project.

## What is this repository for? ##

## How do I get set up? ##

## Contribution guidelines ##

## Bench Marking Tests ##

The PyNEMO module can be tested using the bench marking namelist bdy file in the inputs folder. To check the outputs of the benchmark test, these can be visualised using the plotting script within the test_scripts folder. The following steps are required,

- Run PyNEMO using the namelist file in the inputs folder (namelist_remote.bdy) e.g.

	-	$ pynemo -s /path/to/namelist/file

- This will create two output files coordinates.bdy.nc and NNA_R12_bdyT_y1979)m11.nc in an outputs folder

- To check the coordinates.bdy.nc has the correct boundary points, the script bdy_coords_plot.py will plot the domain boundaries and shown the different locations of the rim width (increasing number should go inwards) This script is located in the test_scripts folder.

- The result should look like this (if using the current benchmark data)

![Example BDY coords output](/screenshots/example_bdy_coords.png)

## Who do I talk to? ##

* Repo owner or admin

jdha

* Other community or team contact


For more information regarding the use and development of PyNEMO see: [PyNEMO Wiki](https://github.com/jdha/PyNEMO/wiki)
