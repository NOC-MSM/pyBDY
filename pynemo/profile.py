# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

'''
Created on Wed Sep 12 08:02:46 2012

The main application script for the NRCT. 

@author James Harle
@author John Kazimierz Farey
@author Srikanth Nagella
$Last commit on:$
'''

# pylint: disable=E1103
# pylint: disable=no-name-in-module

#External imports
import time
import logging
import numpy as np
from PyQt5.QtWidgets import QMessageBox
from calendar import monthrange
import sys

#Local imports
from pynemo import pynemo_settings_editor
from pynemo import nemo_bdy_ncgen as ncgen
from pynemo import nemo_bdy_ncpop as ncpop
from pynemo import nemo_bdy_source_coord as source_coord
from pynemo import nemo_bdy_dst_coord as dst_coord
from pynemo import nemo_bdy_setup as setup
from pynemo import nemo_bdy_gen_c as gen_grid
from pynemo import nemo_coord_gen_pop as coord
from pynemo import nemo_bdy_zgrv2 as zgrv
from pynemo import nemo_bdy_extr_tm3 as extract

from pynemo.reader.factory import GetFile
from pynemo.reader import factory
from pynemo.tide import nemo_bdy_tide3 as tide
from pynemo.tide import nemo_bdy_tide_ncgen
from pynemo.tests import nemo_tide_test as tt
from pynemo.utils import Constants
from pynemo.gui.nemo_bdy_mask import Mask as Mask_File
from pynemo import nemo_bdy_dl_cmems as dl_cmems

class Grid(object):
    """ 
    A Grid object that stores bdy grid information
    """    
    def __init__(self):
        self.bdy_i       = None # bdy indices
        self.bdy_r       = None # associated rimwidth values
        self.grid_type   = None # this can be T/U/V
        self.fname_2     = None # 2nd file for vector rotation
        self.max_i       = None # length of i-axis in fname_2
        self.max_j       = None # length of j-axis in fname_2
        self.source_time = None # netcdftime information from parent files

logger = logging.getLogger(__name__)
logging.basicConfig(filename='nrct.log', level=logging.INFO)

