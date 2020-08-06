'''
Creates Nemo Bdy netCDF file ready for population

Written by John Kazimierz Farey, started August 30, 2012
Port of Matlab code of James Harle
'''
# pylint: disable=E1103
# pylint: disable=no-name-in-module
from netCDF4 import Dataset
import datetime
import logging
from pynemo import nemo_ncml_parse as ncml_parse

def CreateBDYNetcdfFile(filename, N, I, J, K, rw, h, orig, fv, calendar, grd, var_nam,ncml_out):
    """ This method creates a template of bdy netcdf files. A common for
    T, I, U, V, E grid types.
    """
    gridNames = ['T', 'I', 'U', 'V', 'E', 'Z'] # All possible grids
    # Dimension Lengths
    xb_len = N
    yb_len = 1
    x_len = I
    y_len = J
    depth_len = K

    # Enter define mode
    ncid = Dataset(filename, 'w', clobber=True, format='NETCDF4')

    #define dimensions
    if grd in gridNames and grd != 'Z': # i.e grid NOT barotropic (Z)
        z = ncml_parse.gen_dims_NCML(ncml_out,'z')
        dimztID = ncid.createDimension(z, depth_len)
    else:
        logging.error('Grid tpye not known')
    xb = ncml_parse.gen_dims_NCML(ncml_out, 'xb')
    dimxbID = ncid.createDimension(xb, xb_len)
    yb = ncml_parse.gen_dims_NCML(ncml_out,'yb')
    dimybID = ncid.createDimension(yb, yb_len)
    x = ncml_parse.gen_dims_NCML(ncml_out,'x')
    dimxID = ncid.createDimension(x, x_len)
    y = ncml_parse.gen_dims_NCML(ncml_out,'y')
    dimyID = ncid.createDimension(y, y_len)
    time_counter = ncml_parse.gen_dims_NCML(ncml_out,'time_counter')
    dimtcID = ncid.createDimension(time_counter, None)

    #define variable
    time_var = ncml_parse.gen_var_NCML(ncml_out,'time_counter')
    vartcID = ncid.createVariable(time_var['name'], time_var['type'], (time_var['shape'][0], ))
    lon_var = ncml_parse.gen_var_NCML(ncml_out,'nav_lon')
    varlonID = ncid.createVariable(lon_var['name'], lon_var['type'], (lon_var['shape'][0], lon_var['shape'][1], ))
    lat_var = ncml_parse.gen_var_NCML(ncml_out,'nav_lat')
    varlatID = ncid.createVariable(lat_var['name'], lat_var['type'], (lat_var['shape'][0], lat_var['shape'][1], ))

    if grd in ['E']:
        deptht = ncml_parse.gen_var_NCML(ncml_out,'deptht')
        varztID = ncid.createVariable(deptht['name'], deptht['type'], (deptht['shape'][0], deptht['shape'][1], deptht['shape'][2], ))
        bdy_msk = ncml_parse.gen_var_NCML(ncml_out,'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1], ), fill_value=fv)
        N1p = ncml_parse.gen_var_NCML(ncml_out,'N1p')
        varN1pID = ncid.createVariable(N1p['name'], N1p['type'], (N1p['shape'][0], N1p['shape'][1], N1p['shape'][2], N1p['shape'][3], ),
                                       fill_value=fv)
        N3n = ncml_parse.gen_var_NCML(ncml_out,'N3n')
        varN3nID = ncid.createVariable(N3n['name'], N3n['type'], (N3n['shape'][0], N3n['shape'][1], N3n['shape'][2], N3n['shape'][3], ),
                                       fill_value=fv)
        N5s = ncml_parse.gen_var_NCML(ncml_out,'N5s')
        varN5sID = ncid.createVariable(N5s['name'], N5s['type'], (N5s['shape'][0], N5s['shape'][0], N5s['shape'][0], N5s['shape'][0], ),
                                       fill_value=fv)
    elif grd in ['T', 'I']:
        deptht = ncml_parse.gen_var_NCML(ncml_out, 'deptht')
        varztID = ncid.createVariable(deptht['name'], deptht['type'],(deptht['shape'][0], deptht['shape'][1], deptht['shape'][2],))
        bdy_msk = ncml_parse.gen_var_NCML(ncml_out, 'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1],),fill_value=fv)
        # TODO: generic variable name assignment
        temp_var = ncml_parse.gen_var_NCML(ncml_out,'votemper')
        vartmpID = ncid.createVariable(temp_var['name'], temp_var['type'],
                                       (temp_var['shape'][0], temp_var['shape'][1], temp_var['shape'][2], temp_var['shape'][3], ), fill_value=fv)
        sal_var = ncml_parse.gen_var_NCML(ncml_out,'vosaline')
        varsalID = ncid.createVariable(sal_var['name'], sal_var['type'],
                                       (sal_var['shape'][0], sal_var['shape'][1], sal_var['shape'][2], sal_var['shape'][3], ), fill_value=fv)

        if grd == 'I':
            ileadfra = ncml_parse.gen_var_NCML(ncml_out,'ileadfra')
            varildID = ncid.createVariable(ileadfra['name'], ileadfra['type'], (ileadfra['shape'][0], ileadfra['shape'][1], ileadfra['shape'][2],),
                                           fill_value=fv)
            iicethic = ncml_parse.gen_var_NCML(ncml_out,'iicethic')
            variicID = ncid.createVariable(iicethic['name'], iicethic['type'], (iicethic['shape'][0], iicethic['shape'][1], iicethic['shape'][2],),
                                           fill_value=fv)
            isnowthi = ncml_parse.gen_var_NCML(ncml_out,'isnowthi')
            varisnID = ncid.createVariable(isnowthi['name'], isnowthi['type'], (isnowthi['shape'][0], isnowthi['shape'][1], isnowthi['shape'][2],),
                                           fill_value=fv)
    elif grd == 'U':
        depthu = ncml_parse.gen_var_NCML(ncml_out,'depthu')
        varztID = ncid.createVariable(depthu['name'], depthu['type'], (depthu['shape'][0], depthu['shape'][1], depthu['shape'][2], ), fill_value=fv)
        vobtcrx = ncml_parse.gen_var_NCML(ncml_out,'vobtcrtx')
        varbtuID = ncid.createVariable(vobtcrx['name'], vobtcrx['type'], (vobtcrx['shape'][0], vobtcrx['shape'][1], vobtcrx['shape'][2], ),
                                       fill_value=fv)
        vozocrtx = ncml_parse.gen_var_NCML(ncml_out,'vozocrtx')
        vartouID = ncid.createVariable(vozocrtx['name'], vozocrtx['type'],
                                       (vozocrtx['shape'][0], vozocrtx['shape'][1], vozocrtx['shape'][2], vozocrtx['shape'][3], ),
                                       fill_value=fv)
    elif grd == 'V':
        depthv = ncml_parse.gen_var_NCML(ncml_out, 'depthv')
        varztID = ncid.createVariable(depthv['name'], depthv['type'], (depthv['shape'][0], depthv['shape'][1], depthv['shape'][2], ))
        vobtcrty = ncml_parse.gen_var_NCML(ncml_out,'vobtcrty')
        varbtvID = ncid.createVariable(vobtcrty['name'], vobtcrty['type'], (vobtcrty['shape'][0], vobtcrty['shape'][1], vobtcrty['shape'][2], ),
                                       fill_value=fv)
        vomecrty = ncml_parse.gen_var_NCML(ncml_out,'vomecrty')
        vartovID = ncid.createVariable(vomecrty['name'], vomecrty['type'],
                                       (vomecrty['shape'][0], vomecrty['shape'][1], vomecrty['shape'][2], vomecrty['shape'][3],),
                                       fill_value=fv)
    elif grd == 'Z':
        sossheig = ncml_parse.gen_var_NCML(ncml_out,'sossheig')
        varsshID = ncid.createVariable(sossheig['name'], sossheig['type'], (sossheig['shape'][0], sossheig['shape'][1], sossheig['shape'][2], ),
                                       fill_value=fv)
        bdy_msk = ncml_parse.gen_var_NCML(ncml_out,'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1], ), fill_value=fv)
    else:
        logging.error("Unknow Grid input")

    nbidta = ncml_parse.gen_var_NCML(ncml_out,'nbidta')
    varnbiID = ncid.createVariable(nbidta['name'], nbidta['type'], (nbidta['shape'][0], nbidta['shape'][1], ))
    nbjdta = ncml_parse.gen_var_NCML(ncml_out,'nbjdta')
    varnbjID = ncid.createVariable(nbjdta['name'], nbjdta['type'], (nbjdta['shape'][0], nbjdta['shape'][1], ))
    nbrdta = ncml_parse.gen_var_NCML(ncml_out, 'nbrdta')
    varnbrID = ncid.createVariable(nbrdta['name'], nbrdta['type'], (nbrdta['shape'][0], nbrdta['shape'][1], ))

    #Global Attributes
    ncid.file_name = filename
    ncid.creation_date = str(datetime.datetime.now())
    ncid.rim_width = rw
    ncid.history = h
    ncid.institution = ncml_parse.gen_attrib_NCML(ncml_out,'institution')

    #Time axis attributes
    vartcID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,time_var['name'],'axis')
    vartcID.standard_name = ncml_parse.gen_var_attrib_NCML(ncml_out,time_var['name'],'standard_name')
    vartcID.units = 'seconds since '+orig
    vartcID.title = ncml_parse.gen_var_attrib_NCML(ncml_out,time_var['name'],'title')
    vartcID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,time_var['name'],'long_name')
    # TODO: should the bdy file or NCML file define what origin or calendar to use?
    vartcID.time_origin = orig
    vartcID.calendar = calendar

    #Longitude axis attributes
    varlonID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,lon_var['name'],'axis')
    varlonID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,lon_var['name'],'short_name')
    varlonID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,lon_var['name'],'units')
    varlonID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,lon_var['name'],'long_name')

    #Latitude axis attributes
    varlatID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,lat_var['name'],'axis')
    varlatID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,lat_var['name'],'short_name')
    varlatID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,lat_var['name'],'units')
    varlatID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,lat_var['name'],'long_name')

    #nbidta attributes
    varnbiID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbidta['name'],'short_name')
    varnbiID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,nbidta['name'],'units')
    varnbiID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbidta['name'],'long_name')

    #nbjdta attributes
    varnbjID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbjdta['name'],'short_name')
    varnbjID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,nbjdta['name'],'units')
    varnbjID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbjdta['name'],'long_name')

    #nbrdta attributes
    varnbrID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbrdta['name'],'short_name')
    varnbrID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,nbrdta['name'],'units')
    varnbrID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,nbrdta['name'],'long_name')

    if grd == 'E':
        varztID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID['name'],'axis')
        varztID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID['name'],'short_name')
        varztID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID['name'],'units')
        varztID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID['name'],'long_name')

        varmskID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID['name'],'short_name')
        varmskID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID['name'],'units')
        varmskID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID['name'],'long_name')

        varN1pID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varN1pID['name'],'units')
        varN1pID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN1pID['name'],'short_name')
        varN1pID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN1pID['name'],'long_name')
        varN1pID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varN1pID['name'],'grid')

        varN3nID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varN3nID['name'],'units')
        varN3nID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN3nID['name'],'short_name')
        varN3nID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN3nID['name'],'long_name')
        varN3nID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varN3nID['name'],'grid')

        varN5sID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varN5sID['name'],'units')
        varN5sID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN5sID['name'],'short_name')
        varN5sID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varN5sID['name'],'long_name')
        varN5sID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varN5sID['name'],'grid')

    if grd in ['T', 'I']:
        varztID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'axis')
        varztID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'short_name')
        varztID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'units')
        varztID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'long_name')

        varmskID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'short_name')
        varmskID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'units')
        varmskID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'long_name')

        vartmpID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,vartmpID.name,'units')
        vartmpID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartmpID.name,'short_name')
        vartmpID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartmpID.name,'long_name')
        vartmpID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,vartmpID.name,'grid')

        varsalID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varsalID.name,'units')
        varsalID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varsalID.name,'short_name')
        varsalID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varsalID.name,'long_name')
        varsalID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varsalID.name,'grid')

        if grd == 'I':
            varildID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varildID.name,'units')
            varildID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varildID.name,'short_name')
            varildID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varildID.name,'long_name')
            varildID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varildID.name,'grid')

            variicID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,variicID.name,'units')
            variicID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,variicID.name,'short_name')
            variicID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,variicID.name,'long_name')
            variicID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,variicID.name,'grid')

            varisnID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varisnID.name,'units')
            varisnID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varisnID.name,'short_name')
            varisnID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varisnID.name,'long_name')
            varisnID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varisnID.name,'grid')

    elif grd == 'U':
        varztID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'axis')
        varztID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'short_name')
        varztID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'units')
        varztID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'long_name')

        varbtuID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtuID.name,'units')
        varbtuID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtuID.name,'short_name')
        varbtuID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtuID.name,'long_name')
        varbtuID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtuID.name,'grid')

        vartouID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,vartouID.name,'units')
        vartouID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartouID.name,'short_name')
        vartouID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartouID.name,'long_name')
        vartouID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,vartouID.name,'grid')

    elif grd == 'V':
        varztID.axis = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'axis')
        varztID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'short_name')
        varztID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'units')
        varztID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varztID.name,'long_name')

        varbtvID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtvID.name,'units')
        varbtvID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtvID.name,'short_name')
        varbtvID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtvID.name,'long_name')
        varbtvID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varbtvID.name,'grid')

        vartovID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,vartovID.name,'units')
        vartovID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartovID.name,'short_name')
        vartovID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,vartovID.name,'long_name')
        vartovID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,vartovID.name,'grid')

    elif grd == 'Z':
        varsshID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varsshID.name,'units')
        varsshID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varsshID.name,'short_name')
        varsshID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varsshID.name,'long_name')
        varsshID.grid = ncml_parse.gen_var_attrib_NCML(ncml_out,varsshID.name,'grid')

        varmskID.short_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'short_name')
        varmskID.units = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'units')
        varmskID.long_name = ncml_parse.gen_var_attrib_NCML(ncml_out,varmskID.name,'long_name')

    else:
        logging.error('Unknown Grid')

    ncid.close()


