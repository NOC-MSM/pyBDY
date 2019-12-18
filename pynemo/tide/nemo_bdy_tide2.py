'''



'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
import numpy as np
import scipy.spatial as sp
from netCDF4 import Dataset
import copy # DEBUG ONLY- allows multiple runs without corruption
from pynemo import nemo_bdy_grid_angle
from pynemo.nemo_bdy_lib import rot_rep


"
import foo
method_to_call = getattr(foo, 'bar')
result = method_to_call()
You could shorten lines 2 and 3 to:

result = getattr(foo, 'bar')()
"


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
      
        fileIDb = '../data/tide/grid_tpxo7.2.nc' # TPX bathymetry file
        nb = Dataset(fileIDb) # Open the TPX bathybetry file using the NetCDF4-Python library

        # Open the TPX Datafiles using the NetCDF4-Python library
            
        if self.g_type == 't':    
            self.fileID = '../data/tide/h_tpxo7.2.nc' # TPX sea surface height file
            self.var_Im = 'hIm' 
            self.var_Re = 'hRe' 
        elif (self.g_type == 'u') or (self.g_type == 'v') :
            self.fileID = '../data/tide/u_tpxo7.2.nc' # TPX velocity file
            self.var_Im = 'UIm' 
            self.var_Re = 'URe' 
            self.var_Im2 = 'VIm' 
            self.var_Re2 = 'VRe' 
            self.key_tr = setup['trans']
            
            # Determine the grid angle for rotating vector qunatities
            maxJ = DC.lonlat['t']['lon'].shape[0]
            maxI = DC.lonlat['t']['lon'].shape[1]
            GridAngles = nemo_bdy_grid_angle.GridAngle(setup['dst_hgr'], 1, maxI, 1, maxJ, self.g_type)
            dst_gcos = np.ones([maxJ, maxI])
            dst_gsin = np.zeros([maxJ,maxI])            
            dst_gcos[1:,1:] = GridAngles.cosval
            dst_gsin[1:,1:] = GridAngles.sinval

            # Retain only boundary points rotation information
            self.gcos = np.zeros(Grid.bdy_i.shape[0])
            self.gsin = np.zeros(Grid.bdy_i.shape[0])
            for p in range(Grid.bdy_i.shape[0]):
                self.gcos[p] = dst_gcos[Grid.bdy_i[p,1], Grid.bdy_i[p,0]]
                self.gsin[p] = dst_gsin[Grid.bdy_i[p,1], Grid.bdy_i[p,0]]
            
            if self.g_type == 'u':
                self.rot_dir = 'i'
            elif self.g_type == 'v':
                self.rot_dir = 'j'
        else:
            print 'You should not see this message!'
              
        # We will average velocities onto the T grid as there is a rotation to be done 
        # Also need to account for east-west wrap-around
        nc = Dataset('../data/tide/h_tpxo7.2.nc')
        lon = np.ravel(np.concatenate([nc.variables['lon_z'][-2:,:], 
                                       nc.variables['lon_z'][:,:], 
                                       nc.variables['lon_z'][0:2,:]]))
        lat = np.ravel(np.concatenate([nc.variables['lat_z'][-2:,:], 
                                       nc.variables['lat_z'][:,:], 
                                       nc.variables['lat_z'][0:2,:]]))
        bat = np.ravel(np.concatenate([nb.variables['hz'][-2:,:], 
                                       nb.variables['hz'][:,:], 
                                       nb.variables['hz'][0:2,:]]))
        msk = np.ravel(np.concatenate([nb.variables['mz'][-2:,:], 
                                       nb.variables['mz'][:,:], 
                                       nb.variables['mz'][0:2,:]]))
     
        # Pull out the constituents that are avaibable
        self.cons = []
        for ncon in range(nc.variables['con'].shape[0]):
            self.cons.append(nc.variables['con'][ncon,:].tostring().strip())
                        
        nc.close() # Close Datafile
        nb.close() # Close Bathymetry file

        # Find nearest neighbours on the source grid to each dst bdy point
        source_tree = sp.cKDTree(zip(lon, lat))
        dst_pts = zip(dst_lon, dst_lat)
        # Upper bound set at 0.5 deg as the TPXO7.2 data are at 0.25 deg resolution and 
        # we don't want to grab points from further afield
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
        
        mv = np.sum(self.nn_wei,axis=1) == 0
        if np.sum(mv) > 1:
            print '##WARNING## There are', np.sum(mv), 'missing values, these will be set to ZERO'
        else:
            print '##WARNING## There is', np.sum(mv), 'missing value, this will be set to ZERO'
        
    def extract_con(self, con):        
        
        if con in self.cons:
            con_ind = self.cons.index(con)
            
            # Extract the complex amplitude components
            nc = Dataset(self.fileID) # pass variable ids to nc
            
            if self.g_type == 't':
                
                
                vIm = np.ravel(np.concatenate([nc.variables[self.var_Im][con_ind,-2:,:],
                                               nc.variables[self.var_Im][con_ind,:,:],
                                               nc.variables[self.var_Im][con_ind,0:2,:]]))
                vRe = np.ravel(np.concatenate([nc.variables[self.var_Re][con_ind,-2:,:],
                                               nc.variables[self.var_Re][con_ind,:,:],
                                               nc.variables[self.var_Re][con_ind,0:2,:]]))
        
                self.harm_Im[con] = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)
                self.harm_Re[con] = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)
            
            else: 
                
                uIm = np.concatenate([nc.variables[self.var_Im][con_ind,-2:,:],
                                      nc.variables[self.var_Im][con_ind,:,:],
                                      nc.variables[self.var_Im][con_ind,0:3,:]])
                uRe = np.concatenate([nc.variables[self.var_Re][con_ind,-2:,:],
                                      nc.variables[self.var_Re][con_ind,:,:],
                                      nc.variables[self.var_Re][con_ind,0:3,:]])
                                               
                vIm = np.concatenate([nc.variables[self.var_Im2][con_ind,-2:,:],
                                      nc.variables[self.var_Im2][con_ind,:,:],
                                      nc.variables[self.var_Im2][con_ind,0:2,:]])
                vRe = np.concatenate([nc.variables[self.var_Re2][con_ind,-2:,:],
                                      nc.variables[self.var_Re2][con_ind,:,:],
                                      nc.variables[self.var_Re2][con_ind,0:2,:]])
                # Deal with north pole. NB in TPXO7.2 data U and Z at 90N have different
                # values for each Longitude value! Plus there's something odd with the 
                # hu and hv depths not being the min of surrounding T-grid depths
                # TODO remove hardwired 722 index point and make generic
                vIm = np.concatenate([vIm[:,:], np.concatenate([vIm[722:,-1],vIm[:722,-1]])[:,np.newaxis]],axis=1)
                vRe = np.concatenate([vRe[:,:], np.concatenate([vRe[722:,-1],vRe[:722,-1]])[:,np.newaxis]],axis=1)
                                      
                # Average U and V onto the T-grid
                                      
                uIm = np.ravel((uIm[:-1,:] + uIm[1:,:])/2)
                uRe = np.ravel((uRe[:-1,:] + uRe[1:,:])/2)
                vIm = np.ravel((vIm[:,:-1] + vIm[:,1:])/2)
                vRe = np.ravel((vRe[:,:-1] + vRe[:,1:])/2)
                
                if self.key_tr: # We convert to velocity using tidal model bathymetry
                
                    harm_Im = np.sum(uIm[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat*self.nn_wei,axis=1)
                    harm_Re = np.sum(uRe[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat*self.nn_wei,axis=1)
                    harm_Im2 = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat*self.nn_wei,axis=1)
                    harm_Re2 = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)/np.sum(self.bat*self.nn_wei,axis=1)
      
                else: # We convert to velocity using the regional model bathymetry
                
                    harm_Im = np.sum(uIm[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
                    harm_Re = np.sum(uRe[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
                    harm_Im2 = np.sum(vIm[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
                    harm_Re2 = np.sum(vRe[self.nn_id]*self.nn_wei,axis=1)/self.dst_dep
      
                
                # Rotate vectors
            
                self.harm_Im[con] = rot_rep(harm_Im, harm_Im2, self.g_type,
                                      'en to %s' %self.rot_dir, self.gcos, self.gsin)
                self.harm_Re[con] = rot_rep(harm_Re, harm_Re2, self.g_type,
                                      'en to %s' %self.rot_dir, self.gcos, self.gsin)
                self.harm_Im[con][self.msk]=0.
                self.harm_Re[con][self.msk]=0.
              
            nc.close()
                                    
        else:
            
            # throw some warning
            print '##WARNING## Missing constituent values will be set to ZERO'
        
            self.harm_Im[con] = np.zeros(self.nn_id[:,0].size)
            self.harm_Re[con] = np.zeros(self.nn_id[:,0].size)
            