def download_cmems(setup_filepath=0):
    '''
    CMEMS download function.

    This is the main script to download CMEMS data, it has been removed from core PyNEMO function
    to handle issues with downloading better e.g. connection issues etc.

    Input options are handled in the same NEMO style namelist that the main script uses.


    :param setup_filepath:
    :param mask_gui:
    :return:
    '''
    logger.info('============================================')
    logger.info('Start CMEMS download Logging: ' + time.asctime())
    logger.info('============================================')

    Setup = setup.Setup(setup_filepath)  # default settings file
    settings = Setup.settings
    if settings['download_static'] == False:
        logger.info('CMEMS static data download not requested')
    if settings['download_static'] == True:
        for re in range(settings['num_retry']):
            logger.info('CMEMS Static data requested: downloading static data now.... (this may take awhile)')
            static = dl_cmems.get_static(settings)
            if static == 0:
                logger.info('CMEMS static data downloaded')
                break
            if type(static) == str:
                err_chk = dl_cmems.err_parse(static,'FTP')
                if err_chk == 0:
                    logger.info('retrying FTP download....retry number '+str(re+1)+' of '+str(settings['num_retry']) )
                    if re == (settings['num_retry']-1):
                        logger.critical('reached retry limit defined in BDY file, exiting now')
                        logger.critical(static)
                        dl_cmems.clean_up(settings)
                        sys.exit(static)
                if err_chk == 1:
                    dl_cmems.clean_up(settings)
                    sys.exit(static)
                if err_chk == 2:
                    dl_cmems.clean_up(settings)
                    sys.exit(static)
        dl_cmems.clean_up(settings)

    # subset downloaded static grid files to match downloaded CMEMS data
    if settings['subset_static'] == False:
        logger.info('CMEMS subset static data not requested')
    if settings['subset_static'] == True:
        logger.info('CMEMS subset static data requested: subsetting now......')
        subset_static = dl_cmems.subset_static(settings)
        if subset_static == 0:
            logger.info('CMEMS static data subset successfully')
        if type(subset_static) == str:
            logger.error(subset_static)
            dl_cmems.clean_up(settings)
            sys.exit(subset_static)
        dl_cmems.clean_up(settings)

    if settings['download_cmems'] == False:
        logger.info('CMEMS Boundary data download not requested')

    if settings['download_cmems'] == True:

        logger.info('CMEMS Boundary data requested: starting download process....')

        if settings['year_end'] - settings['year_000'] > 0:
            date_min = str(settings['year_000']) + '-01-01'
            date_max = str(settings['year_end']) + '-12-31'

        elif settings['year_end'] - settings['year_000'] == 0:

            days_mth = monthrange(settings['year_end'], settings['month_end'])
            date_min = str(settings['year_000']) + '-' + str(settings['month_000']).zfill(2) + '-01'
            date_max = str(settings['year_end']) + '-' + str(settings['month_end']).zfill(2) + '-' + str(
                days_mth[1])

        elif settings['year_end'] - settings['year_000'] < 0:
            error_msg = 'end date before start date please ammend bdy file'
            logger.error(error_msg)
            dl_cmems.clean_up(settings)
            sys.exit(error_msg)
        else:
            logger.warning('unable to parse dates..... using demo date November 2017')
            date_min = '2017-11-01'
            date_max = '2017-11-30'
        # check to see if MOTU client is installed
        chk = dl_cmems.chk_motu()
        if chk == 1:
            error_msg = 'motuclient not installed, please install by running $ pip install motuclient'
            logger.error(error_msg)
            dl_cmems.clean_up(settings)
            sys.exit(error_msg)
        if type(chk) == str:
            logger.info('version ' + chk + ' of motuclient is installed')
        else:
            error_msg = 'unable to parse MOTU check'
            logger.error(error_msg)
            dl_cmems.clean_up(settings)
            sys.exit(error_msg)
        # download request for CMEMS data, try whole time interval first.
        for re in range(settings['num_retry']):
            logger.info('starting CMES download now (this can take a while)...')
            dl = dl_cmems.request_cmems(settings, date_min, date_max)
            if dl == 0:
                logger.info('CMES data downloaded successfully')
                break
            # a string return means MOTU has return an error
            if type(dl) == str:
            # check error message against logged errors
                err_chk = dl_cmems.err_parse(dl,'MOTU')
            # error is known and retry is likely to work
                if err_chk == 0:
                    logger.info('retrying CMEMS download....retry number '+str(re+1)+' of '+str(settings['num_retry']) )
                    if re == (settings['num_retry']-1):
                        logger.critical('reached retry limit defined in BDY file, exiting now')
                        logger.critical(dl)
                        dl_cmems.clean_up(settings)
                        sys.exit(dl)
            # error is known and retry is likely to not work
                if err_chk == 1:
                    dl_cmems.clean_up(settings)
                    sys.exit(dl)
            # error is not logged, add to error file.
                if err_chk == 2:
                    dl_cmems.clean_up(settings)
                    sys.exit(dl)
            if dl == 1:
                # if the request is too large try monthly intervals
                logger.warning('CMEMS request too large, try monthly downloads...(this may take awhile)')
                mnth_dl = dl_cmems.MWD_request_cmems(settings, date_min, date_max, 'M')
                if mnth_dl == 0:
                    logger.info('CMEMS monthly request successful')
                    break
                if type(mnth_dl) == str:
                    err_chk = dl_cmems.err_parse(mnth_dl,'MOTU')
                    if err_chk == 0:
                        logger.info('retrying CMEMS download....retry number '+str(re+1)+' of '+str(settings['num_retry']) )
                        if re == (settings['num_retry']-1):
                            logger.critical('reached retry limit defined in BDY file, exiting now')
                            logger.critical(mnth_dl)
                            dl_cmems.clean_up(settings)
                            sys.exit(mnth_dl)
                    if err_chk == 1:
                        dl_cmems.clean_up(settings)
                        sys.exit(mnth_dl)
                    if err_chk == 2:
                        dl_cmems.clean_up(settings)
                        sys.exit(mnth_dl)
                if mnth_dl == 1:
                    # if the request is too large try weekly intervals
                    logger.warning('CMEMS request still too large, trying weekly downloads...(this will take longer...)')
                    wk_dl = dl_cmems.MWD_request_cmems(settings, date_min, date_max, 'W')
                    if wk_dl == 0:
                        logger.info('CMEMS weekly request successful')
                        break
                    if type(wk_dl) == str:
                        err_chk = dl_cmems.err_parse(wk_dl,'MOTU')
                        if err_chk == 0:
                            logger.info('retrying CMEMS download....retry number ' + str(re + 1) + ' of ' + str(settings['num_retry']))
                            if re == (settings['num_retry'] - 1):
                                logger.critical('reached retry limit defined in BDY file, exiting now')
                                logger.critical(wk_dl)
                                dl_cmems.clean_up(settings)
                                sys.exit(wk_dl)
                        if err_chk == 1:
                            dl_cmems.clean_up(settings)
                            sys.exit(wk_dl)
                        if err_chk == 2:
                            dl_cmems.clean_up(settings)
                            sys.exit(wk_dl)
                    if wk_dl == 1:
                        # if the request is too large try daily intervals.
                        logger.warning('CMESM request STILL too large, trying daily downloads....(even longer.....)')
                        dy_dl = dl_cmems.MWD_request_cmems(settings, date_min, date_max, 'D')
                        if dy_dl == 0:
                            logger.info('CMEMS daily request successful')
                            break
                        # if the request is still too large then smaller domain is required.
                        if dy_dl == str:
                            # perform error check for retry
                            err_chk = dl_cmems.err_parse(dy_dl,'MOTU')
                            if err_chk == 0:
                                logger.info('retrying CMEMS download....retry number ' + str(re + 1) + ' of ' + str(settings['num_retry']))
                                if re == (settings['num_retry'] - 1):
                                    logger.critical('reached retry limit defined in BDY file, exiting now')
                                    logger.critical(dy_dl)
                                    dl_cmems.clean_up(settings)
                                    sys.exit(dy_dl)
                            if err_chk == 1:
                                dl_cmems.clean_up(settings)
                                sys.exit(dy_dl)
                            if err_chk == 2:
                                dl_cmems.clean_up(settings)
                                sys.exit(dy_dl)
