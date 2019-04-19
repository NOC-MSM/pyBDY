'''
funtion e3_to_depth
Purpose :   compute t- & w-depths of model levels from e3t & e3w scale factors
Method  :   The t- & w-depth are given by the summation of e3w & e3t, resp.
Action  :   pe3t, pe3w : scale factor of t- and w-point (m)
Useage: [gdept, gdepw] = e3_to_depth(e3t, e3w, nz)
'''

import numpy as np
## COMMENT(jelt 5Feb18). Since the move from NEMOv3.6 to NEMOv4 we now need to compute the depth variables from e3[tw] metrics
## Older namelist_dst.ncml files did not have an e3w definition. This is now needed to reconstruct depth at w-points
## However if e3w isn't defined in the *ncml file it is likely that PyNEMO will fail here.
def e3_to_depth(pe3t, pe3w, jpk):
  pdepw      = np.zeros_like(pe3w)
  pdepw[0,:] = 0.
  pdept      = np.zeros_like(pe3t)
  pdept[0,:] = 0.5 * pe3w[0,:]

  for jk in np.arange(1,jpk,1):
    pdepw[jk,:] = pdepw[jk-1,:] + pe3t[jk-1,:]
    pdept[jk,:] = pdept[jk-1,:] + pe3w[jk  ,:]

  return pdept, pdepw
