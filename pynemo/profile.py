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
from PyQt4.QtGui import QMessageBox

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
from pynemo.utils import Constants
from pynemo.gui.nemo_bdy_mask import Mask as Mask_File

from pynemo import nemo_bdy_dl_cmems as dl_cmems
from calendar import monthrange

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
    
    logger.info('Start NRCT Logging: '+time.asctime())
    logger.info('============================================')

    Setup = setup.Setup(setup_filepath) # default settings file
    settings = Setup.settings

    # download CMEMS data if requested
    
    if settings['use_cmems'] == True:
        
        logger.info('starting CMEMS download process....')
 
        if settings['year_end'] - settings['year_000'] > 0:
            date_min = settings['year_000']+'-01-01'
            date_max = settings['year_end']+'-12-31'
        
        days_mth = monthrange(settings['year_end'],settings['month_end'])
        
        date_min = str(settings['year_000'])+'-'+str(settings['month_000'])+'-01'
        
        date_max = str(settings['year_end'])+'-'+str(settings['month_end'])+'-'+str(days_mth[1])
        
        cmes_config= {
               'ini_config_template'    : settings['cmes_config_template'],
               'user'                   : settings['cmes_usr'],
               'pwd'                    : settings['cmes_pwd'],
               'motu_server'            : settings['motu_server'],  
               'service_id'             : settings['cmes_model'],
               'product_id'             : settings['cmes_product'],
               'date_min'               : date_min,
               'date_max'               : date_max,
               'latitude_min'           : settings['latitude_min'],
               'latitude_max'           : settings['latitude_max'],
               'longitude_min'          : settings['longitude_min'],
               'longitude_max'          : settings['longitude_max'],
               'depth_min'              : settings['depth_min'],
               'depth_max'              : settings['depth_max'],
               'variable'               : settings['cmes_variable'],
               'out_dir'                : settings['dst_dir'],
               'out_name'               : settings['cmes_output'],
               'config_out'             : settings['cmes_config']
               }        
        
        chk = dl_cmems.chk_motu()
        
        if chk == 1:
            logger.error('motuclient not installed, please install by running $ pip install motuclient')
            
        else:
            logger.info('version ' +chk+ ' of motuclient is installed')
        logger.info('requesting CMES download now (this can take a while)...')    
        dl = dl_cmems.request_CMEMS(cmes_config)
        
        if dl == 0:
            logger.info('CMES data downloaded successfully')
            
        if type(dl) == str:
            logger.error(dl)

    SourceCoord = source_coord.SourceCoord()
    DstCoord    = dst_coord.DstCoord()

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
    SourceCoord.zt = np.squeeze(nc['gdept_0'][:])
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

    nc = GetFile(settings['src_hgr'])
    SourceCoord.lon = nc['glamt'][:,:]
    SourceCoord.lat = nc['gphit'][:,:]
    
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
            cons = tide.nemo_bdy_tpx7p2_rot(
                Setup, DstCoord, bdy_ind['t'], bdy_ind['u'], bdy_ind['v'],
                                                            settings['clname'])
        elif settings['tide_model']=='fes':
            logger.error('Tidal model: %s, not yet implimented', 
                         settings['tide_model'])
            return
        else:
            logger.error('Tidal model: %s, not recognised', 
                         settings['tide_model'])
            return
            
        write_tidal_data(Setup, DstCoord, bdy_ind, settings['clname'], cons)

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
    
    yrs = range(yr_000, yr_end+1)
    
    if yr_end - yr_000 >= 1:
        if range(mn_000, mn_end+1) < 12:
            logger.info('Warning: All months will be extracted as the number '+
                        'of years is greater than 1')
        mns = range(1,13)
    else:
        mn_000 = settings['month_000']
        mn_end = settings['month_end']
        if mn_end > 12 or mn_000 < 1:
            logging.error('Please check the nn_month_000 and nn_month_end '+
                          'values in input bdy file')
            return
        mns = range(mn_000, mn_end+1)
    
    # Enter the loop for each year and month extraction
    
    logger.info('Entering extraction loop')
    
    ln_dyn2d   = settings['dyn2d']            
    ln_dyn3d   = settings['dyn3d'] # are total or bc velocities required
    ln_tra     = settings['tra']          
    ln_ice     = settings['ice']   

    # Define mapping of variables to grids with a dictionary
    
    emap = {}
    grd  = [  't',  'u',  'v']
    pair = [ None, 'uv', 'uv'] # TODO: devolve this to the namelist?
    
    # TODO: The following is a temporary stop gap to assign variables. In 
    # future we need a slicker way of determining the variables to extract. 
    # Perhaps by scraping the .ncml file - this way biogeochemical tracers
    # can be included in the ln_tra = .true. option without having to
    # explicitly declaring them.

    var_in = {}
    for g in range(len(grd)):
        var_in[grd[g]] = []
        
    if ln_tra:
        var_in['t'].extend(['votemper', 'vosaline'])
        
    if ln_dyn2d or ln_dyn3d:
        var_in['u'].extend(['vozocrtx', 'vomecrty'])
        var_in['v'].extend(['vozocrtx', 'vomecrty'])
    
    if ln_dyn2d:
        var_in['t'].extend(['sossheig'])
        
    if ln_ice:
        var_in['t'].extend(['ice1', 'ice2', 'ice3'])
    
    # As variables are associated with grd there must be a filename attached
    # to each variable
    
    for g in range(len(grd)):
        
        if len(var_in[grd[g]])>0:
            emap[grd[g]]= {'variables': var_in[grd[g]],
                           'pair'     : pair[g]} 

    extract_obj = {}
    
    # Initialise the mapping indices for each grid 
    
    for key, val in emap.items():
        
        extract_obj[key] = extract.Extract(Setup.settings, 
                                           SourceCoord, DstCoord,
                                           bdy_ind, val['variables'], 
                                           key, val['pair'])
    
    # TODO: Write the nearest neighbour parent grid point to each bdy point
    #       possibly to the coordinates.bdy.nc file to help with comparison
    #       plots later.
        
    for year in yrs:
        for month in mns:
            for key, val in emap.items():
                
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

        for key,val in tmap.items():
            
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
