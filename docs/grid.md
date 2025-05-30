# grid package

## Submodules

# grid.hgr module

> Created on Mon Feb 03 18:01:00 2025.<br>

@author James Harle
@author Benjamin Barton
@author Ryan Patmore

## *class* grid.hgr.H_Grid(hgr_file, name_map_file, logger, dst=1)

> Bases: `object`<br>

### \_\_init\_\_(hgr_file, name_map_file, logger, dst=1)

Master horizontal class.

### Parameters

> hgr_file (str) : string of file for loading hgr data<br>
> name_map_file (str) : string of file for mapping variable names<br>
> logger (object) : log error and messages<br>
> dst (bool) : flag for destination (true) or source (false)<br>

### Returns

> H_grid (object) : horizontal grid object<br>

### find_hgrid_type()

Find out what type of hoizontal grid is provided A, B or C.

### get_vars(vars_want)

Get the glam, gphi and e scale factors from file if possible.

### Parameters

> vars_want (list) : variables needed from file.<br>

## grid.hgr.calc_e1_e2(glam, gphi, ij)

Calculate missing scale factor e1 and e2 from glam or gphi.

### Parameters

> glam (np.array) : mesh variable glam (lon) [time, j, i]<br>
> gphi (np.array) : mesh variable gphi (lat) [time, j, i]<br>
> ij (int) : ij direction 1 (i or x direction) or 2 (j or y direction)<br>

### Returns

> e (np.array) : horizontal distance scale factor e<br>

## grid.hgr.calc_grid_from_t(t_mesh, mesh)

Calculate missing glam, gphi or gdep from t-grid.

### Parameters

> t_mesh (np.array) : mesh variable glam or gphi on t-grid<br>
> mesh (str) : grid mesh type (glam, gphi, or gdep of u, v, f)<br>

### Returns

> mesh_out (dict) : horizontal grid mesh data variable<br>

## grid.hgr.fill_hgrid_vars(grid_type, grid, missing)

Calculate the missing horizontal grid variables and add them to grid.

### Parameters

> grid_type (str) : type of horizontal grid (A, B or C)<br>
> grid (dict) : dictionary of grid data variable<br>
> missing (list) : list of missing variables to calculate<br>

### Returns

> grid (dict) : horizontal grid data dictionary<br>

# grid.zgr module

> Created on Mon Feb 03 18:01:00 2025.<br>

@author James Harle
@author Benjamin Barton
@author Ryan Patmore
@author Anthony Wise

## *class* grid.zgr.Z_Grid(zgr_file, name_map_file, hgr_type, e_dict, logger, dst=1)

> Bases: `object`<br>

### \_\_init\_\_(zgr_file, name_map_file, hgr_type, e_dict, logger, dst=1)

Master depth class.

### Parameters

> zgr_file (str) : string of file for loading zgr data<br>
> name_map_file (str) : string of file for mapping variable names<br>
> hgr_type (str) : horizontal grid type<br>
> e_dict (dict) : dictionary of e1 and e2 scale factors<br>
> logger (object) : log error and messages<br>
> dst (bool) : flag for destination (true) or source (false)<br>

### Returns

> Depth (object) : Depth object<br>

### find_zgrid_type()

Find out what type of vertical grid is provided zco, zps or sigma levels (sco).

### get_vars(vars_want)

Get the gdep and e3 scale factors from file if possible.

### Parameters

> vars_want (list) : variables needed from file.<br>

## grid.zgr.calc_gdepw(gdept)

Calculate missing gdepw from gdept.

### Parameters

> gdept (np.array) : mesh variable gdept on t-grid<br>

### Returns

> dep_out (np.array) : vertical grid mesh data variable<br>

## grid.zgr.fill_zgrid_vars(zgr_type, grid, hgr_type, e_dict, missing)

Calculate the missing vertical grid variables and add them to grid.

### Parameters

> zgr_type (str) : type of vertical grid (zco, zps or sco)<br>
> grid (dict) : dictionary of grid data variable<br>
> hgr_type (str) : horizontal grid type<br>
> e_dict (dict) : dictionary of e1 and e2 scale factors<br>
> missing (list) : list of missing variables to calculate<br>

### Returns

> grid (dict) : vertical grid data dictionary<br>

## grid.zgr.horiz_interp_e3_old(e_in, var_in, lev)

Horizontally interpolate the vertical scale factors e3u, e3v, e3f.

Use the horizontal scale factors to calculate interpolation factors.
To interpolate to get e3u or e3v, input var_in as e3t data but for e3f this
should be e3u.

### Parameters

> e_in (dict) : all horizontal scale factors e1 and e2 in dictionary<br>
> var_in (np.array) : e scale factor to interpolate from e3t (or e3u for f)<br>
> lev (str) : grid level type (e3 of u, v, f)<br>

### Returns

> e3 (np.array) : vertical distance scale factor e3 of lev<br>

## grid.zgr.horiz_interp_lev(t, w, zgr_type, hgr_type)

Horizontally interpolate the vertical scale factors e3 and gdep.

For A-Grids, u, v and f values are set to t and w values.
For C-Grids, zps or sco verticle coords are used to define u, v, and f.
For B-Grids, u and v values are set to f values following zps or sco.

### Parameters

> t (np.array) : vertical scale factors e or dep on t points<br>
> w (np.array) : vertical scale factors e or dep on w points<br>
> zgr_type (str) : type of vertical grid (zco, zps or sco)<br>
> hgr_type (str) : horizontal grid type (A, B or C)<br>

### Returns

> lev (dict) : vertical distance scale factor e or gdep<br>

## grid.zgr.vert_calc_e3(gdep_mid, gdep_top, lev)

Calculate missing vertical scale factors e3 from gdep.

### Parameters

> gdep_mid (np.array) : mesh variable on t levels<br>
> gdep_top (np.array) : mesh variable on w levels<br>
> lev (str) : grid level type (e3 of t, w, u, v)<br>

### Returns

> e3 (np.array) : vertical distance scale factor e3 of lev<br>

## Module contents

a Python based regional NEMO model configuration toolbox.
