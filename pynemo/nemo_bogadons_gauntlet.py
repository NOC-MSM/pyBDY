#
# The loop from nemo_bdy_extr_tm3
#
# 
#

from calendar import monthrange
from datetime import datetime

from netCDF4 import Dataset, netcdftime


class Enter:

    def __init__(self, settings, sc_time, dir_list, dst_cal_type, year, month):

        var_nam = ['votemper', 'vosaline']
        sc_fields = source_fields

        #self.setup = settings # dict
        # define src/dst cals
        sf, ed = cal_trans(sc_time, dst_cal_type, year, month)
        # W
        DstCal = utime('seconds since %d-1-1' %year, dst_cal_type)
        dst_start = DstCal.date2num(datetime(year, month, 1))
        dst_end = DstCal.date2num(datetime(year, month, ed, 23, 59, 59))

        self.S_cal = utime(sc_time[0]['units'], sc_time[0]['calendar'])
        self.D_cal = utime('seconds since %d-1-1' %settings['year_000'], 
                           settings['dst_calendar'])

        for date in sc_time:
            date['date_num'] = DstCal.date2num(date['date']) * sf

        # Get first and last date within range
        first_date, last_date = None, None
        rev_seq = range(len_sc_time)
        rev_seq.reverse()
        # Multiple values.. might be broken.. 
        for date in rev_seq:
            if sc_time[date]['date_num'] < dst_start:
                first_date = date #number..
                break
        for date in range(len_sc_time):
            if sc_time[date]['date_num'] > dst_end:
                last_date = date
                break

        for date in range(first_date, last_date + 1):
            nc = Dataset(sc_time[date], 'r')
            if key_vec:
                pass
                #nc_2 = Dataset
                # FIX ME

            # We shouldnt have to worry about counters
            sc_bdy = np.zeros(nvar, sc_z_len, source_ind['ind'].shape[0],
                                  source_ind['ind'].shape[1])
            ind_vec = {}
            # distinctive variable name since it gets lost in the huge loop
            for shoggoth in range(nvar):
                varid = nc.variables[var_nam[shoggoth]]
                i, ii = source_ind['imin'], source_ind['imax']
                j, jj = source_ind['jmin'], source_ind['jmax']
                sc_arrays = []
                col_sc_arrays = []
                if key_vec:
                    varid_2 = nc_2.variables[var_nam[shoggoth + 1]]
                if not isslab and not key_vec:
                    # NOTE: 0 v 1 indexing may problemate
                    sc_arrays.append(varid[i-1:ii, j-1:jj, :sc_z_len, :1])
                elif key_vec:
                    sc_arrays.append(varid[i-2:ii, j-1:jj, :sc_z_len, :1])
                    sc_arrays.append(varid_2[i-1:ii, j-2:jj, :sc_z_len, :1])
                    for x in 0,1:
                        # tidy up src array - replace missing val
                        for y in 'mv', 'fv':
                            if not np.isnan(sc_fields[y][x]):
                                ind_vec[y] = sc_arrays[x] == sc_fields[y][x]
                                sc_arrays[x][ind_vec[y]] = 0
                            else:
                                sc_arrays[x][np.isnan(scarr)] = 0
                        # Adjust for scaling or offsets
                        if not np.isnan(sc_fields['sf'][x]):
                            sc_arrays[x] *= sc_fields['sf'][x]
                        if not np.isnan(sc_fields['os'][x]):
                            sc_arrays[x] += sc_fields['os'][x]
                
                        # Colocate velocity points on T grid prior to rotation
                        axis = [1, None]
                        col = 0.5 * (sc_arrays[x][:-axis[0],:-axis[1],:] + 
                                     sc_arrays[x][axis[0]:,axis[1]:,:])
                        col[col == 0] = np.NaN
                        col_sc_arrays.append(col)
                        axis.reverse()
                
                # This is a slab
                else:
                    sc_arrays.append(varid[i-1:ii, j-1:jj, :1])
                    #query var names
                    if msk and first and shoggoth==0:
                        pass
                        # Open another magic file and do stuff
                        nc3 = Dataset(source_mask, 'r')
                        varid_3 = nc3.variables['tmaskutil']
                        msk_array = varid_3[i-1:ii, j-1:jj, :1]
                    if msk: #must be true for msk array ??...
                        sc_arrays[0][msk_array == 0] = np.NaN

        
            # Finished reading Source data

            #for depth_val in range(sc_z_len):
            #    tmp_arrays = []
            #    if not key_vec:
            #        tmp_arrays.append(sc_arrays[0][:,:depth_val]


    def _fv_mv_to_zero(self, scarr, indvec, sc_fields, pos):
        
        for x in 'mv', 'fv':
            if not np.isnan(sc_fields[x][pos]):
                ind_vec[x] = scarr == sc_fields[x][pos]
                scarr[ind_vec[x]] = 0
            else:
                scarr[np.isnan(scarr)] = 0
        return scarr, indvec

    # Convert numeric date from source to dest
    def convert_date(self, date):
        
        val = self.S_cal.num2date(date)
        return self.D_cal.date2num(val)

    def cal_trans(self, source, dest, year, month):
        vals = {'gregorian': [monthrange(year, month)[1], 31], 'noleap': 
                [365., 31],'360_day': [360., 30]}
        if source not in vals.keys():
            raise ValueError('Unknown calendar type: %s' %source)
        
        sf = val[source][0] / val[dest][0]
        
        return sf, vals[dest][1]





