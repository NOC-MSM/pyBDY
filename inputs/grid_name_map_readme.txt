This readme is instructions for editing the file "grid_name_map.json".

The "grid_name_map.json" file provides a way to rename/remap the variables from
names in the file netcdf file to the variable names desired by pybdy. This is
specifically for the horizontal (hgr) and vertical (vgr) grid files (not data IO).
In the past this could be done with a .ncml file but now it done using .json.

The "grid_name_map.json" file has "dimension_map", "sc_variable_map" and
"dst_variable_map", these should not be edited. "sc" refers to the source grid
and "dst" refers to the destination grid. The list of dimensions t, z, y, x
under "dimension_map" are "key: value" pairs, where the "key" should be unedited
and the "value" should be changed to match the name of the respective dimension
in your netcdf file. The is the same process for the list of variables under
"variable_map". The "variable_map" is used for both horizontal and vertical
grid variable names even if they come from separate files.

Below is a decription of each dimension and variable. Not all variables are needed,
those that are marked with a * below are optional, if you don't have the optional
variable in your netcdf file leave it as the default "value" and pybdy will do its
best to calculate it. If the variable is available it should be name mapped
otherwise pybdy may incorrectly interpret the grid type for example. Variables
marked ** may be optional depending on what other variables are provided.
In all cases "t" should be size 1. Pybdy does not deal with time varying grids.

"dimension_map"

"t" = time dimension (size 1)
"z" = depth dimension
"y" = horizontal dimension often aligned with latitude
"x" = horizontal dimension often aligned with longitude

"sc_variable_map" and "dst_variable_map"

"nav_lon" = ** Longitude on t-grid (dims [y, x])
            (only needed if glamt is not present in the file)
"nav_lat" = ** Latitude on t-grid (dims [y, x])
            (only needed if gphit is not present in the file)
"glamt" = Longitude on t-grid (dims [t, y, x])
"gphit" = Latitude on t-grid (dims [t, y, x])
"glamf" = * Longitude on f-grid (dims [t, y, x])
"gphif" = * Latitude on f-grid (dims [t, y, x])
"glamu" = * Longitude on u-grid (dims [t, y, x])
"gphiu" = * Latitude on u-grid (dims [t, y, x])
"glamv" = * Longitude on v-grid (dims [t, y, x])
"gphiv" = * Latitude on v-grid (dims [t, y, x])
"e1t" = * scale factor distance between grid cell in x direction on t-grid (dims [t, y, x])
"e2t" = * scale factor distance between grid cell in y direction on t-grid (dims [t, y, x])
"e1f" = * scale factor distance between grid cell in x direction on f-grid (dims [t, y, x])
"e2f" = * scale factor distance between grid cell in y direction on f-grid (dims [t, y, x])
"e1u" = * scale factor distance between grid cell in x direction on u-grid (dims [t, y, x])
"e2u" = * scale factor distance between grid cell in y direction on u-grid (dims [t, y, x])
"e1v" = * scale factor distance between grid cell in x direction on v-grid (dims [t, y, x])
"e2v" = * scale factor distance between grid cell in y direction on v-grid (dims [t, y, x])

"mbathy" = ** index of the ocean bottom level (may be called bottom_level) (dims [t, y, x])
            (only needed if gdept or e3t not given i.e. gdept_0 given. If gdept_0 is the
            only option and no mbathy is available offer any variable with dims [t, y, x]
            or dims [y, x])
"gdept_0" = ** 1D depth of levels on t-grid and t-levels (dims [t, z])
            (only needed if gdept or e3t not given)
"gdept" = ** 3D depth of levels on t-grid and t-levels (dims [t, z, y, x])
            (only needed if gdept_0 or e3t not given)
"gdepu" = * 3D depth of levels on u-grid and t-levels (dims [t, z, y, x])
"gdepv" = * 3D depth of levels on v-grid and t-levels (dims [t, z, y, x])
"gdepf" = * 3D depth of levels on f-grid and t-levels (dims [t, z, y, x])
"gdepw" = * 3D depth of levels on t-grid and w-levels (dims [t, z, y, x])
"gdepuw" = * 3D depth of levels on u-grid and w-levels (dims [t, z, y, x])
"gdepvw" = * 3D depth of levels on v-grid and w-levels (dims [t, z, y, x])
"e3t" = ** vertical scale factor distance between t-levels on t-grid (dims [t, z, y, x])
            (only needed if gdept or gdept_0 not given)
"e3w" = * vertical scale factor distance between w-levels on t-grid (dims [t, z, y, x])
"e3u" = * vertical scale factor distance between t-levels on u-grid (dims [t, z, y, x])
"e3v" = * vertical scale factor distance between t-levels on v-grid (dims [t, z, y, x])
"e3f" = * vertical scale factor distance between t-levels on f-grid (dims [t, z, y, x])
"e3uw" = * vertical scale factor distance between w-levels on u-grid (dims [t, z, y, x])
"e3vw" = * vertical scale factor distance between w-levels on v-grid (dims [t, z, y, x])
"e3fw" = * vertical scale factor distance between w-levels on f-grid (dims [t, z, y, x])