# end of messy if statements to split requests into months, weeks and days as needed.
        dl_cmems.clean_up(settings)
    logger.info('============================================')
    logger.info('End CMEMS download: ' + time.asctime())
    logger.info('============================================')


def process_bdy(setup_filepath=0, mask_gui=False):
    """ 
    Main entry for processing BDY lateral boundary conditions.

    This is the main script that handles all the calls to generate open 
    boundary conditions for a given regional domain. Input options are handled 
    in a NEMO style namelist (namelist.bdy). There is an optional GUI allowing
    the user to create a mask that defines the extent of the regional model.

    Args:
        setup_filepath (str) : file path to find namelist.bdy
        mask_gui       (bool): whether use of the GUI is required

    """
    # Start Logger
    logger.info('============================================')
    logger.info('Start NRCT Logging: '+time.asctime())
    logger.info('============================================')
    
    SourceCoord = source_coord.SourceCoord()
    DstCoord    = dst_coord.DstCoord()

    Setup = setup.Setup(setup_filepath) # default settings file
    settings = Setup.settings

    logger.info('Reading grid completed')

    bdy_msk = _get_mask(Setup, mask_gui)
    DstCoord.bdy_msk = bdy_msk == 1
    
    logger.info('Reading mask completed')
    
    bdy_ind = {} # define a dictionary to hold the grid information
    
    for grd in ['t', 'u', 'v']:
        bdy_ind[grd] = gen_grid.Boundary(bdy_msk, settings, grd)
        logger.info('Generated BDY %s information', grd)
        logger.info('Grid %s has shape %s', grd, bdy_ind[grd].bdy_i.shape)

    # TODO: Write in option to seperate out disconnected LBCs
    
    # Write out grid information to coordinates.bdy.nc

    co_set = coord.Coord(settings['dst_dir']+'/coordinates.bdy.nc', bdy_ind)
    co_set.populate(settings['dst_hgr'])
    logger.info('File: coordinates.bdy.nc generated and populated')

    # Idenitify number of boundary points
    
    nbdy = {}
    
    for grd in ['t', 'u', 'v']:
        nbdy[grd] = len(bdy_ind[grd].bdy_i[:, 0])

    # Gather grid information
    
    # TODO: insert some logic here to account for 2D or 3D src_zgr
    
    logger.info('Gathering grid information')
    nc = GetFile(settings['src_zgr'])
    try:
        SourceCoord.zt = np.squeeze(nc['gdept_0'][:])
    except:
        SourceCoord.zt = np.squeeze(nc['depth'][:])
    nc.close()

    # Define z at t/u/v points

    z = zgrv.Depth(bdy_ind['t'].bdy_i,
                   bdy_ind['u'].bdy_i,
                   bdy_ind['v'].bdy_i, settings)

    # TODO: put conditional here as we may want to keep data on parent
    #       vertical grid
   
    DstCoord.depths = {'t': {}, 'u': {}, 'v': {}}

    for grd in ['t', 'u', 'v']:
        DstCoord.depths[grd]['bdy_H']  = np.nanmax(z.zpoints['w'+grd], axis=0)
        DstCoord.depths[grd]['bdy_dz'] = np.diff(z.zpoints['w'+grd], axis=0)
        DstCoord.depths[grd]['bdy_z']  = z.zpoints[grd]

    logger.info('Depths defined')
    
    # Gather vorizontal grid information
    # TODO: Sort generic grid variables (define in bdy file?)
    nc = GetFile(settings['src_hgr'])

    try:
        SourceCoord.lon = nc['glamt'][:,:]
        SourceCoord.lat = nc['gphit'][:,:]
    except:
        SourceCoord.lon = nc['longitude'][:]
        SourceCoord.lat = nc['latitude'][:]
        # expand lat and lon 1D arrays into 2D array matching nav_lat nav_lon
        SourceCoord.lon = np.tile(SourceCoord.lon, (np.shape(SourceCoord.lat)[0], 1))
        SourceCoord.lat = np.tile(SourceCoord.lat, (np.shape(SourceCoord.lon)[1], 1))
        SourceCoord.lat = np.rot90(SourceCoord.lat)
    
    try: # if they are masked array convert them to normal arrays
        SourceCoord.lon = SourceCoord.lon.filled()
    except:
        pass
    try:
        SourceCoord.lat = SourceCoord.lat.filled()
    except:
        pass
        
    nc.close()

    DstCoord.lonlat = {'t': {}, 'u': {}, 'v': {}}

    nc = GetFile(settings['dst_hgr'])

    # Read and assign horizontal grid data
    
    for grd in ['t', 'u', 'v']:
        DstCoord.lonlat[grd]['lon'] = nc['glam' + grd][0, :, :]
        DstCoord.lonlat[grd]['lat'] = nc['gphi' + grd][0, :, :]
    
    nc.close()

    logger.info('Grid coordinates defined')
    
    # Identify lons/lats of the BDY points
    
    DstCoord.bdy_lonlat = {'t': {}, 'u': {}, 'v': {}}
     
    for grd in ['t', 'u', 'v']:
        for l in ['lon', 'lat']:
            DstCoord.bdy_lonlat[grd][l] = np.zeros(nbdy[grd])

    for grd in ['t', 'u', 'v']:
        for i in range(nbdy[grd]):
            x = bdy_ind[grd].bdy_i[i, 1]
            y = bdy_ind[grd].bdy_i[i, 0]
            DstCoord.bdy_lonlat[grd]['lon'][i] =                              \
                                              DstCoord.lonlat[grd]['lon'][x, y]
            DstCoord.bdy_lonlat[grd]['lat'][i] =                              \
                                              DstCoord.lonlat[grd]['lat'][x, y]

        DstCoord.lonlat[grd]['lon'][DstCoord.lonlat[grd]['lon'] > 180] -= 360

    logger.info('BDY lons/lats identified from %s', settings['dst_hgr'])

    # Set up time information
    
    t_adj = settings['src_time_adj'] # any time adjutments?
    reader = factory.GetReader(settings['src_dir'],t_adj)
    for grd in ['t', 'u', 'v']:
        bdy_ind[grd].source_time = reader[grd]
 
    unit_origin = '%d-01-01 00:00:00' %settings['base_year']

    # Extract source data on dst grid

    if settings['tide']:
        if settings['tide_model']=='tpxo':
            cons = tide.nemo_bdy_tide_rot(
                Setup, DstCoord, bdy_ind['t'], bdy_ind['u'], bdy_ind['v'],
                                                               settings['clname'], settings['tide_model'])
            write_tidal_data(Setup, DstCoord, bdy_ind, settings['clname'], cons)

            if settings['tide_checker'] == True:
                logger.info('tide checker starting now.....')
                tt_test = tt.main(setup_filepath,settings['amp_thres'],settings['ref_model'])
                if tt_test == 0:
                    logger.info('tide checker ran successfully, check spreadsheet in output folder')
                if tt_test !=0:
                    logger.warning('error running tide checker')

        elif settings['tide_model']=='fes':
            cons = tide.nemo_bdy_tide_rot(
                Setup, DstCoord, bdy_ind['t'], bdy_ind['u'], bdy_ind['v'],
                                                            settings['clname'],settings['tide_model'])
            write_tidal_data(Setup, DstCoord, bdy_ind, settings['clname'], cons)

            if settings['tide_checker'] == True:
                logger.info('tide checker starting now.....')
                tt_test = tt.main(setup_filepath,settings['amp_thres'],settings['ref_model'])
                if tt_test == 0:
                    logger.info('tide checker ran successfully, check spreadsheet in output folder')
                if tt_test !=0:
                    logger.warning('error running tide checker')
        else:
            logger.error('Tidal model: %s, not recognised', 
                         settings['tide_model'])
            return

    logger.info('Tidal constituents written to file')
    
    # Set the year and month range
    
    yr_000 = settings['year_000']
    yr_end = settings['year_end']
    mn_000 = settings['month_000']
    mn_end = settings['month_end']
    
    if yr_000 > yr_end:
        logging.error('Please check the nn_year_000 and nn_year_end '+ 
                      'values in input bdy file')
        return
    
    yrs = list(range(yr_000, yr_end+1))
    
    if yr_end - yr_000 >= 1:
        if list(range(mn_000, mn_end+1)) < 12:
            logger.info('Warning: All months will be extracted as the number '+
                        'of years is greater than 1')
        mns = list(range(1,13))
    else:
        mn_000 = settings['month_000']
        mn_end = settings['month_end']
        if mn_end > 12 or mn_000 < 1:
            logging.error('Please check the nn_month_000 and nn_month_end '+
                          'values in input bdy file')
            return
        mns = list(range(mn_000, mn_end+1))
    
    # Enter the loop for each year and month extraction
    
    logger.info('Entering extraction loop')
    
    ln_dyn2d   = settings['dyn2d']            
    ln_dyn3d   = settings['dyn3d'] # are total or bc velocities required
    ln_tra     = settings['tra']          
    ln_ice     = settings['ice']   

    # Define mapping of variables to grids with a dictionary
    
    emap = {}
    grd  = [  't',  'u',  'v']
    #pair = [ None, 'uv', 'uv'] # TODO: devolve this to the namelist?
    pair = [None, None, None]
    # TODO: The following is a temporary stop gap to assign variables for both CMEMS downloads
    #  and existing variable names. In future we need a slicker way of determining the variables to extract.
    # Perhaps by scraping the .ncml file - this way biogeochemical tracers
    # can be included in the ln_tra = .true. option without having to
    # explicitly declaring them.

    var_in = {}
    for g in range(len(grd)):
        var_in[grd[g]] = []
    if 'use_cmems' in settings:
        if settings['use_cmems'] == True:
            logger.info('using CMEMS variable names......')
            if ln_tra:
                var_in['t'].extend(['thetao'])
                #var_in['t'].extend(['so'])

            if ln_dyn2d or ln_dyn3d:
                var_in['u'].extend(['uo'])
                var_in['v'].extend(['vo'])

            if ln_dyn2d:
                var_in['t'].extend(['zos'])

            if ln_ice:
                var_in['t'].extend(['siconc', 'sithick'])

        if settings['use_cmems'] == False:
            logger.info('using existing PyNEMO variable names.....')
            if ln_tra:
                var_in['t'].extend(['votemper', 'vosaline'])

            if ln_dyn2d or ln_dyn3d:
                var_in['u'].extend(['vozocrtx'])
                var_in['v'].extend(['vomecrty'])

            if ln_dyn2d:
                var_in['t'].extend(['sossheig'])

            if ln_ice:
                var_in['t'].extend(['iicethic', 'ileadfra', 'isnowthi'])

    if 'use_cmems' not in settings:
        logger.info('using existing PyNEMO variable names.....')
        if ln_tra:
            var_in['t'].extend(['votemper', 'vosaline'])

        if ln_dyn2d or ln_dyn3d:
            var_in['u'].extend(['vozocrtx'])
            var_in['v'].extend(['vomecrty'])

        if ln_dyn2d:
            var_in['t'].extend(['sossheig'])

        if ln_ice:
            var_in['t'].extend(['iicethic', 'ileadfra', 'isnowthi'])
    
    # As variables are associated with grd there must be a filename attached
    # to each variable
    
    for g in range(len(grd)):
        
        if len(var_in[grd[g]])>0:
            emap[grd[g]]= {'variables': var_in[grd[g]],
                           'pair'     : pair[g]} 

    extract_obj = {}
    
    # Initialise the mapping indices for each grid 
    
    for key, val in list(emap.items()):
        
        extract_obj[key] = extract.Extract(Setup.settings, 
                                           SourceCoord, DstCoord,
                                           bdy_ind, val['variables'], 
                                           key, val['pair'])
    
    # TODO: Write the nearest neighbour parent grid point to each bdy point
    #       possibly to the coordinates.bdy.nc file to help with comparison
    #       plots later.
        
    for year in yrs:
        for month in mns:
            for key, val in list(emap.items()):
                
                # Extract the data for a given month and year
                
                extract_obj[key].extract_month(year, month)
                
                # Interpolate/stretch in time if time frequecy is not a factor 
                # of a month and/or parent:child calendars differ
                
                extract_obj[key].time_interp(year, month)
                
                # Finally write to file
                
                extract_obj[key].write_out(year, month, bdy_ind[key], 
                                           unit_origin)
                
    logger.info('End NRCT Logging: '+time.asctime())
    logger.info('==========================================')
                

