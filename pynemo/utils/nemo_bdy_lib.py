"""
 Library of some functions used by multiple classes
 Written by John Kazimierz Farey, Sep 2012
"""
import scipy.spatial as sp
import numpy as np

def sub2ind(shap, subx, suby):
    """subscript to index of a 1d array"""
    ind = (subx * shap[0]) + suby
    return ind

def rot_rep(pxin, pyin, dummy, cd_todo, gcos, gsin):
    """rotate function"""
    if cd_todo.lower() == 'en to i':
        x_var, y_var = pxin, pyin
    elif cd_todo.lower() == 'en to j':
        x_var, y_var = pyin, pxin*-1
    elif cd_todo.lower() == 'ij to e':
        x_var, y_var = pxin, pyin*-1
    elif cd_todo.lower() == 'ij to n':
        x_var, y_var = pyin, pxin
    else:
        raise SyntaxError('rot_rep cd_todo %s is invalid' %cd_todo)
    return x_var * gcos + y_var * gsin

def get_output_filename(setup_var, year, month, var_type):
    """This returns a output filename constructed for a given var_type, year and month"""
    if var_type == 'ice':
        return setup_var.settings['dst_dir']+setup_var.settings['fn']+'_bdyT_y'+str(year)+ \
               'm'+str(month)+'.nc'
    elif var_type == 'bt':
        return setup_var.settings['dst_dir']+setup_var.settings['fn']+'_bt_bdyT_y'+str(year)+ \
               'm'+str(month)+'.nc'
    elif var_type == 'u':
        return setup_var.settings['dst_dir'] + setup_var.settings['fn'] + '_bdyU_y' + \
               str(year) + 'm' + str(month) + '.nc'
    elif var_type == 'v':
        return setup_var.settings['dst_dir'] + setup_var.settings['fn'] + '_bdyV_y' + \
               str(year) + 'm' + str(month) + '.nc'

def get_output_tidal_filename(setup_var, const_name, grid_type):
    """This method returns a output filename constructed for a given tidal constituent and
    grid type"""
    return setup_var.settings['dst_dir']+setup_var.settings['fn']+"_bdytide_rotT_"+const_name+ \
           "_grid_"+grid_type.upper()+".nc"

def psi_field(U, V):
    psiu = np.cumsum(U[1:,:], axis=0) - np.cumsum(V[0,:])
    psiv = ( np.cumsum(U[:,0]) - np.cumsum(V[:,1:], axis=1).T ).T
    return psiu[:,1:], psiv[1:,:]

def velocity_field(psi):
    U = np.diff(psi, n=1, axis=0)
    V = - np.diff(psi, n=1, axis=1)
    return U, V

def bdy_sections(nbidta,nbjdta,nbrdta,rw):
    """Extract individual byd sections

    Keyword arguments:
    """
    
    # TODO Need to put a check in here to STOP if we have E-W wrap
    # as this is not coded yet
    
    # Define the outer most halo
    outer_rim_i = nbidta[nbrdta==rw]
    outer_rim_j = nbjdta[nbrdta==rw]

    # Set initial constants

    nbdy = len(outer_rim_i)
    count = 0
    flag = 0
    mark = 0
    source_tree = sp.cKDTree(list(zip(outer_rim_i, outer_rim_j))) 
    id_order = np.ones((nbdy,), dtype=np.int)*source_tree.n
    id_order[count] = 0 # use index 0 as the starting point 
    count += 1
    end_pts = {}
    nsec = 0
    
    # Search for individual sections and order

    while count <= nbdy:
        
        lcl_pt = list(zip([outer_rim_i[id_order[count-1]]],
                     [outer_rim_j[id_order[count-1]]]))
        junk, an_id = source_tree.query(lcl_pt, k=3, distance_upper_bound=1.1)
        
        if an_id[0,1] in id_order:
            if (an_id[0,2] in id_order) or (an_id[0,2] == source_tree.n) : # we are now at an end point and ready to sequence a section
                if flag == 0:
                    flag = 1  
                    end_pts[nsec] = [id_order[count-1], id_order[count-1]] # make a note of the starting point
                    id_order[mark] = id_order[count-1]
                    id_order[mark+1:] = source_tree.n # remove previous values
                    count = mark + 1
                else:
                    i = 0
                    end_pts[nsec][1] = id_order[count-1] # update the end point of the section
                    nsec += 1
                    
                    while i in id_order:
                        i += 1
                        
                    if count < nbdy:
                        id_order[count] = i
                    flag = 0
                    mark = count
                    count += 1

            else: # lets add the next available point to the sequence
                id_order[count] = an_id[0,2]
                count += 1

        else: # lets add the next available point to the sequence
            id_order[count] = an_id[0,1]
            count += 1
        
    return id_order, end_pts
    
def bdy_transport():
    """Calculate transport across individual bdy sections

    Keyword arguments:
    """
    raise NotImplementedError
    
