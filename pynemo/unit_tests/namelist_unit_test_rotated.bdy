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
   sn_src_hgr = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/test_src_hgr_zps.nc'
   sn_src_zgr = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/test_src_zgr_zps.nc'
   sn_dst_hgr = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/test_rot_dst_hgr_zps.nc'
   sn_dst_zgr = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/test_rot_dst_zgr_zps.nc'
   sn_src_msk = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/mask.nc'
   sn_bathy   = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_inputs/test_rot_dst_bathy.nc'

!------------------------------------------------------------------------------
!  I/O 
!------------------------------------------------------------------------------
   sn_src_dir = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/unit_tests.ncml' ! src_files/'
   sn_dst_dir = '/Users/thopri/Projects/PyNEMO/pynemo/unit_tests/test_outputs'
   sn_fn      = 'unit_test_rotated'             ! prefix for output files
   nn_fv      = -1e20                 !  set fill value for output files
   nn_src_time_adj = 0                ! src time adjustment
   sn_dst_metainfo = 'Unit Test Data'

!------------------------------------------------------------------------------
!  CMEMS Data Source Configuration
!------------------------------------------------------------------------------
   ln_use_cmems             = .true.

!------------------------------------------------------------------------------
!  unstructured open boundaries                         
!------------------------------------------------------------------------------
    ln_coords_file = .true.               !  =T : produce bdy coordinates files
    cn_coords_file = 'coordinates.bdy.nc' !  name of bdy coordinates files 
                                          !  (if ln_coords_file=.TRUE.)
    ln_mask_file   = .false.              !  =T : read mask from file
    cn_mask_file   = 'mask.nc'            !  name of mask file 
                                          !  (if ln_mask_file=.TRUE.)
    ln_dyn2d       = .true.              !  boundary conditions for
                                          !  barotropic fields
    ln_dyn3d       = .false.              !  boundary conditions for 
                                          !  baroclinic velocities
    ln_tra         = .true.               !  boundary conditions for T and S
    ln_ice         = .false.              !  ice boundary condition   
    nn_rimwidth    = 9                    !  width of the relaxation zone

!------------------------------------------------------------------------------
!  unstructured open boundaries tidal parameters                        
!------------------------------------------------------------------------------
    ln_tide        = .false.              !  =T : produce bdy tidal conditions
    sn_tide_model  = 'FES'                !  Name of tidal model (FES|TPXO)
    clname(1)      = 'M2'                 !  constituent name
    clname(2)      = 'S2'         
    clname(3)      = 'K2'        
    ln_trans       = .true.               !  interpolate transport rather than
                                          !  velocities
!------------------------------------------------------------------------------
!  Time information
!------------------------------------------------------------------------------
    nn_year_000     = 2017        !  year start
    nn_year_end     = 2017        !  year end
    nn_month_000    = 01          !  month start (default = 1 is years>1)
    nn_month_end    = 01          !  month end (default = 12 is years>1)
    sn_dst_calendar = 'gregorian' !  output calendar format
    nn_base_year    = 1960        !  base year for time counter
	sn_tide_grid   = './src_data/tide/grid_tpxo7.2.nc'
	sn_tide_h      = './src_data/tide/h_tpxo7.2.nc'
	sn_tide_u      = './src_data/tide/u_tpxo7.2.nc'
	
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
