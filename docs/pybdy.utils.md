# pybdy.utils package

## Submodules

# pybdy.utils.Constants module

File with all the constants that will be used.

> @author: Mr. Srikanth Nagella<br>

# pybdy.utils.e3_to_depth module

Function e3_to_depth.

> Purpose : compute t- & w-depths of model levels from e3t & e3w scale factors<br>
> Method : The t- & w-depth are given by the summation of e3w & e3t, resp.<br>
> Action : pe3t, pe3w : scale factor of t- and w-point (m)<br>
> Useage: [gdept, gdepw] = e3_to_depth(e3t, e3w, nz).<br>

## pybdy.utils.e3_to_depth.e3_to_depth(pe3t, pe3w, jpk)

# pybdy.utils.gcoms_break_depth module

Rewritting the break depth implementation from matlab version.

> @author: Mr. Srikanth Nagella<br>

## pybdy.utils.gcoms_break_depth.gcoms_boundary_masks(bathy, ov, lv)

\_Summary.

### Parameters

> - **type bathy:**<br>
> - **param bathy:**<br>
>     This is the input bathymetry data
> - **type ov:**<br>
> - **param ov:**<br>
>     Latittude array
> - **type lv:**<br>
> - **param lv:**<br>
>     Longitude array
> - **type bathy:**<br>
>     numpy array
> - **type ov:**<br>
>     numpy array
> - **type lv:**<br>
>     numpy array
> - **return:**<br>
>     returns the ob, lb
> - **rtype:**<br>
>     numpy arrays
> - **Example:**<br>

## pybdy.utils.gcoms_break_depth.gcoms_break_depth(bathy)

Create a mask for the break depth using histograms.

## pybdy.utils.gcoms_break_depth.polcoms_select_domain(bathy, lat, lon, roi, dr)

Calculate the shelf break.

- **Parameters**
    - **bathy** (*numpy array*) – This is the input bathymetry data
    - **lat** (*numpy array*) – Latittude array
    - **lon** (*numpy array*) – Longitude array
    - **roi** (*python array*) – region of interest array [4]
    - **dr** (*float*) – shelf break distance
- **Returns**
    returns the depth_shelf, h_max

> - **Return type:**<br>
>     numpy arrays.
> - **Example:**<br>

# pybdy.utils.nemo_bdy_lib module

Library of some functions used by multiple classes.

Written by John Kazimierz Farey, Sep 2012.

## pybdy.utils.nemo_bdy_lib.bdy_sections(nbidta, nbjdta, nbrdta, rw)

Extract individual byd sections.

## pybdy.utils.nemo_bdy_lib.bdy_transport()

Calculate transport across individual bdy sections.

## pybdy.utils.nemo_bdy_lib.dist(self, x, y)

Return the distance between two points.

## pybdy.utils.nemo_bdy_lib.dist_point_to_segment(p, s0, s1)

Get the distance of a point to a segment.

## Notes

*p*, *s0*, *s1* are *xy* sequences
This algorithm from

> [http://geomalgorithms.com/a02-\_lines.html](http://geomalgorithms.com/a02-_lines.html).<br>

## pybdy.utils.nemo_bdy_lib.get_output_filename(setup_var, year, month, var_type)

Return a output filename constructed for a given var_type, year and month.

## pybdy.utils.nemo_bdy_lib.get_output_tidal_filename(setup_var, const_name, grid_type)

Return a output filename constructed for a given tidal constituent and grid type.

## pybdy.utils.nemo_bdy_lib.psi_field(U, V)

## pybdy.utils.nemo_bdy_lib.rot_rep(pxin, pyin, dummy, cd_todo, gcos, gsin)

Rotate function.

## pybdy.utils.nemo_bdy_lib.sub2ind(shap, subx, suby)

Subscript to index of a 1d array.

## pybdy.utils.nemo_bdy_lib.velocity_field(psi)

## Module contents
