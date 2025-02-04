# Model Configuration

!!! abstract "Summary"

```
**This page provide additional details on the parameter choices, initial/surface/boundary conditions and output options of the base NAARC simulation.**
```

______________________________________________________________________

## Overview :globe_with_meridians:

The NAARC integrations have been performed using the NEMO ocean sea-ice model configurations at 1/12$^{\\circ}$ nominal horizontal resolution.

They are based on the recent UK Global Ocean and Sea Ice configuration version 9 (GOSI9), which has been documented comprehensively in [Guiavarc’h et al. (in review)](https://doi.org/10.5194/egusphere-2024-805).

In this section, we describe the configuration in detail and provide references for those seeking further technical information.

### Ocean Model

The NAARC configuration has been developed using the Nucleus for European Modelling of the Ocean ([NEMO](https://www.nemo-ocean.eu)) modelling framework version 4.2.2. There have been several modifications to the code
base, which are listed under \[Modifications\]: #Modifications. Although we are wedded to NEMO 4.2.2 for the CANARI project the repository is also configured to setup NAARC at 4.2.3 and 4.2_HEAD.

For a list of the additions made to the version 4.2 release, users are referred to the NEMO [release notes](https://sites.nemo-ocean.io/user-guide/changes.html#changes-since-4-0-7).

#### Model Grid & Bathymetry

The ocean model horizontal grid and bathymetry used for the NAARC simulations are the same as documented in [Storkey et al (2018)](https://doi.org/10.5194/gmd-11-3187-2018).

The NAARC configuration is based on the eORCA12 grid and has a horizontal resolution of 1/12$^{\\circ}$. A mask is applied to the eORCA12 grid at run-time providing an *active* domain north of 20$^{\\circ}$S
in the Atlantic and Arctic, through to 67^{\\circ}$N in the Pacific. The vertical coordinates are defined over 75 levels using a mix of Multi-Enevelope s-coordinates [Bruciaferri et al (2018)](https://link.springer.com/article/10.1007/s10236-018-1189-x)
in the shelf regions (see \[MEs\]: #MEs for further details), and z$^{\*}$ coordinates, [Adcroft and Campin, 2004](https://doi.org/10.1016/j.ocemod.2003.09.003) with partial step topography (e.g., [Barnier et al., 2006](https://doi.org/10.1007/s10236-006-0082-1))
in the remaining open ocean.

#### Mixing

- **Momentum Advection:** Vector-invariant form separating horizontal advection into a rotational term (scheme of [Arakawa & Lamb, 1981](<https://doi.org/10.1175/1520-0493(1981)109%3C0018:APEAEC%3E2.0.CO;2>)) and irrotational term (scheme of [Hollingsworth et al., 1983](https://doi.org/10.1002/qj.49710946012)).

- **Tracer Advection:** 4th Order Total Variance Diminishing (TVD) scheme ([Zalesak, 1979](<https://doi.org/10.1016/0021-9991(79)90051-2>)) in both horizontal and vertical directions.

- **Lateral Diffusion of Momentum:** Performed along iso-level surfaces with the following parameters:

  ```
    * Bi-Laplacian viscosity with a lateral viscous velocity = 0.1895 m s$^{-1}$
  ```

- **Lateral Diffusion of Tracers:** Performed using a triad rotated lapalcian operator on iso-neutral surfaces ([Griffies et al, 1998](https://journals.ametsoc.org/view/journals/phoc/28/5/1520-0485_1998_028_0805_idiazc_2.0.co_2.xml)) :

  ```
    * Lateral diffusive velocity = 0.027 m s$^{-1}$.
    * Using all four triads
    * Pure horizontal mixing in the mixed layer
    * Lateral mixing on bottom
  ```

- **Vertical Mixing of Momentum & Tracers:** Performed using turbulent closure Generic Length Scale (GLS) scheme based on prognostic equations for the turbulent kinetic energy and another for the generic length scale (see [Reffray et al., 2015](https://gmd.copernicus.org/articles/8/69/2015/) and references therein).

#### Tides

- **Forcing**

- **Boundary**

#### Equation of State

The NAARC simulations use the Thermodynamic Equation Of Seawater 2010 (TEOS-10, [Ioc et al., 2010](https://unesdoc.unesco.org/ark:/48223/pf0000188170)) and hence absolute salinity and conservative temperature variables are output rather than practical salinity and potential temperature as in EOS-80.

#### Atmospheric Forcing

The base NAARC simluations are forced over the period 1979-2023 by the JRA55-do atmospheric reanalysis ([Tsujino et al, 2018](https://doi.org/10.1016/j.ocemod.2018.07.002)) using the NCAR bulk formulae ([Large and Yeager, 2009](https://doi.org/10.1007/s00382-008-0441-3)).
River inflow is also derived from the JRA55-do dataset with time-varying input over the top 10m.

!!! info "Accounting for Current Feedback to the Atmosphere"

```
Since global atmospheric reanalyses already take into account the coupling between ocean currents and surface wind wind stress (termed the Current Feedback), directly forcing an ocean model with reanalysis (relative) winds results in unrealistically weak mesoscale activity and large-scale circulation features (see [Renault et al., 2020](https://doi.org/10.1029/2019MS001715)).

To overcome this, the parameterisation of [Renault et al., 2017](https://doi.org/10.1038/s41598-017-17939-1) is used to remove the wind and surface stress anomalies induced by the reanalysis surface ocean currents and replace them with those induced by the currents of the Near-Present-Day simulation. This relies on a linear estimate for the current-stress coupling coefficient, $S_{\tau} = \alpha |U_{10_{abs}}| + \beta$, where $\alpha$ = -2.9x10$^{-3}$ N s$^{2}$ m$^{-4}$ and $\beta$ = 0.008 N s m$^{-3}$.
```

#### Initial Conditions

To initialise the NAARC integrations, conservative temperature, absolute salinity and ice fields from the [eORCA025 NOC-Near-Present-Day](https://noc-msm.github.io/NOC_Near_Present_Day) (1979) simulations are used.

#### Sea Surface Salinity Restoration

None at present

### Sea Ice Model

The Near-Present-Day simulations use NEMO's recently introduced dynamic-thermodynamic continuum sea ice model, SI$^{3}$ (Sea Ice modelling Integrated Initiative) (see [Vancoppenolle et al., 2023](https://doi.org/10.5281/zenodo.7534900)).

For a more detailed discussion on the SI$^{3}$ model configuration, users are referred to [Blockley et al. (2023)](<>) and [Guiavarc’h et al., in review](https://doi.org/10.5194/egusphere-2024-805).

______________________________________________________________________

## Creating Initial Conditions :thermometer:

!!! info "Section Currently Under Development: Come Back Soon!"

```
**This section will include a description on how to create initial conditions for Near-Present-Day integrations.**
```

______________________________________________________________________

## Editing the Runscript :hammer:

To run your own Near-Present-Day integrations, you'll likely need to make changes to the `run_nemo_???.slurm` runscript in the `/nemo/cfgs/GLOBAL_QCO/eORCA??/` directory of your local installation of the NOC_Near_Present_Day repository.

In this section, we discuss the key parameters you will need to modify to begin running your own Near-Present-Day experiments.

Let's start by defining each of the parameters available in an example runscript `run_nemo_example.slurm`:

```sh title="run_nemo_example.slurm"
# ========================================================
# PARAMETERS TO SET
# time units used here for restart frequency and simulaion length
TIME_UNITS=0 # 0=years ; 1=days ; 2=hours
# Restart/resubmission frequency (in TIME_UNITS)
FREQRST=1
# job-step initial time step (0: infer from time.step)
# IT000 != 0 -> auto-resubmission is switched OFF
IT000=0
#
# Simulation original starting time step (unchanged for LENGTHxTIME_UNITS)
ITBEGIN=1
# Simulation length (in TIME_UNITS)
LENGTH=3
# Name of this script (to resubmit)
SCRIPTNAME=run_nemo_example.slurm
# If conducting the repeat and reset T and S spinup set SPIN to 1, else set to 0
SPIN=0
```

- **TIME_UNITS** is used to define the length of the simulation and to specify the resubmission frequency of the runscript. In the above example, `TIME_UNITS=0` indicates we are working in years.

- **FREQRST** defines the frequency (in the time units defined above) at which the runscript will be resubmitted as a SLURM batch job. In the above example, `FREQRST=1` indicates that every simulation year should be submitted as a separate SLURM batch job (dependent on the successful completion of the previous job/year).

- **IT000** specifies the initial time-step of this job. If `IT000=0` then the initial time-step will be determined from the time.step file in the run directory (if no time.step files exists then IT000 is set to 1). When IT000 != 0, runscript resubmission is turned off and its value will be unchanged.

- **ITBEGIN** specifies the starting time-step of the simulation. This is used to update the namelist_cfg file with the final time-step of the job when a restart file is to be written.

- **LENGTH** defines the length of the simulation (in the time units defined above). The simulation length together with the frequency of resubmission (FREQRST) will determine the number of SLURM batch jobs which are created. In the above example, `LENGTH=3` and `FREQRST=1` means that 3 separate SLURM batch jobs will be required to complete this simulation.

- **SCRIPTNAME** defines the name of the runscript to be resubmitted as a SLURM batch job. In most cases this should be the name of the runscript and should be checked carefully!

- **SPIN** specifies that a spin-up simulation should be perfomed. If `SPIN=1`, the simulation year will be restarted and the atmospheric forcing repeated, but the initial temperature and salinity fields will be defined from the restart file produced at the final time-step of the previous simulation year. Once a spin-up simulation is completed, define `SPIN=0` to continue the simulation with the next year of atmospheric forcing.

#### A Typical Use Case:

Let's consider a typical example: a user would like to perform a 25-year hindcast simulation (2000-2024) starting with a 5-year spin-up simulation repeating the year 2000. The user would also like each simulation year to be submitted as a separate SLURM batch job.

We can divide this workflow into two runscripts: (1) to perform the spin-up simulation from rest...

```sh title="run_nemo_example_spin-up.slurm"
# ========================================================
# PARAMETERS TO SET
# time units used here for restart frequency and simulaion length
TIME_UNITS=0 # 0=years ; 1=days ; 2=hours
# Restart/resubmission frequency (in TIME_UNITS)
FREQRST=1
# job-step initial time step (0: infer from time.step)
# IT000 != 0 -> auto-resubmission is switched OFF
IT000=0
#
# Simulation original starting time step (unchanged for LENGTHxTIME_UNITS)
ITBEGIN=1
# Simulation length (in TIME_UNITS)
LENGTH=5
# Name of this script (to resubmit)
SCRIPTNAME=run_nemo_example_spin-up.slurm
# If conducting the repeat and reset T and S spinup set SPIN to 1, else set to 0
SPIN=1
```

...and (2) to perform the 25-year hindcast simulation.

```sh title="run_nemo_example_hindcast.slurm"
# ========================================================
# PARAMETERS TO SET
# time units used here for restart frequency and simulaion length
TIME_UNITS=0 # 0=years ; 1=days ; 2=hours
# Restart/resubmission frequency (in TIME_UNITS)
FREQRST=1
# job-step initial time step (0: infer from time.step)
# IT000 != 0 -> auto-resubmission is switched OFF
IT000=0
#
# Simulation original starting time step (unchanged for LENGTHxTIME_UNITS)
ITBEGIN=1
# Simulation length (in TIME_UNITS)
LENGTH=30
# Name of this script (to resubmit)
SCRIPTNAME=run_nemo_example_hindcast.slurm
# If conducting the repeat and reset T and S spinup set SPIN to 1, else set to 0
SPIN=0
```

!!! note "Note on Modifying Parameters between Runscripts"

````
In the example above, we did not modify ```ITBEGIN``` in ```run_nemo_example_hindcast.slurm``` since using ```IT000=0``` means that this simulation will automatically start in 2001 following the final year of the 2000 spin-up simulation.

Also, note that ```LENGTH=30``` in ```run_nemo_example_hindcast.slurm``` defines the total simulation length in years, including the 5-year spin-up period and 25-year hindcast, rather than the number of additional years to simulate starting from 2001.
````

______________________________________________________________________

## Storing Output with a Zoom Domain :mag:

!!! info "Section Currently Under Development: Come Back Soon!"

```
**This section will include instructions on how to output variables for a sub-domain of the global eORCA grid.**
```
