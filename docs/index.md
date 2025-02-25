# Getting Started

**Welcome to the documentation for NEMO lateral boundary conditions (pyBDY)**

## Introduction

pyBDY is a python package to generate lateral boundary conditions for regional NEMO model configurations.
It has been developed to uses geographical and depth information from an a source data (e.g. a global ocean
simulation) and translate them to a destination NEMO region simulation. It makes use of a kdtree approximate
nearest neighbour algorithm in order to provide a generic method of interpolation for any flavour of ocean
model. The available options are accessed either through a NEMO style namelist or a convient GUI.

---

## Dependecies :globe_with_meridians:

pyBDY is insatlled under a conda/mamba environment to aid wider distribution and to facilitate development.
The key dependecies are listed below:

- netCDF4
- scipy
- numpy
- matplotlib
- cartopy
- thredds_crawler
- seawater
- pyqt5
- pyjnius
- cftime

A recent JAVA installation is also required.

---

## Quick Start :rocket:

### Installation

To get started, check out and set up an instance of the pyBDY GitHub [repository](https://github.com/NOC-MSM/pyBDY):

```sh
export PYBDY_DIR=$PWD/pyBDY
git clone git@github.com:NOC-MSM/pyBDY.git
```

??? tip "Helpful Tip..."

    - **It is not advised to checkout the respository in your home directory.**

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
