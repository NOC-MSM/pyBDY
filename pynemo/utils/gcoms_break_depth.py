'''
Rewritting the break depth implementation from matlab version

@author: Mr. Srikanth Nagella
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
import numpy as np
import math
import copy
import logging
#import pyproj

#import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
import seawater
def gcoms_break_depth(bathy):
    """ This creates a mask for the break depth using histograms """
    ocean_depth = bathy[...]
    ocean_depth = ocean_depth[ocean_depth > 0]

    depth_bin = 10.0    
    depth_max = np.max(ocean_depth)
    num_bin = int(math.floor(depth_max/depth_bin))

    # Compute the histogram of depth values over the whole Domain
    depth_vec = (np.arange(1,num_bin+1)+0.5)*depth_bin    
    histbat, dummy = np.histogram(ocean_depth, num_bin)
    max_hist_value_index = np.argmax(histbat)
    #z_smo = (max_hist_value_index * depth_bin)/2.0
    z_smo = 100.0
    nsmo = math.floor(z_smo/depth_bin)
#    print nsmo, z_smo, histbat.dtype
    #print max_hist_value_index
#    plt.subplot(211)
#    plt.hist(ocean_depth, num_bin) 
    #plt.show()
    hist_smooth = ndimage.uniform_filter(histbat.astype(float), int(nsmo)*2+1, mode='nearest')
#    print histbat.shape, dummy.shape
#    plt.subplot(212)
#    plt.bar(dummy[:-1],hist_smooth)
    
#    plt.show()
#    print histbat
#    print hist_smooth
    kshelf = -1
    kbreak = -1
    kplain = -1
    kfloor = -1
    histfloor = 0.0
    for depth_bin_index in range(0,num_bin-1): 
        if kshelf == -1:
            if hist_smooth[depth_bin_index] > hist_smooth[depth_bin_index+1]:
                kshelf = depth_bin_index;
        elif kbreak == -1:
            if hist_smooth[depth_bin_index] < hist_smooth[depth_bin_index+1]:
                kbreak = depth_bin_index
        elif kplain == -1:
            if hist_smooth[depth_bin_index] > hist_smooth[depth_bin_index+1]:
                kplain = depth_bin_index
                histfloor = hist_smooth[depth_bin_index]
    
    depth_shelf = depth_vec[kshelf]
    depth_break = depth_vec[kbreak]
    depth_plain = depth_vec[kplain]
#    print kshelf,kbreak,kplain
#    print 'Approximate depths: shelf=%sm, break=%sm, plain=%sm' % (depth_shelf,depth_break,depth_plain)
    h_max = math.floor(depth_break/100)*100
    return depth_shelf, h_max


def gcoms_boundary_masks(bathy,ov,lv):    
    """ 
    :param bathy: This is the input bathymetry data
    :param ov: Latittude array
    :param lv: Longitude array  
    :type bathy: numpy array
    :type ov: numpy array
    :type lv: numpy array
    :return: returns the ob, lb
    :rtype: numpy arrays
    
    :Example:
    """    
    tmp = np.pad(bathy, (1, 1), 'constant', constant_values=(np.NaN, np.NaN))
    tmp[tmp==ov] = np.NaN
    
    tmp1 = tmp[1:-1, :-2] + tmp[1:-1, 2:] + tmp[:-2, 1:-1] + tmp[2:, 1:-1]

    ob = np.logical_and(np.logical_and(np.isnan(tmp1), bathy != ov) , bathy != lv)
    
    tmp = np.pad(bathy, (1, 1), 'constant', constant_values=(-1,-1))
    tmp[tmp==lv] = np.NaN
    
    tmp1 = tmp[1:-1, :-2] + tmp[1:-1, 2:] + tmp[:-2, 1:-1] + tmp[2:, 1:-1]

    lb = np.logical_and(np.logical_and(np.isnan(tmp1), bathy!=ov), bathy!=lv)
    return ob, lb


def polcoms_select_domain(bathy, lat, lon, roi, dr):
    """ This calculates the shelf break
    :param bathy: This is the input bathymetry data
    :param lat: Latittude array
    :param lon: Longitude array
    :param roi: region of interest array [4]
    :param dr: shelf break distance
    :type bathy: numpy array
    :type lat: numpy array
    :type lon: numpy array
    :type roi: python array
    :type dr: float
    :return: returns the depth_shelf, h_max
    :rtype: numpy arrays
    
    :Example:
    """
    logger = logging.getLogger(__name__)
#   dy = 0.1
#   dx = 0.1
    
    #create a copy of bathy
    bathy_copy = bathy.copy()
#    bathy[bathy>=0] = 0;
#    bathy = bathy*-1
    global_ind = bathy_copy*np.NaN
#   r = np.ceil(dr/(np.pi/180*6400)/dy)
#   r = np.ceil(dr/(np.cos(np.radians(lat_ob[idx]))*np.pi*6400*2/360*dy))
#   if r > np.max(bathy_copy.shape):
#       logger.error("Shelf break is larger than the grid")
#        d1 = bathy_copy.shape[0]-(roi[3]-roi[2])/2.0
#        d2 = bathy_copy.shape[1]-(roi[1]-roi[0])/2.0
#        r = np.ceil(min(d1,d2))
        #just select the box roi
#       ret_val = np.ones(bathy.shape)
#       ret_val[roi[2]:roi[3],roi[0]:roi[1]] = -1
#       return ret_val == -1
        
    tmp = bathy_copy[roi[2]:roi[3],roi[0]:roi[1]]
    lat = lat[roi[2]:roi[3],roi[0]:roi[1]]
    lon = lon[roi[2]:roi[3],roi[0]:roi[1]]
    
    nanind = np.isnan(tmp) 
    tmp[nanind] = -1
    dummy, lb = gcoms_boundary_masks(tmp, -1,0)
    Zshelf, Hmax = gcoms_break_depth(tmp)
    tmp[tmp>Hmax] = -1
    tmp[np.logical_and(np.logical_and(tmp!=0, np.logical_not(np.isnan(tmp))), tmp!=-1)] = 1
    
    ob, dummy = gcoms_boundary_masks(tmp, -1, 0)
    
    lat_ob = np.ravel(lat,order='F')[np.ravel(ob,order='F')]
    lon_ob = np.ravel(lon,order='F')[np.ravel(ob,order='F')]
    
    
    print(lat_ob, lon_ob)
    len_lat = len(lat[:,0])
    len_lon = len(lon[0,:])
    lat_lon_index = np.nonzero( np.logical_and(lat == lat_ob[0], lon == lon_ob[0]))    
    for idx in range(0, len(lat_ob)):        
        lat_lon_index = np.nonzero( np.logical_and(lat == lat_ob[idx], lon == lon_ob[idx]))
        # messy fudge to determine local dx,dy TODO tidy and formalise
        j_0 = max(lat_lon_index[0],0)
        j_e = min(lat_lon_index[0]+1+1,len_lat)
        i_0 = max(lat_lon_index[1],0)
        i_e = min(lat_lon_index[1]+1+1,len_lon)
        if j_e>len_lat-2:
           j_0 = j_0 - 3
           j_e = j_0 + 2
        if i_e>len_lon-2:
           i_0 = i_0 - 3
           i_e = i_0 + 2
        lat_slice = slice(max(lat_lon_index[0],0),min(lat_lon_index[0]+1+1,len_lat))
        lon_slice = slice(max(lat_lon_index[1],0),min(lat_lon_index[1]+1+1,len_lon))   
        print('method2', lon_slice, lat_slice)
        lat_slice = slice(j_0,j_e)
        lon_slice = slice(i_0,i_e)
        print('method1', lon_slice, lat_slice)
        lat_pts = lat[lat_slice, lon_slice]
        lon_pts = lon[lat_slice, lon_slice]
        print(lat_pts, lon_pts)
        print(lat_lon_index[0], lat_lon_index[1]) 
        print(len_lon, len_lat, lat_lon_index[0], lat_lon_index[1])
        dy,py=seawater.dist(lat_pts[:,0], lon_pts[:,0])
        dx,px=seawater.dist(lat_pts[0,:], lon_pts[0,:])
        r = np.rint(np.ceil(dr/np.amax([dx,dy])))
        print(dx, dy, r)
        lat_slice = slice(max(lat_lon_index[0]-r,0),min(lat_lon_index[0]+r+1,len_lat))
        lon_slice = slice(max(lat_lon_index[1]-r,0),min(lat_lon_index[1]+r+1,len_lon))   
        lat_pts = lat[lat_slice, lon_slice]
        lon_pts = lon[lat_slice, lon_slice]
        lat_pts_shape = lat_pts.shape
        lat_pts = np.ravel(lat_pts)
        lon_pts = np.ravel(lon_pts)
        # NOTE: seawater package calculates the distance from point to the next point in the array
        # that is the reason to insert reference point before every point
        lat_pts = np.insert(lat_pts,list(range(0,len(lat_pts))), lat_ob[idx])
        lon_pts = np.insert(lon_pts,list(range(0,len(lon_pts))), lon_ob[idx])
        distance_pts = seawater.dist(lat_pts, lon_pts)
        #distances repeat themselves so only pick every alternative distance
        distance_pts = distance_pts[0][::2]
        
        #Using pyproj
        #geod = pyproj.Geod(ellps='WGS84')
        #dummy,dummy, distance_pts = geod.inv(len(lon_pts)*[lon_ob[idx]],len(lat_pts)*[lat_ob[idx]], lon_pts, lat_pts)
        #distance_pts=distance_pts/1000.0
                         
        distance_pts = np.reshape(distance_pts, lat_pts_shape)
        distance_pts[distance_pts>dr] = np.NaN
        distance_pts[np.logical_not(np.isnan(distance_pts))] = 1
        tmp1 = tmp[lat_slice, lon_slice]
        tmp1[np.logical_and(tmp1==-1, distance_pts==1)] = 1
        tmp[lat_slice, lon_slice] = tmp1
        
    lat_lb = lat[lb]
    lon_lb = lon[lb]
    
    for idx in range(0, len(lat_lb)):
        lat_lon_index = np.nonzero( np.logical_and(lat == lat_lb[idx], lon == lon_lb[idx]))
        # messy fudge to determine local dx,dy TODO tidy and formalise
        j_0 = max(lat_lon_index[0],0)
        j_e = min(lat_lon_index[0]+1+1,len_lat)
        i_0 = max(lat_lon_index[1],0)
        i_e = min(lat_lon_index[1]+1+1,len_lon)
        if j_e>len_lat-2:
           j_0 = j_0 - 3
           j_e = j_0 + 2
        if i_e>len_lon-2:
           i_0 = i_0 - 3
           i_e = i_0 + 2
        lat_slice = slice(max(lat_lon_index[0],0),min(lat_lon_index[0]+1+1,len_lat))
        lon_slice = slice(max(lat_lon_index[1],0),min(lat_lon_index[1]+1+1,len_lon))   
        print('method2', lon_slice, lat_slice)
        lat_slice = slice(j_0,j_e)
        lon_slice = slice(i_0,i_e)
        print('method1', lon_slice, lat_slice)
        lat_pts = lat[lat_slice, lon_slice]
        lon_pts = lon[lat_slice, lon_slice]
        print(lat_pts, lon_pts)
        print(lat_lon_index[0], lat_lon_index[1]) 
        print(len_lon, len_lat, lat_lon_index[0], lat_lon_index[1])
        dy,py=seawater.dist(lat_pts[:,0], lon_pts[:,0])
        dx,px=seawater.dist(lat_pts[0,:], lon_pts[0,:])
        r = np.rint(np.ceil(dr/np.amax([dx,dy])))
        print(dx, dy, r)
        lat_slice = slice(max(lat_lon_index[0]-r,0),min(lat_lon_index[0]+r+1,len_lat))
        lon_slice = slice(max(lat_lon_index[1]-r,0),min(lat_lon_index[1]+r+1,len_lon))   
        lat_pts = lat[lat_slice, lon_slice]
        lon_pts = lon[lat_slice, lon_slice]
        lat_pts_shape = lat_pts.shape
        lat_pts = np.ravel(lat_pts)
        lon_pts = np.ravel(lon_pts)
        # NOTE: seawater package calculates the distance from point to the next point in the array
        # that is the reason to insert reference point before every point
        lat_pts = np.insert(lat_pts,list(range(0,len(lat_pts))), lat_lb[idx])
        lon_pts = np.insert(lon_pts,list(range(0,len(lon_pts))), lon_lb[idx])
        distance_pts = seawater.dist(lat_pts, lon_pts)
        #distances repeat themselves so only pick every alternative distance
        distance_pts = distance_pts[0][::2]
        
        #Using pyproj
        #geod = pyproj.Geod(ellps='WGS84')
        #dummy,dummy, distance_pts = geod.inv(len(lon_pts)*[lon_lb[idx]],len(lat_pts)*[lat_lb[idx]], lon_pts, lat_pts) 
        #distance_pts=distance_pts/1000.0
        
        distance_pts = np.reshape(distance_pts, lat_pts_shape)
        distance_pts[distance_pts>dr] = np.NaN
        distance_pts[np.logical_not(np.isnan(distance_pts))] = 1
        tmp1 = tmp[lat_slice, lon_slice]
        tmp1[np.logical_and(tmp1==-1, distance_pts==1)] = 1
        tmp[lat_slice, lon_slice] = tmp1        
         
    #Only select largest sub region 
    tmp[nanind] = np.NaN
    ret_val = np.ones(bathy.shape)
    ret_val[roi[2]:roi[3],roi[0]:roi[1]] = tmp
    return ret_val == 1
    #in
         
    

    