def write_tidal_data(setup_var, dst_coord_var, grid, tide_cons, cons):
    """ 
    This method writes the tidal data to netcdf file.

    Args:
        setup_var     (list): Description of arg1
        dst_coord_var (obj) : Description of arg1
        grid          (dict): Description of arg1
        tide_cons     (list): Description of arg1
        cons          (data): Description of arg1
    """
    indx = 0
    
    # Mapping of variable names to grid types
    
    tmap = {}
    grd = ['t', 'u', 'v']
    var = ['z', 'u', 'v']
    des = ['tidal elevation components for:',
           'tidal east velocity components for:',
           'tidal north velocity components for:']
    
    for g in range(len(grd)):
        bdy_r = grid[grd[g]].bdy_r
        tmap[grd[g]]= {'nam': var[g], 'des': des[g], 
                       'ind': np.where(bdy_r == 0),
                       'nx' : len(grid[grd[g]].bdy_i[bdy_r == 0, 0])}
        
    # Write constituents to file
    
    for tide_con in tide_cons:
        
        const_name = setup_var.settings['clname'][tide_con]
        const_name = const_name.replace("'", "").upper()

        for key,val in list(tmap.items()):
            
            fout_tide = setup_var.settings['dst_dir']+             \
                        setup_var.settings['fn']+                  \
                        '_bdytide_'+const_name+'_grd_'+            \
                        val['nam'].upper()+'.nc'
            
            nemo_bdy_tide_ncgen.CreateBDYTideNetcdfFile(fout_tide, 
                            val['nx'], 
                            dst_coord_var.lonlat['t']['lon'].shape[1],
                            dst_coord_var.lonlat['t']['lon'].shape[0], 
                            val['des']+tide_con, 
                            setup_var.settings['fv'], key.upper())
            
            ncpop.write_data_to_file(fout_tide, val['nam']+'1', 
                                     cons['cos'][val['nam']][indx])
            ncpop.write_data_to_file(fout_tide, val['nam']+'2', 
                                     cons['sin'][val['nam']][indx])
            ncpop.write_data_to_file(fout_tide, 'bdy_msk',
                                     dst_coord_var.bdy_msk)
            ncpop.write_data_to_file(fout_tide, 'nav_lon',
                                     dst_coord_var.lonlat['t']['lon'])
            ncpop.write_data_to_file(fout_tide, 'nav_lat',
                                     dst_coord_var.lonlat['t']['lat'])
            ncpop.write_data_to_file(fout_tide, 'nbidta',
                                     grid[key].bdy_i[val['ind'], 0]+1)
            ncpop.write_data_to_file(fout_tide, 'nbjdta',
                                     grid[key].bdy_i[val['ind'], 1]+1)
            ncpop.write_data_to_file(fout_tide, 'nbrdta',
                                     grid[key].bdy_r[val['ind']]+1)
        
        # Iterate over constituents
        
        indx += 1

