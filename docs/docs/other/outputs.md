# Outputs

!!! abstract "Summary"

    **This page provides information on the ocean & sea-ice outputs made available from the NAARC simulations their frequency & how to access them.**

---

## Primary Outputs
Primary outputs of the NAARC simulations are those variables which are calculated online at runtime and are written to netCDF files according to where they are defined on the eORCA grid.

!!! info "Example: NAARC T-Grid Variables"
    The conservative temperature ```thetao_con``` averaged at monthly intervals will be stored in the ```NAARC_1m_YYYYMM_grid_T.nc``` file. 

Below we include tables of the available ocean and sea-ice variables output by each NAARC simulation:

### List of Available Ocean & Sea-Ice Outputs

**In Progress:** We are currently working on improving access to the NAARC simulations by using [Intake](https://intake.readthedocs.io/en/latest/) to catalog the available datasets.

### Transport Diagnostics

Using diadct

---

## Secondary Outputs
Secondary outputs of the NAARC simulations include those diagnostics which are calculated offline using the primary output variables.

### AMOC 

The Atlantic Meridional Overturning Circulation (AMOC) is a fundamental component of the global climate system owing to its role in the redistribution of heat, nutrients and freshwater. On account of its wider societal significance, a number of continuous ocean observing systems have been deployed throughout the Atlantic Ocean to monitor the state and variability of the AMOC.

The [METRIC](https://github.com/oj-tooth/metric) Python package allows users to calculate meridional overturning and heat transport diagnostics in numerical models which are equivalent (and hence comparable) to existing observations at the RAPID (26.5$^{\circ}$N), MOVE (16$^{\circ}$N) and SAMBA (34.5$^{\circ}$S) (see [Danabasoglu et al., 2021](https://doi.org/10.1029/2021GL093045)).

Diagnostics including meridional overturning stream functions and the meridional fluxes of heat and freshwater will be made available as secondary output variables via the [JASMIN Object Store].


---

## Accessing NAARC Simulation Outputs.

JASMIN

```
---
title: NAARC Outputs available via JASMIN
config:
  layout: elk
  look: handDrawn
  theme: neutral
---
graph LR
  subgraph npd-eorca12-jra55v1 [eORCA12]
	  NAARC.T1m[T1m]
	  NAARC.U1m[U1m]
	  NAARC.V1m[V1m]
	 end

    A[noc-msm-o.s3-ext.jc.rl.ac.uk] --> B[npd-eorca1-jra55v1]
    B --> npd-eorca1-jra55v1
    A --> C[npd-eorca025-jra55v1]
    C --> npd-eorca025-jra55v1
    A --> D[npd-eorca12-jra55v1]
    D --> npd-eorca12-jra55v1
```

**In Progress:** We are currently working on improving access to the NAARC simulations by using [Intake](https://intake.readthedocs.io/en/latest/) to catalog the available datasets.
