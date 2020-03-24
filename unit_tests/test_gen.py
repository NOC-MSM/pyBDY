"""
Source: https://gist.github.com/LyleScott/d17e9d314fbe6fc29767d8c5c029c362

Adapted Function to rotate NEMO grid for unit testing. rot variable defines how much rotation
occurs, the results are then plotted in a figure showing original (blue points) and rotated (red) grids.
The source coordinate grid is also plotted (green).

"""
import unit_tests.gen_tools as gt

# TODO: remove hard coded file names and directories.
# TODO: organise the variables better, (maybe in a single dict?)

def _main():
    #Source Coords
    dx = 1000 # units in km
    dy = 1000 # units in Km
    jpi = 16
    jpj = 16
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    h_fname = 'unit_tests/test_data/test_src_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_src_zgr_zps.nc'
    grid_h1 = gt.set_hgrid(dx,dy,jpi,jpj)
    grid_z1 = gt.set_zgrid(grid_h1,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = gt.write_coord_H(h_fname,grid_h1)
    write_coord_Z = gt.write_coord_Z(z_fname,grid_h1,grid_z1)
    if write_coord_H + write_coord_Z == 0:
        print("Parent grid generation successful!")

    #Dst Coords
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 30
    zoffy = 30
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    sf = 10
    h_fname = 'unit_tests/test_data/test_dst_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_dst_zgr_zps.nc'
    grid_h2 = gt.set_hgrid(dx,dy,jpi,jpj,zoffx,zoffy,sf)
    grid_z2 = gt.set_zgrid(grid_h2,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = gt.write_coord_H(h_fname,grid_h2)
    write_coord_Z = gt.write_coord_Z(z_fname,grid_h2,grid_z2)
    # write bathy files (constant bathy)
    bathy_fname = 'unit_tests/test_data/test_dst_bathy.nc'
    bathy = gt.write_bathy(bathy_fname,grid_h2,grid_z2)
    if write_coord_H + write_coord_Z + bathy == 0:
        print("Org child grid generation successful!")

    # set rotation and origin point
    rot = 45
    theta = gt.radians(rot)
    origin = (8,8)

    # rotate grid
    rot_h_fname = 'unit_tests/test_data/test_rot_dst_hgr_zps.nc'
    rot_z_fname = 'unit_tests/test_data/test_rot_dst_zgr_zps.nc'
    grid_rot = grid_h2.copy()
    grid_rot['latt'], grid_rot['lont'] = gt.rotate_around_point(grid_h2['latt'],grid_h2['lont'],theta,origin)
    grid_rot['latu'], grid_rot['lonu'] = gt.rotate_around_point(grid_h2['latu'], grid_h2['lonu'], theta, origin)
    grid_rot['latv'], grid_rot['lonv'] = gt.rotate_around_point(grid_h2['latv'], grid_h2['lonv'], theta, origin)
    grid_rot['latf'], grid_rot['lonf'] = gt.rotate_around_point(grid_h2['latf'], grid_h2['lonf'], theta, origin)
    write_coord_H = gt.write_coord_H(rot_h_fname,grid_rot)
    write_coord_Z = gt.write_coord_Z(rot_z_fname,grid_rot,grid_z2)
    # write bathy files (constant bathy)
    bathy_fname = 'unit_tests/test_data/test_rot_dst_bathy.nc'
    bathy = gt.write_bathy(bathy_fname,grid_rot,grid_z2)
    if write_coord_H + write_coord_Z + bathy == 0:
        print("Rotated child grid generation Successful!")

    # offset grid
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 35
    zoffy = 35
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    sf = 10
    h_fname = 'unit_tests/test_data/test_offset_dst_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_offset_dst_zgr_zps.nc'
    grid_h3 = gt.set_hgrid(dx,dy,jpi,jpj,zoffx,zoffy,sf)
    grid_z3 = gt.set_zgrid(grid_h2,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = gt.write_coord_H(h_fname,grid_h3)
    write_coord_Z = gt.write_coord_Z(z_fname,grid_h3,grid_z3)
    # write bathy files (constant bathy)
    bathy_fname = 'unit_tests/test_data/test_offset_dst_bathy.nc'
    bathy = gt.write_bathy(bathy_fname,grid_h3,grid_z3)
    if write_coord_H + write_coord_Z + bathy == 0:
        print("Offset child grid gneration successful!")

    # plot orginal, rotatated and source lat and lon
    #gt.plot_grids(grid_h2['latt'],grid_h2['lont'],grid_rot['latt'],grid_rot['lont'],grid_h3['latt'], \
    #           grid_h3['lont'],grid_h1['latt'],grid_h1['lont'])

    # write boundary files (constant parameters)
    out_fname = 'unit_tests/test_data/output_boundary' #drop file extension
    params_t = {'param1': {'name':'thetao','const_value':15.0,'longname':'temperature','units':'degreesC'},
              'param2': {'name':'so','const_value':35.0,'longname':'salinity','units':'PSU'},
              'param3': {'name': 'zos', 'const_value': 1.0, 'longname': 'sea surface height', 'units': 'metres'}
              }
    params_u = {'param1': {'name':'uo','const_value':0.5,'longname':'Zonal current','units':'ms-1'}
              }
    params_v = {'param1': {'name':'vo','const_value':0.5,'longname':'Meridional current','units':'ms-1'}
              }
    # TODO: This needs to be adapted for parameters that are not on the T grid.
    boundary_T = gt.write_parameter(out_fname,grid_h1,grid_z1,params_t,'t')
    boundary_U = gt.write_parameter(out_fname, grid_h1, grid_z1, params_u, 'u')
    boundary_V = gt.write_parameter(out_fname, grid_h1, grid_z1, params_v, 'v')
    if boundary_T + boundary_U + boundary_V == 0:
        print('Boundary file generation successful!')

    #write_mask
    mask_fname = 'unit_tests/test_data/mask.nc'
    mask = gt.write_mask(mask_fname,grid_h1,grid_z1)
    if mask == 0:
        print('Mask file generation successful!')

    return 0

if __name__ == '__main__':
    _main()