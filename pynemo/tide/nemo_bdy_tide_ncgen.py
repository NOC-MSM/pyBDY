'''
Creates Tide netcdf file ready for population

@author: Mr. Srikanth Nagella
'''

from netCDF4 import Dataset 
import datetime
import logging
from pynemo import nemo_ncml_parse as ncml_parse

def CreateBDYTideNetcdfFile(filename, N,I,J,h,fv,grd,ncml_out):
    gridNames = ['T', 'U', 'V']
    
    # Dimension Lengths
    xb_len = N
    yb_len = 1
    x_len  = I
    y_len  = J
    
    # Enter define mode
    ncid = Dataset(filename, 'w', clobber=True, format='NETCDF4')
    
    #define dimensions
    xb = ncml_parse.dst_dims(ncml_out, 'xb')
    dimxbID = ncid.createDimension(xb,xb_len)
    yb = ncml_parse.dst_dims(ncml_out, 'yb')
    dimybID = ncid.createDimension(yb,yb_len)
    x = ncml_parse.dst_dims(ncml_out, 'x')
    dimxID  = ncid.createDimension(x, x_len)
    y = ncml_parse.dst_dims(ncml_out, 'y')
    dimyID  = ncid.createDimension(y, y_len)

    #define variable
    lon_var = ncml_parse.dst_var(ncml_out, 'nav_lon')
    varlonID = ncid.createVariable(lon_var['name'], lon_var['type'], (lon_var['shape'][0], lon_var['shape'][1], ))
    lat_var = ncml_parse.dst_var(ncml_out, 'nav_lat')
    varlatID = ncid.createVariable(lat_var['name'], lat_var['type'], (lat_var['shape'][0], lat_var['shape'][1], ))

    if grd =='T':
        bdy_msk = ncml_parse.dst_var(ncml_out, 'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1],),fill_value=fv)
        z1 = ncml_parse.dst_var(ncml_out,'z1')
        varz1ID = ncid.createVariable(z1['name'],z1['type'],(z1['shape'][0],z1['shape'][1],),fill_value=fv)
        z2 = ncml_parse.dst_var(ncml_out,'z2')
        varz2ID = ncid.createVariable(z2['name'],z2['type'],(z2['shape'][0],z2['shape'][1],),fill_value=fv)

    elif grd == 'U':
        bdy_msk = ncml_parse.dst_var(ncml_out, 'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1],),fill_value=fv)
        u1 = ncml_parse.dst_var(ncml_out,'u1')
        varu1ID = ncid.createVariable(u1['name'],u1['type'],(u1['shape'][0],u1['shape'][1],),fill_value=fv)
        u2 = ncml_parse.dst_var(ncml_out,'u2')
        varu2ID = ncid.createVariable(u2['name'],u2['type'],(u2['shape'][0],u2['shape'][1],),fill_value=fv)
    elif grd == 'V':
        bdy_msk = ncml_parse.dst_var(ncml_out, 'bdy_msk')
        varmskID = ncid.createVariable(bdy_msk['name'], bdy_msk['type'], (bdy_msk['shape'][0], bdy_msk['shape'][1],),fill_value=fv)
        v1 = ncml_parse.dst_var(ncml_out,'v1')
        varv1ID = ncid.createVariable(v1['name'],v1['type'],(v1['shape'][0],v1['shape'][1],),fill_value=fv)
        v2 = ncml_parse.dst_var(ncml_out,'v2')
        varv2ID = ncid.createVariable(v2['name'],v2['type'],(v2['shape'][0],v2['shape'][1],),fill_value=fv)
    else :
        logging.error("Unknown Grid input")
        
    
    nbidta = ncml_parse.dst_var(ncml_out,'nbidta')
    varnbiID = ncid.createVariable(nbidta['name'], nbidta['type'], (nbidta['shape'][0], nbidta['shape'][1], ))
    nbjdta = ncml_parse.dst_var(ncml_out,'nbjdta')
    varnbjID = ncid.createVariable(nbjdta['name'], nbjdta['type'], (nbjdta['shape'][0], nbjdta['shape'][1], ))
    nbrdta = ncml_parse.dst_var(ncml_out, 'nbrdta')
    varnbrID = ncid.createVariable(nbrdta['name'], nbrdta['type'], (nbrdta['shape'][0], nbrdta['shape'][1], ))
    #Global Attributes
    ncid.file_name = filename
    ncid.creation_date = str(datetime.datetime.now())
    ncid.history = h
    ncid.institution = ncml_parse.dst_glob_attrib(ncml_out,'institution')
    
    #Longitude axis attributes
    varlonID.axis = ncml_parse.dst_var_attrib(ncml_out,lon_var['name'],'axis')
    varlonID.short_name = ncml_parse.dst_var_attrib(ncml_out,lon_var['name'],'short_name')
    varlonID.units = ncml_parse.dst_var_attrib(ncml_out,lon_var['name'],'units')
    varlonID.long_name = ncml_parse.dst_var_attrib(ncml_out,lon_var['name'],'long_name')
    
    #Latitude axis attributes
    varlatID.axis = ncml_parse.dst_var_attrib(ncml_out,lat_var['name'],'axis')
    varlatID.short_name = ncml_parse.dst_var_attrib(ncml_out,lat_var['name'],'short_name')
    varlatID.units = ncml_parse.dst_var_attrib(ncml_out,lat_var['name'],'units')
    varlatID.long_name = ncml_parse.dst_var_attrib(ncml_out,lat_var['name'],'long_name')
    
    #nbidta attributes
    varnbiID.short_name = ncml_parse.dst_var_attrib(ncml_out,nbidta['name'],'short_name')
    varnbiID.units = ncml_parse.dst_var_attrib(ncml_out,nbidta['name'],'units')
    varnbiID.long_name = ncml_parse.dst_var_attrib(ncml_out,nbidta['name'],'long_name')
    
    #nbjdta attributes
    varnbjID.short_name = ncml_parse.dst_var_attrib(ncml_out,nbjdta['name'],'short_name')
    varnbjID.units = ncml_parse.dst_var_attrib(ncml_out,nbjdta['name'],'units')
    varnbjID.long_name = ncml_parse.dst_var_attrib(ncml_out,nbjdta['name'],'long_name')
    
    #nbrdta attributes
    varnbrID.short_name = ncml_parse.dst_var_attrib(ncml_out,nbrdta['name'],'short_name')
    varnbrID.units = ncml_parse.dst_var_attrib(ncml_out,nbrdta['name'],'units')
    varnbrID.long_name = ncml_parse.dst_var_attrib(ncml_out,nbrdta['name'],'long_name')

    if grd == 'T' :
        varmskID.short_name = ncml_parse.dst_var_attrib(ncml_out,varmskID.name,'short_name')
        varmskID.units = ncml_parse.dst_var_attrib(ncml_out,varmskID.name,'units')
        varmskID.long_name = ncml_parse.dst_var_attrib(ncml_out,varmskID.name,'long_name')
        
        varz1ID.units = ncml_parse.dst_var_attrib(ncml_out,varz1ID.name,'units')
        varz1ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varz1ID.name,'short_name')
        varz1ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varz1ID.name,'long_name')
        varz1ID.grid = ncml_parse.dst_var_attrib(ncml_out,varz1ID.name,'grid')
        
        varz2ID.units = ncml_parse.dst_var_attrib(ncml_out,varz2ID.name,'units')
        varz2ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varz2ID.name,'short_name')
        varz2ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varz2ID.name,'long_name')
        varz2ID.grid = ncml_parse.dst_var_attrib(ncml_out,varz2ID.name,'grid')
        
    elif grd == 'U' :
        
        varu1ID.units = ncml_parse.dst_var_attrib(ncml_out,varu1ID.name,'units')
        varu1ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varu1ID.name,'short_name')
        varu1ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varu1ID.name,'long_name')
        varu1ID.grid = ncml_parse.dst_var_attrib(ncml_out,varu1ID.name,'grid')
        
        varu2ID.units = ncml_parse.dst_var_attrib(ncml_out,varu2ID.name,'units')
        varu2ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varu2ID.name,'short_name')
        varu2ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varu2ID.name,'long_name')
        varu2ID.grid = ncml_parse.dst_var_attrib(ncml_out,varu2ID.name,'grid')
        
    elif grd == 'V':
        
        varv1ID.units = ncml_parse.dst_var_attrib(ncml_out,varv1ID.name,'units')
        varv1ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varv1ID.name,'short_name')
        varv1ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varv1ID.name,'long_name')
        varv1ID.grid = ncml_parse.dst_var_attrib(ncml_out,varv1ID.name,'grid')
        
        varv2ID.units = ncml_parse.dst_var_attrib(ncml_out,varv2ID.name,'units')
        varv2ID.short_name = ncml_parse.dst_var_attrib(ncml_out,varv2ID.name,'short_name')
        varv2ID.long_name = ncml_parse.dst_var_attrib(ncml_out,varv2ID.name,'long_name')
        varv2ID.grid = ncml_parse.dst_var_attrib(ncml_out,varv2ID.name,'grid')
        
    else :
        logging.error('Unknown Grid')
        
    ncid.close()

              
    


