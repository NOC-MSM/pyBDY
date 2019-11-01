# -*- coding: utf-8 -*-
"""
Libray module to populate an motu configuration file to download CMEMS data 
using the motu client python module
"""
# import modules
from subprocess import Popen, PIPE

# Need to add try excepts for files and folders being present

# check to see if motuclient is installed, if not then return error
# if it is installed return the version number
def chk_motu():
    chk = Popen(['motuclient','--version'], stdout=PIPE, stderr=PIPE)
    stdout,stderr = chk.communicate()
    
    if not 'motuclient-python' in stdout:
        status = 1
    
    else:
        idx = stdout.find('v')
        version = stdout[idx:-1]
        status = version
        
    return status
 
# request CMEMSE data by populating config file with arguments passed from bdy file
# then execute command using subprocess. stdout is checked for errors 
# and confirmation of successful download     
def request_CMEMS(args):
    
    with open(args['ini_config_template'], 'r') as file:
        filedata = file.read()
            
        filedata = filedata.replace('J90TBS4Q1UCT4CM7', args['user'])
        filedata = filedata.replace('Z8UKFNXA5OIZRXCK', args['pwd'])
        filedata = filedata.replace('DSGJJGWODV2F8TFU', args['motu_server'])
        filedata = filedata.replace('S7L40ACQHANTAC6Y', args['service_id'])
        filedata = filedata.replace('4LC8ALR9T96XN08U', args['product_id'])
        filedata = filedata.replace('M49OAWI14XESWY1K', args['date_min'])
        filedata = filedata.replace('DBT3J4GH2O19Q75P', args['date_max'])
        filedata = filedata.replace('3M2FJJE5JW1EN4C1', str(args['latitude_min']))
        filedata = filedata.replace('OXI2PXSTJG5PV6OW', str(args['latitude_max']))
        filedata = filedata.replace('DWUJ65Y233FQFW3F', str(args['longitude_min']))
        filedata = filedata.replace('K0UQJJDJOKX14DPS', str(args['longitude_max']))
        filedata = filedata.replace('FNO0GZ1INQDATAXA', str(args['depth_min']))
        filedata = filedata.replace('EI6GB1FHTMCIPOZC', str(args['depth_max']))
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
        status = 0
    
    return status