def _get_mask(Setup, mask_gui):
    """ 
    Read mask information from file or open GUI.

    This method reads the mask information from the netcdf file or opens a gui
    to create a mask depending on the mask_gui input. The default mask data 
    uses the bathymetry and applies a 1pt halo.

    Args:
        Setup    (list): settings for bdy
        mask_gui (bool): whether use of the GUI is required

    Returns:
        numpy.array     : a mask array of the regional domain
    """
    # Initialise bdy_msk array
    
    bdy_msk = None
    
    if mask_gui: # Do we activate the GUI
        
        # TODO: I do not like the use of _ for a dummy variable - better way?
        
        _, mask = pynemo_settings_editor.open_settings_dialog(Setup)
        bdy_msk = mask.data
        Setup.refresh()
        logger.info('Using GUI defined mask')
    else: # Try an read mask from file
        try:
            if (Setup.bool_settings['mask_file'] and 
                Setup.settings['mask_file'] is not None):
                mask = Mask_File(Setup.settings['bathy'], 
                                 Setup.settings['mask_file'])
                bdy_msk = mask.data
                logger.info('Using input mask file')
            elif Setup.bool_settings['mask_file']:
                logger.error('Mask file is not given')
                return
            else: # No mask file specified then use default 1px halo mask
                logger.warning('Using default mask with bathymetry!!!!')
                mask = Mask_File(Setup.settings['bathy'])
                mask.apply_border_mask(Constants.DEFAULT_MASK_PIXELS)
                bdy_msk = mask.data
        except:
            return
    
    if np.amin(bdy_msk) == 0: # Mask is not set, so set border to 1px
        logger.warning('Setting the mask to with a 1 grid point border')
        QMessageBox.warning(None,'NRCT', 'Mask is not set, setting a 1 grid '+
                                         'point border mask')
        if (bdy_msk is not None and 1 < bdy_msk.shape[0] and 
            1 < bdy_msk.shape[1]):
            tmp = np.ones(bdy_msk.shape, dtype=bool)
            tmp[1:-1, 1:-1] = False
            bdy_msk[tmp] = -1
            
    return bdy_msk
