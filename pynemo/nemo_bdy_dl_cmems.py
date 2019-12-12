# -*- coding: utf-8 -*-
"""
Libray module to populate an motu configuration file to download CMEMS data 
using the motu client python module
"""
# import modules
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import logging

# Need to add try excepts for files and folders being present

# check to see if motuclient is installed, if not then return error
# if it is installed return the version number
logger = logging.getLogger(__name__)

def chk_motu():
    chk = Popen(['motuclient','--version'], stdout=PIPE, stderr=PIPE)
    stdout,stderr = chk.communicate()
    
    if not 'motuclient-python' in stdout:
        status = 1
    
    else:
        idx = stdout.find('v')
        status = stdout[idx:-1]
        
    return status

def request_cmems(args):
    variables = args['variable'].split(' ')
    filenames = args['out_name'].split(' ')
    v_num = len(variables)
    logger.info('CMEMS data requested.......')
    for v in range(v_num):
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
            filedata = filedata.replace('4Y4LMQLAKP10YFUE', variables[v])
            filedata = filedata.replace('QFCN2P56ZQSA7YNK', args['src_dir'])
            filedata = filedata.replace('YSLTB459ZW0P84GE', filenames[v])
    
        with open(args['config_out'], 'w') as file:
            file.write(filedata)

        size_chk = Popen(['motuclient', '--size','--config-file', args['config_out']], stdout=PIPE, stderr=PIPE)
        stdout,stderr = size_chk.communicate()
        logger.info('checking size of request for variables '+variables[v])

        if 'ERROR' in stdout:
            idx = stdout.find('ERROR')
            status = stdout[idx-1:-1]
            return status

        if 'Done' in stdout:
            status = 0

        split_filename = filenames[v].split('.')
        xml = args['src_dir']+split_filename[0] + '.xml'
        root = ET.parse(xml).getroot()
        logger.info('size of request ' + root.attrib['size'])

        if 'OK' in root.attrib['msg']:
            logger.info('request valid, downloading now......')
            motu = Popen(['motuclient', '--config-file', args['config_out']], stdout=PIPE, stderr=PIPE)
            stdout, stderr = motu.communicate()

            if 'ERROR' in stdout:
                idx = stdout.find('ERROR')
                status = stdout[idx:-1]
                return status

            if 'Done' in stdout:
                logger.info('downloading of variables '+variables[v]+' successful')
                status = 0

        #split = float(root.attrib['maxAllowedSize']) / float(root.attrib['size'])

        elif 'too big' in root.attrib['msg']:

            status = 'file request too big reduce size of domain or length of time series'
            return status

        else:
            status = 'unable to determine if size request is valid (too big or not)'

    return status

