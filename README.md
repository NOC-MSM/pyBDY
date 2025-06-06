# pyBDY

[pyBDY documentation](https://noc-msm.github.io/pyBDY/).

## How do I get set up?

These are the steps to take to install pyBDY:

- Clone pyBDY repository:

    ```
    export PYBDY_DIR=$PWD/pyBDY
    git clone https://github.com/NOC-MSM/pyBDY.git
    ```

- Creating a specific conda virtual environment is highly recommended ([click here for more about virtual
    enviroments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)).
    Use the latest version of anaconda (to be added in your .bashrc or load the module in the command line, e.g ` module load anaconda/5-2021`).

    ```
    cd $PYBDY_DIR
    conda env create -n pybdy -f environment.yml python=3.9
    ```

- Activate the new virtual environment:

    ```
    conda activate pybdy
    ```

- To deactivate (not now!):

    ```
    conda deactivate
    ```

- Make sure the Java Runtime Environment is set e.g.:

    ```
    export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.372.b07-1.el7_9.x86_64/ # e.g. for livljobs\*
    ```

    Or (downloading from https://jdk.java.net/20/)

    ```
    export JAVA_HOME=/Users/<username>/Downloads/jdk-20.0.1.jdk/Contents/Home/ # e.g. for mac OSX
    ```

    Generalised methods for defining paths are as follows:

    ```
    export JAVA_HOME=$(readlink -f $(which java)) # UNIX
    export JAVA_HOME=$(/usr/libexec/java_home)    # Mac

    ```

    NB the above may not land at the correct directory level, but should find
    the correct root. PyBDY expects this to be the directory level with `lib`
    in which might be e.g. 3 directories back.

- Install pyBDY:

    ```
    pip install -e .
    ```

This should result in pyBDY being installed in the virtual environment,
and can be checked by entering:

```
pybdy -v
```

Resulting in a help usage prompt:

```
usage: pybdy -g -s <namelist.bdy>
```

To use pyBDY, the following command is entered: (the example will run
an benchmarking test):

```
pybdy -s /path/to/namelist/file (e.g. ./inputs/namelist_remote.bdy)
```

## Contribution guidelines

See [contribution guidelines](contribution_guidelines.md) for developers.

## Bench Marking Tests

The pyBDY module can be tested using the bench marking namelist bdy
file in the inputs folder. To check the outputs of the benchmark test,
these can be visualised using the plotting script within the
plotting folder. A local version of the benchmark data can be
downloaded from
[here](https://gws-access.jasmin.ac.uk/public/jmmp/benchmark/).

E.g.

```
cd $PYBDY_DIR/inputs/benchmark/
wget -r -np -nH --cut-dirs=3 -erobots=off --reject="index.html*" http://gws-access.jasmin.ac.uk/public/jmmp/benchmark/
```

The
./benchmark directory should reside as a subfolder of ./inputs. The
following steps are required,

- Run pyBDY using the namelist file in the inputs folder
    (namelist_local.bdy) from inside the root pyBDY directory, e.g.:

    ```
    cd $PYBDY_DIR
    mkdir -p outputs
    pybdy -s inputs/namelist_local.bdy
    ```

- This will create two output files `coordinates.bdy.nc` and
    `NNA_R12_bdyT_y1979_m11.nc` in an `./outputs` folder

- To check the coordinates.bdy.nc has the correct boundary points, the
    script `plotting/plot_coords.py` will plot the domain boundaries and show
    the different locations of the rim width (increasing number should
    go inwards).

    E.g.
    `python plotting/plot_coords.py outputs/NNA_R12_bdyT_y1979m11.nc outputs/coordinates.bdy.nc`
    ![Example plot_coords.py output](/screenshots/example_coords.png)

    The other script `plot_bdy.py` plots extracted variables at the boundaries to help visualise the output (1D or 2D).
    E.g.
    `python plotting/plot_bdy.py outputs/NNA_R12_bdyT_y1979m11.nc votemper`
    ![Example plot_bdy.py output](/screenshots/example_bdy_data.png)

    which also works on 2D tidal boundary data (note you can specify an output file name):
    `python plotting/plot_bdy.py outputs/NNA_R12_bdytide_TPXO7p2_M2_grd_Z.nc z1 example_bdy_1d_data.png`
    ![Example plot_bdy.py output for tides](/screenshots/example_bdy_1d_data.png)

## Example: generating tidal boundary conditions on ARCHER2

- Activate the new virtual environment:

    ```
    conda activate pybdy
    ```

- Make sure all the directories and files are in place:

    ```
    cd pyBDY
    mkdir outputs
    ln -s /work/n01/n01/shared/jelt/FES2014 inputs/.
    <cp benchmark dir into inputs/benchmark>
    ```

- Press go:

    ```
    pybdy -s inputs/namelist_local.bdy
    ```

Take about 120s. Generates 7 consitutents, using FES2014 data, written
to \`outputs\`:

```
coordinates.bdy.nc
NNA_R12_bdytide_FES2014_M4_grd_V.nc
NNA_R12_bdytide_FES2014_Q1_grd_U.nc
NNA_R12_bdytide_FES2014_K2_grd_U.nc
NNA_R12_bdytide_FES2014_M4_grd_Z.nc
NNA_R12_bdytide_FES2014_Q1_grd_V.nc
NNA_R12_bdytide_FES2014_K2_grd_V.nc
...
```
