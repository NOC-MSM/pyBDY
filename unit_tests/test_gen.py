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
    jpi = 15
    jpj = 15
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
        print("Success!")

    #Dst Coords
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 20
    zoffy = 20
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
    if write_coord_H + write_coord_Z == 0:
        print("Success!")

    # set rotation and origin point
    rot = 45
    theta = gt.radians(rot)
    origin = (7,7)

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
    if write_coord_H + write_coord_Z == 0:
        print("Success!")

    # offset grid
    dx = 100 # units in km
    dy = 100 # units in Km
    jpi = 100
    jpj = 100
    zoffx = 25
    zoffy = 25
    jpk = 10
    max_dep = 100
    min_dep = 10
    z_end_dim = 1
    sf = 10
    h_fname = 'unit_tests/test_data/test_dst_offset_hgr_zps.nc'
    z_fname = 'unit_tests/test_data/test_dst_offset_zgr_zps.nc'
    grid_h3 = gt.set_hgrid(dx,dy,jpi,jpj,zoffx,zoffy,sf)
    grid_z3 = gt.set_zgrid(grid_h2,jpk,max_dep,min_dep,z_end_dim)
    write_coord_H = gt.write_coord_H(h_fname,grid_h3)
    write_coord_Z = gt.write_coord_Z(z_fname,grid_h3,grid_z3)
    if write_coord_H + write_coord_Z == 0:
        print("Success!")


    # plot orginal, rotatated and source lat and lon
    gt.plot_grids(grid_h2['latt'],grid_h2['lont'],grid_rot['latt'],grid_rot['lont'],grid_h3['latt'], \
               grid_h3['lont'],grid_h1['latt'],grid_h1['lont'])
    # save new lat lon to dataset
    #ds.nav_lat.values[:], ds.nav_lon.values[:] = new_lat,new_lon
    # save dataset to netcdf
    #ds.to_netcdf('unit_tests/test_data/rot_'+str(rot)+'_dst_hgr_zps.nc')
    # close data files
    #ds.close()
    #src.close()
    out_fname = 'unit_tests/test_data/output_boundary.nc'
    params = {'name':'thetao','const_value':15.0,'longname':'temperature','units':'degreesC'}
    boundary = gt.write_parameter(out_fname,grid_h1,grid_z1,params)
    if boundary == 0:
        print('Success!')

if __name__ == '__main__':
    _main()