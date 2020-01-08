##############################################
# Generates Depth information                #
# #                                        # #
# Written by John Kazimierz Farey, Sep 2012  #
# Port of Matlab code of James Harle         #
##############################################
"""
# NOTES:
# I have skipped error check code

# Generates depth points for t, u and v in one loop iteration

Initialise with bdy t, u and v grid attributes (Grid.bdy_i)
and settings dictionary 
"""

from .reader.factory import GetFile
import numpy as np
import logging

from .utils.nemo_bdy_lib import sub2ind
from .utils.e3_to_depth import e3_to_depth
#     pylint: disable=E1101
# Query name
class Depth:

    def __init__(self, bdy_t, bdy_u, bdy_v, settings):
        self.logger = logging.getLogger(__name__) 
        self.logger.debug( 'init Depth' )
        hc = settings['hc'] 
        nc = GetFile(settings['dst_zgr'])#Dataset(settings['dst_zgr'], 'r')
        mbathy = nc['mbathy'][:,:,:].squeeze() #nc.variables['mbathy'][:,:,:].squeeze()
        # numpy requires float dtype to use NaNs
        mbathy = np.float16(mbathy)
        mbathy[mbathy == 0] = np.NaN 
        nz = len(nc['nav_lev'][:])#.variables['nav_lev'][:])

        # Set up arrays
        t_nbdy = len(bdy_t[:,0])
        u_nbdy = len(bdy_u[:,0])
        v_nbdy = len(bdy_v[:,0])
        zp = ['t', 'wt', 'u', 'wu', 'v', 'wv']
        self.zpoints = {}
        for z in zp:
            if 't' in z:
                nbdy = t_nbdy
            elif 'u' in z:
                nbdy = u_nbdy
            elif 'v' in z:
                nbdy = v_nbdy
            self.zpoints[z] = np.zeros((nz, nbdy))

        # Check inputs
        # FIX ME? Errors for wrong obj arg len. probably better to work around
        if settings['sco']:
            # hc = ... FIX ME??
            # Depth of water column at t-point
            hbatt = nc['hbatt'][:,:,:]#nc.variables['hbatt'][:,:,:]
            # Replace land with NaN   
            hbatt[mbathy == 0] = np.NaN

        # find bdy indices from subscripts
        t_ind = sub2ind(mbathy.shape, bdy_t[:,0], bdy_t[:,1])
        
        u_ind = sub2ind(mbathy.shape, bdy_u[:,0], bdy_u[:,1])
        u_ind2 = sub2ind(mbathy.shape, bdy_u[:,0] + 1, bdy_u[:,1])

        v_ind = sub2ind(mbathy.shape, bdy_v[:,0], bdy_v[:,1])
        v_ind2 = sub2ind(mbathy.shape, bdy_v[:,0], bdy_v[:,1] + 1) 
   
    	[tmp_zt, tmp_zw] = e3_to_depth(np.squeeze(nc['e3t'][:,:,:,:]), np.squeeze(nc['e3w'][:,:,:,:]), nz)
        # This is very slow
        self.logger.debug( 'starting nc reads loop' )
        for k in range(nz):
            if settings['sco']:
                # sigma coeffs at t-point (1->0 indexed)
                gsigt = nc['gsigt'][0,k,:,:]#nc.variables['gsigt'][0,k,:,:]
                # sigma coeffs at w-point
                gsigw = nc['gsigw'][0,k,:,:]#nc.variables['gsigw'][0,k,:,:]

                # NOTE:  check size of gsigt SKIPPED

                wrk1 = (hbatt - hc) * gsigt[:,:] + (hc * (k + 0.5) / (nz - 1))
                wrk2 = (hbatt - hc) * gsigw[:,:] + (hc * (k + 0.5) / (nz - 1))
            else:
		# jelt: replace 'load gdep[wt] with load e3[tw] and compute gdep[tw]
                #wrk1 = nc['gdept'][0,k,:,:]#nc.variables['gdept'][0,k,:,:]
                #wrk2 = nc['gdepw'][0,k,:,:]#nc.variables['gdepw'][0,k,:,:]
                #print 'e3t shape: ', nc['e3t_0'][:].shape
                [wrk1, wrk2] = tmp_zt[k,:,:], tmp_zw[k,:,:] 

            # Replace deep levels that are not used with NaN
            wrk2[mbathy + 1 < k + 1] = np.NaN
            wrk1[mbathy < k + 1] = np.NaN

            # Set u and v grid point depths
            zshapes = {}
            for p in list(self.zpoints.keys()):
                zshapes[p] = self.zpoints[p].shape
            wshapes = []
            wshapes.append(wrk1.shape)
            wshapes.append(wrk2.shape)
            wrk1, wrk2 = wrk1.flatten(1), wrk2.flatten(1)

            self.zpoints['t'][k,:]  = wrk1[t_ind]
            self.zpoints['wt'][k,:] = wrk2[t_ind]
            
            self.zpoints['u'][k,:]  = 0.5 * (wrk1[u_ind] + wrk1[u_ind2])
            self.zpoints['wu'][k,:] = 0.5 * (wrk2[u_ind] + wrk2[u_ind2])
            
            self.zpoints['v'][k,:]  = 0.5 * (wrk1[v_ind] + wrk1[v_ind2])
            self.zpoints['wv'][k,:] = 0.5 * (wrk2[v_ind] + wrk2[v_ind2])

            for p in list(self.zpoints.keys()):
                self.zpoints[p] = self.zpoints[p].reshape(zshapes[p])
            
        self.logger.debug( 'Done loop, zpoints: %s ', self.zpoints['t'].shape)
                                

        nc.close()

            


