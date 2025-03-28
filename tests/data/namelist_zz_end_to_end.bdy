!!>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
!! NEMO/OPA  : namelist for BDY generation tool
!!
!!             User inputs for generating open boundary conditions
!!             employed by the BDY module in NEMO. Boundary data
!!             can be set up for v3.2 NEMO and above.
!!
!!             More info here.....
!!
!!>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

!------------------------------------------------------------------------------
!   vertical coordinate
!------------------------------------------------------------------------------
   ln_zco      = .false.   !  z-coordinate - full    steps   (T/F)
   ln_zps      = .true.    !  z-coordinate - partial steps   (T/F)
   ln_sco      = .false.   !  s- or hybrid z-s-coordinate    (T/F)
   rn_hmin     =   -10     !  min depth of the ocean (>0) or
                           !  min number of ocean level (<0)

!------------------------------------------------------------------------------
!   s-coordinate or hybrid z-s-coordinate
!------------------------------------------------------------------------------
   rn_sbot_min =   10.     !  minimum depth of s-bottom surface (>0) (m)
   rn_sbot_max = 7000.     !  maximum depth of s-bottom surface
                           !  (= ocean depth) (>0) (m)
   ln_s_sigma  = .false.   !  hybrid s-sigma coordinates
   rn_hc       =  150.0    !  critical depth with s-sigma

!------------------------------------------------------------------------------
!  grid information
!------------------------------------------------------------------------------
   sn_src_hgr = './tests/data/mesh_synth_sc.nc' ! sn_src_hgr = './tests/mesh_hgr.nc'
   sn_src_zgr = './tests/data/mesh_synth_sc.nc' ! sn_src_zgr = './tests/mesh_zgr.nc'
   sn_dst_hgr = './tests/data/mesh_synth_dst.nc' ! Expects vars found in domain_cfg.nc
   sn_dst_zgr = './tests/data/mesh_synth_dst.nc' ! Expects vars: {e3u,e3v,e3w,e3t,nav_lat,nav_lon,mbathy}
   sn_src_msk = './tests/data/mesh_synth_sc.nc' ! sn_src_msk = './tests/mask.nc'
   sn_bathy   = './tests/data/mesh_synth_dst.nc' ! dst bathymetry w/o time dimension
                                                                            !Expects vars: {Bathymetry,nav_lat,nav_lon}
   sn_nme_map = './tests/data/grid_name_map.json'     ! json file mapping variable names to netcdf vars

!------------------------------------------------------------------------------
!  I/O
!------------------------------------------------------------------------------
   sn_src_dir = './tests/data/sc_test.ncml' ! src_files/'
   sn_dst_dir = './tests/data' ! sn_dst_dir = './tests'
   sn_fn      = 'data_output'        ! prefix for output files
   nn_fv      = -1e20                 !  set fill value for output files
   nn_src_time_adj = 0                ! src time adjustment
   sn_dst_metainfo = 'Benchmarking Data'

!------------------------------------------------------------------------------
!  unstructured open boundaries
!------------------------------------------------------------------------------
    ln_coords_file = .true.               !  =T : produce bdy coordinates files
    cn_coords_file = 'coordinates.bdy.nc' !  name of bdy coordinates files
                                          !  (if ln_coords_file=.TRUE.)
    ln_mask_file   = .false.              !  =T : read mask from file
    cn_mask_file   = 'mask.nc'            !  name of mask file
                                          !  (if ln_mask_file=.TRUE.)
    ln_dyn2d       = .true.               !  boundary conditions for
                                          !  barotropic fields
    ln_dyn3d       = .false.              !  boundary conditions for
                                          !  baroclinic velocities
    ln_tra         = .true.               !  boundary conditions for T and S
    ln_ice         = .false.              !  ice boundary condition
    ln_zinterp     = .true.               !  vertical interpolation
    nn_rimwidth    = 9                    !  width of the relaxation zone

!------------------------------------------------------------------------------
!  unstructured open boundaries tidal parameters
!------------------------------------------------------------------------------
    ln_tide        = .false.              !  =T : produce bdy tidal conditions
    sn_tide_model  = 'FES2014'            !  Name of tidal model. Accepts FES2014, TPXO7p2, or TPXO9v5
    clname(1)      = 'M2'                 !  constituent name
    clname(2)      = 'S2'
    clname(3)      = 'K2'
    clname(4)      = 'O1'
    clname(5)      = 'P1'
    clname(6)      = 'Q1'
    clname(7)      = 'M4'
    ln_trans       = .true.               !  interpolate transport rather than
                                          !  velocities
	! location of TPXO7.2 data
	sn_tide_grid_7p2   = './inputs/tpxo7.2/grid_tpxo7.2.nc'
	sn_tide_h          = './inputs/tpxo7.2/h_tpxo7.2.nc'
	sn_tide_u          = './inputs/tpxo7.2/u_tpxo7.2.nc'
	! location of TPXO9v5 data: single constituents per file
	sn_tide_grid_9p5   = './inputs/TPXO9_atlas_v5_nc/grid_tpxo9_atlas_30_v5.nc'
	sn_tide_dir        = './inputs/TPXO9_atlas_v5_nc/'
	! location of FES2014 data
	sn_tide_fes        = './inputs/FES2014/'

!------------------------------------------------------------------------------
!  Time information for output
!------------------------------------------------------------------------------
    sn_date_start   = '1979-11-01'    !  dst output date start YYYY-MM-DD
    sn_date_end     = '1979-12-01'    !  dst output date end YYYY-MM-DD
    sn_dst_calendar = 'gregorian'     !  output calendar format
    sn_date_origin  = '1960-01-01'    !  reference for time counter YYYY-MM-DD    ln_time_interpolation = .true. !  set to false to use parent frequency and calender
                                   !  for monthly only

!------------------------------------------------------------------------------
!  Additional parameters
!------------------------------------------------------------------------------
    nn_wei  = 1                   !  smoothing filter weights
    rn_r0   = 0.041666666         !  decorrelation distance use in gauss
                                  !  smoothing onto dst points. Need to
                                  !  make this a funct. of dlon
    sn_history  = 'Benchmarking test case'
                                  !  history for netcdf file
    ln_nemo3p4  = .true.          !  else presume v3.2 or v3.3
    nn_alpha    = 0               !  Euler rotation angle
    nn_beta     = 0               !  Euler rotation angle
    nn_gamma    = 0               !  Euler rotation angle
	rn_mask_max_depth = 100.0     !  Maximum depth to be ignored for the mask
	rn_mask_shelfbreak_dist = 20000.0 !  Distance from the shelf break
