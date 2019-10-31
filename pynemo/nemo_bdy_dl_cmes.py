# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from subprocess import Popen, PIPE

# arguments from bdy file maybe global settings file?
#args= {
#       'ini_config_template'     : './config/motu_config_template.ini',
#       'user'           : 'tprime',
#       'pwd'            : '*5TrsWI8i&Ds',
#       'motu_server'    : 'http://nrt.cmems-du.eu/motu-web/Motu',  
#       'service_id'     : 'NORTHWESTSHELF_ANALYSIS_FORECAST_PHY_004_013-TDS',
#       'product_id'     : 'MetO-NWS-PHY-dm-SAL',
#       'date_min'       : '2019-03-27',
#       'date_max'       : '2019-03-28',
#       'latitude_min'   : '46',
#       'latitude_max'   : '62',
#       'longitude_min'  : '-16',
#       'longitude_max'  : '13',
#       'depth_min'      : '-1',
#       'depth_max'      : '1',
#       'variable'       : 'so',
#       'out_dir'        : './outputs',
#       'out_name'       : 'test.nc',
#       'config_out'     : './config/motu_config.ini'
#       }

def request_CMES(args):

    with open(args['ini_config_template'], 'r') as file:
        filedata = file.read()
            
        filedata = filedata.replace('J90TBS4Q1UCT4CM7', args['user'])
        filedata = filedata.replace('Z8UKFNXA5OIZRXCK', args['pwd'])
        filedata = filedata.replace('DSGJJGWODV2F8TFU', args['motu_server'])
        filedata = filedata.replace('S7L40ACQHANTAC6Y', args['service_id'])
        filedata = filedata.replace('4LC8ALR9T96XN08U', args['product_id'])
        filedata = filedata.replace('M49OAWI14XESWY1K', args['date_min'])
        filedata = filedata.replace('DBT3J4GH2O19Q75P', args['date_max'])
        filedata = filedata.replace('3M2FJJE5JW1EN4C1', args['latitude_min'])
        filedata = filedata.replace('OXI2PXSTJG5PV6OW', args['latitude_max'])
        filedata = filedata.replace('DWUJ65Y233FQFW3F', args['longitude_min'])
        filedata = filedata.replace('K0UQJJDJOKX14DPS', args['longitude_max'])
        filedata = filedata.replace('FNO0GZ1INQDATAXA', args['depth_min'])
        filedata = filedata.replace('EI6GB1FHTMCIPOZC', args['depth_max'])
        filedata = filedata.replace('4Y4LMQLAKP10YFUE', args['variable'])
        filedata = filedata.replace('QFCN2P56ZQSA7YNK', args['out_dir'])
        filedata = filedata.replace('YSLTB459ZW0P84GE', args['out_name'])
    
    with open(args['config_out'], 'w') as file:
        file.write(filedata)        
    
    motu = Popen(['motuclient','--config-file',args['config_out']], stdout=PIPE, stderr=PIPE)
    stdout, stderr = motu.communicate()
    
    if 'ERROR' in stdout:
        idx = stdout.find('ERROR')
        status = stdout[idx:-1]
        
    if 'Done' in stdout:
        status = 'Download Complete!'
    
    return status
