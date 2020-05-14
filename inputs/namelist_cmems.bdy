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
   sn_src_hgr = '/Users/thopri/Projects/PyNEMO/inputs/subset_coordinates.nc'
   sn_src_zgr = '/Users/thopri/Projects/PyNEMO/inputs/subset_coordinates.nc'
   sn_dst_hgr = 'http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_grid_C/mesh_hgr_zps.nc'
   sn_dst_zgr = 'http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_grid_C/mesh_zgr_zps.nc'
   sn_src_msk = '/Users/thopri/Projects/PyNEMO/inputs/subset_bathy.nc'
   sn_bathy   = 'http://opendap4gws.jasmin.ac.uk/thredds/noc_msm/dodsC/pynemo_grid_C/NNA_R12_bathy_meter_bench.nc'

!------------------------------------------------------------------------------
!  I/O 
!------------------------------------------------------------------------------
   sn_src_dir = '/Users/thopri/Projects/PyNEMO/inputs/CMEMS.ncml' ! src_files/'
   sn_dst_dir = '/Users/thopri/Projects/PyNEMO/outputs'

   sn_fn      = 'NNA_R12'             ! prefix for output files
   nn_fv      = -1e20                 !  set fill value for output files
   nn_src_time_adj = 0                ! src time adjustment
   sn_dst_metainfo = 'CMEMS example'
   
!------------------------------------------------------------------------------
!  CMEMS Data Source Configuration
!------------------------------------------------------------------------------
   ln_use_cmems             = .true.
   ln_download_cmems        = .false.
   sn_cmems_dir             = '/Users/thopri/Projects/PyNEMO/inputs/' ! where to download CMEMS input files (static and variable)
   ln_download_static       = .false.
   ln_subset_static         = .false.
   nn_num_retry             = 4 ! how many times to retry CMEMS download after non critical errors?
!------------------------------------------------------------------------------
!  CMEMS MOTU Configuration (for Boundary Data)
!------------------------------------------------------------------------------
   sn_motu_server           = 'http://nrt.cmems-du.eu/motu-web/Motu'
   sn_cmems_config_template = '/Users/thopri/Projects/PyNEMO/pynemo/config/motu_config_template.ini'
   sn_cmems_config          = '/Users/thopri/Projects/PyNEMO/pynemo/config/motu_config.ini'
   sn_cmems_model           = 'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS'
   sn_cmems_product         = 'global-analysis-forecast-phy-001-024'
   sn_dl_prefix             = 'subset'
!------------------------------------------------------------------------------
!  CMEMS FTP Configuration (for Static Files)
!------------------------------------------------------------------------------
   sn_ftp_server            = 'nrt.cmems-du.eu'
   sn_static_dir            = '/Core/GLOBAL_ANALYSIS_FORECAST_PHY_001_024/global-analysis-forecast-phy-001-024-statics'
   sn_static_filenames      = 'GLO-MFC_001_024_coordinates.nc GLO-MFC_001_024_mask_bathy.nc GLO-MFC_001_024_mdt.nc'
   sn_cdo_loc               = '/opt/local/bin/cdo' ! location of cdo executable can be found by running "where cdo"
!------------------------------------------------------------------------------
!  CMEMS Extent Configuration
!------------------------------------------------------------------------------
   nn_latitude_min          = 40
   nn_latitude_max          = 66
   nn_longitude_min         = -22
   nn_longitude_max         = 16
   nn_depth_min             = 0.493
   nn_depth_max             = 5727.918000000001

!------------------------------------------------------------------------------
!  unstructured open boundaries                         
!------------------------------------------------------------------------------
    ln_coords_file = .true.               !  =T : produce bdy coordinates files
    cn_coords_file = 'coordinates.bdy.nc' !  name of bdy coordinates files 
                                          !  (if ln_coords_file=.TRUE.)
    ln_mask_file   = .false.              !  =T : read mask from file
    cn_mask_file   = '/Users/thopri/Projects/PyNEMO/inputs/subset_mask.nc'            !  name of mask file
                                          !  (if ln_mask_file=.TRUE.)
    ln_dyn2d       = .false.              !  boundary conditions for 
                                          !  barotropic fields
    ln_dyn3d       = .false.              !  boundary conditions for
                                          !  baroclinic velocities
    ln_tra         = .false.               !  boundary conditions for T and S
    ln_ice         = .false.              !  ice boundary condition   
    nn_rimwidth    = 9                    !  width of the relaxation zone

!------------------------------------------------------------------------------
!  unstructured open boundaries tidal parameters                        
!------------------------------------------------------------------------------
    ln_tide        = .true.              !  =T : produce bdy tidal conditions
    sn_tide_model  = 'fes'                !  Name of tidal model (fes|tpxo)
    clname(1)      = 'M2'                 !  constituent name
    clname(2)      = 'S2'
    !clname(3)      = 'N2'
    !clname(4)      = 'O1'
    !clname(5)      = 'K1'
    !clname(6)      = 'K2'
    !clname(7)      = 'L2'
    !clname(8)      = 'NU2'
    !clname(9)      = 'M4'
    !clname(10)     = 'MS4'
    !clname(11)     = 'Q1'
    !clname(12)     = 'P1'
    !clname(13)     = 'S1'
    !clname(14)     = '2N2'
    !clname(15)     = 'MU2'
    ln_trans       = .false.                !  interpolate transport rather than velocities
    ln_tide_checker = .true.                ! run tide checker on PyNEMO tide output
    sn_ref_model    = 'fes'                 ! which model to check output against (FES only)
!------------------------------------------------------------------------------
!  Time information
!------------------------------------------------------------------------------
    nn_year_000     = 2017        !  year start
    nn_year_end     = 2017        !  year end
    nn_month_000    = 01          !  month start (default = 1 is years>1)
    nn_month_end    = 03       !  month end (default = 12 is years>1)
    sn_dst_calendar = 'gregorian' !  output calendar format
    nn_base_year    = 1960        !  base year for time counter
    ! TPXO file locations
	sn_tide_grid   = '/Users/thopri/Projects/PyNEMO/DATA/TPXO/grid_tpxo7.2.nc'
	sn_tide_h      = '/Users/thopri/Projects/PyNEMO/DATA/TPXO/h_tpxo7.2.nc'
	sn_tide_u      = '/Users/thopri/Projects/PyNEMO/DATA/TPXO/u_tpxo7.2.nc'
	! location of FES data
	sn_tide_fes      = '/Users/thopri/Projects/PyNEMO/DATA/FES/'
	
!------------------------------------------------------------------------------
!  Additional parameters
!------------------------------------------------------------------------------
    nn_wei  = 1                   !  smoothing filter weights 
    rn_r0   = 0.041666666         !  decorrelation distance use in gauss
                                  !  smoothing onto dst points. Need to 
                                  !  make this a funct. of dlon
    sn_history  = 'CMEMS test case'
                                  !  history for netcdf file
    ln_nemo3p4  = .true.          !  else presume v3.2 or v3.3
    nn_alpha    = 0               !  Euler rotation angle
    nn_beta     = 0               !  Euler rotation angle
    nn_gamma    = 0               !  Euler rotation angle
	rn_mask_max_depth = 100.0     !  Maximum depth to be ignored for the mask
	rn_mask_shelfbreak_dist = 20000.0 !  Distance from the shelf break
