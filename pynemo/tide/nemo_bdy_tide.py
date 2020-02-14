'''



'''
import numpy as np
import scipy.spatial as sp
from netCDF4 import Dataset
import copy # DEBUG ONLY- allows multiple runs without corruption
import nemo_bdy_grid_angle
#from nemo_bdy_extr_tm3 import rot_rep

class Extract:

    def __init__(self, setup, DstCoord, Grid):

        self.g_type = Grid.grid_type
        DC = copy.deepcopy(DstCoord)
        dst_lon = DC.bdy_lonlat[self.g_type]['lon'][Grid.bdy_r == 0]
        dst_lat = DC.bdy_lonlat[self.g_type]['lat'][Grid.bdy_r == 0]
        self.dst_dep = DC.depths[self.g_type]['bdy_hbat'][Grid.bdy_r == 0]
        self.harm_Im = {} # tidal boundary data: Imaginary
        self.harm_Re = {} # tidal boundary data: Real
        
        # Modify lon for 0-360 TODO this needs to be auto-dectected
        
        dst_lon = np.array([x if x > 0 else x+360 for x in dst_lon])
      
        fileIDb = '/Users/jdha/Projects/pynemo_data/DATA/grid_tpxo7.2.nc' # TPX bathymetry file
        nb = Dataset(fileIDb) # Open the TPX bathybetry file using the NetCDF4-Python library

        # Open the TPX Datafiles using the NetCDF4-Python library
#            T_GridAngles = nemo_bdy_grid_angle.GridAngle(
#                       self.settings['src_hgr'], imin, imax, jmin, jmax, 't')
#            RotStr_GridAngles = nemo_bdy_grid_angle.GridAngle(
#                         self.settings['dst_hgr'], 1, maxI, 1, maxJ, self.rot_str)
            
#            self.gcos = T_GridAngles.cosval
#            self.gsin = T_GridAngles.sinval
            
        if self.g_type == 't':    
            self.fileID = '/Users/jdha/Projects/pynemo_data/DATA/h_tpxo7.2.nc' # TPX sea surface height file
            self.var_Im = 'hIm' 
            self.var_Re = 'hRe' 
            nc = Dataset(self.fileID) # pass variable ids to nc
            lon = np.ravel(nc.variables['lon_z'][:,:]) # need to add in a east-west wrap-around
            lat = np.ravel(nc.variables['lat_z'][:,:])
            bat = np.ravel(nb.variables['hz'][:,:])
            msk = np.ravel(nb.variables['mz'][:,:])
        elif self.g_type == 'u':
            self.fileID = '/Users/jdha/Projects/pynemo_data/DATA/u_tpxo7.2.nc' # TPX velocity file
            self.var_Im = 'UIm' 
            self.var_Re = 'URe' 
            self.key_tr = setup['tide_trans']
            nc = Dataset(self.fileID) # pass variable ids to nc
            lon = np.ravel(nc.variables['lon_u'][:,:])
            lat = np.ravel(nc.variables['lat_u'][:,:])
            bat = np.ravel(nb.variables['hu'][:,:])
            msk = np.ravel(nb.variables['mu'][:,:])
        else:
            self.fileID = '/Users/jdha/Projects/pynemo_data/DATA/u_tpxo7.2.nc' # TPX velocity file
            self.var_Im = 'VIm' 
            self.var_Re = 'VRe' 
            self.key_tr = setup['tide_trans']
            nc = Dataset(self.fileID) # pass variable ids to nc
            lon = np.ravel(nc.variables['lon_v'][:,:])
            lat = np.ravel(nc.variables['lat_v'][:,:]) 
            bat = np.ravel(nb.variables['hv'][:,:])
            msk = np.ravel(nb.variables['mv'][:,:])
              
        # Pull out the constituents that are avaibable
        self.cons = []
        for ncon in range(nc.variables['con'].shape[0]):
            self.cons.append(nc.variables['con'][ncon,:].tostring().strip())
                        
        nc.close() # Close Datafile
        nb.close() # Close Bathymetry file

        # Find nearest neighbours on the source grid to each dst bdy point
        source_tree = sp.cKDTree(list(zip(lon, lat)))
        dst_pts = list(zip(dst_lon, dst_lat))
        nn_dist, self.nn_id = source_tree.query(dst_pts, k=4, eps=0, p=2, 
                                                distance_upper_bound=0.5)
        
        # Create a weighting index for interpolation onto dst bdy point 
        # need to check for missing values
        
        ind = nn_dist == np.inf

        self.nn_id[ind] = 0  # better way of carrying None in the indices?      
        dx = (lon[self.nn_id] - np.repeat(np.reshape(dst_lon,[dst_lon.size, 1]),4,axis=1) ) * np.cos(np.repeat(np.reshape(dst_lat,[dst_lat.size, 1]),4,axis=1) * np.pi / 180.)
        dy =  lat[self.nn_id] - np.repeat(np.reshape(dst_lat,[dst_lat.size, 1]),4,axis=1)
        
        dist_tot = np.power((np.power(dx, 2) + np.power(dy, 2)), 0.5)

        self.msk = msk[self.nn_id]
        self.bat = bat[self.nn_id]
        
        dist_tot[ind | self.msk] = np.nan
        
        dist_wei = 1/( np.divide(dist_tot,(np.repeat(np.reshape(np.nansum(dist_tot,axis=1),[dst_lat.size, 1]),4,axis=1)) ) )
        
        self.nn_wei = dist_wei/np.repeat(np.reshape(np.nansum(dist_wei, axis=1),[dst_lat.size, 1]),4,axis=1)       
        self.nn_wei[ind | self.msk] = 0.
        
        # Need to identify missing points and throw a warning and set values to zero
        
        mv = np.sum(self.wei,axis=1) == 0
        print('##WARNING## There are', np.sum(mv), 'missing values, these will be set to ZERO')
        
    def extract_con(self, con):        
        
        if con in self.cons:
            con_ind = self.cons.index(con)
            
            # Extract the complex amplitude components
            
            nc = Dataset(self.fileID) # pass variable ids to nc
            
            vIm = np.ravel(nc.variables[self.var_Im][con_ind,:,:])
            vRe = np.ravel(nc.variables[self.var_Re][con_ind,:,:])
        
            nc.close()
            
            if self.g_type != 't':
                
                self.harm_Im[con] = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)
                self.harm_Re[con] = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)
            
            else: # Convert transports to velocities
                
                if self.key_tr == True: # We convert to velocity using tidal model bathymetry
                
                    self.harm_Im[con] = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat[self.nn_id]*self.nn_wei,axis=1)
                    self.harm_Re[con] = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat[self.nn_id]*self.nn_wei,axis=1)
      
                else: # We convert to velocity using the regional model bathymetry
                
                    self.harm_Im[con] = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
                    self.harm_Re[con] = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
      
                
                # Rotate vectors
            
                self.harm_Im_rot[con] = self.rot_rep(self.harm_Im[con], self.harm_Im[con], self.rot_str,
                                      'en to %s' %self.rot_dir, self.dst_gcos, self.dst_gsin)
                self.harm_Re_rot[con] = self.rot_rep(self.harm_Re[con], self.harm_Re[con], self.rot_str,
                                      'en to %s' %self.rot_dir, self.dst_gcos, self.dst_gsin)
                                      
        else:
            
            # throw some warning
            print('##WARNING## Missing constituent values will be set to ZERO')
        
            self.harm_Im[con] = np.zeros(self.nn_id[:,0].size)
            self.harm_Re[con] = np.zeros(self.nn_id[:,0].size)
            




