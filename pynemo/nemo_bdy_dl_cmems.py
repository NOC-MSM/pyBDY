# -*- coding: utf-8 -*-
"""
Libray module to populate an motu configuration file to download CMEMS data 
using the motu client python module
"""
# import modules
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import logging
import ftplib
from pynemo.utils import CMEMS_cred
import re

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

def get_static(args):
    try:
        ftp = ftplib.FTP(host=args['ftp_server'], user=CMEMS_cred.user, passwd=CMEMS_cred.pwd)
    except PermissionError as e:
        return e
    except TimeoutError as e:
        return e
    # TODO: add try excepts to handle issues with files being missing etc.
    # TODO: Check there is enough space to download as well.....
    # TODO: Handle timeouts etc as well......
    ftp.cwd(args['static_dir'])
    filenames = args['static_filenames'].split(' ')
    for f in filenames:
        ftp.retrbinary("RETR " + f, open(args['cmems_dir']+f, 'wb').write)
    ftp.quit()

    return 0

def subset_static(args):
    logger.info('subsetting static files now......')
    filenames = args['static_filenames'].split(' ')
    for f in filenames:
        v = f.split('_')
        v = 'subset_'+v[-1]
        cdo = '/opt/local/bin/cdo'
        sellon = 'sellonlatbox,'+str(args['longitude_min'])+','+str(args['longitude_max'])+','\
                 +str(args['latitude_min'])+','+str(args['latitude_max'])
        src_file = args['cmems_dir']+f
        dst_file = args['cmems_dir']+v
        sub_coords = Popen([cdo, sellon, src_file, dst_file],stdout=PIPE, stderr=PIPE)
        stdout, stderr = sub_coords.communicate()
        # For some reason CDO seems to pipe output to stderr so check stderr for results and pass stdout
        # if it has length greater than zero i.e. not an empty string
        if 'Abort' in stderr:
            return stderr
        if len(stdout) > 0:
            return stdout
    return 0

def request_cmems(args, date_min, date_max):
    logger.info('CMEMS data requested.......')
    xml = args['src_dir']
    root = ET.parse(xml).getroot()
    num_var = (len(root.getchildren()[0].getchildren()))
    logger.info('number of variables requested is '+str(num_var))
    grids = {}
    locs = {}
    for n in range(num_var):
        F = root.getchildren()[0].getchildren()[n].getchildren()[0].getchildren()[0].attrib
        var_name = root.getchildren()[n+1].attrib['name']
        Type = root.getchildren()[0].getchildren()[n].getchildren()[0].attrib
        logger.info('Variable '+ str(n+1)+' is '+Type['name']+'( Variable name: '+var_name+')')
        r = re.findall('([A-Z])', F['regExp'])
        r = ''.join(r)
        logger.info('It is on the '+str(r)+' grid')
        if r in grids:
            grids[r].append(var_name)
        else:
            grids[r] = [var_name]
        if r in locs:
            pass
        else:
            locs[r] = F['location'][6:]

    for key in grids:
        with open(args['cmems_config_template'], 'r') as file:
            filedata = file.read()
            
            filedata = filedata.replace('J90TBS4Q1UCT4CM7', CMEMS_cred.user)
            filedata = filedata.replace('Z8UKFNXA5OIZRXCK', CMEMS_cred.pwd)
            filedata = filedata.replace('DSGJJGWODV2F8TFU', args['motu_server'])
            filedata = filedata.replace('S7L40ACQHANTAC6Y', args['cmems_model'])
            filedata = filedata.replace('4LC8ALR9T96XN08U', args['cmems_product'])
            filedata = filedata.replace('M49OAWI14XESWY1K', date_min)
            filedata = filedata.replace('DBT3J4GH2O19Q75P', date_max)
            filedata = filedata.replace('3M2FJJE5JW1EN4C1', str(args['latitude_min']))
            filedata = filedata.replace('OXI2PXSTJG5PV6OW', str(args['latitude_max']))
            filedata = filedata.replace('DWUJ65Y233FQFW3F', str(args['longitude_min']))
            filedata = filedata.replace('K0UQJJDJOKX14DPS', str(args['longitude_max']))
            filedata = filedata.replace('FNO0GZ1INQDATAXA', str(args['depth_min']))
            filedata = filedata.replace('EI6GB1FHTMCIPOZC', str(args['depth_max']))
            filedata = filedata.replace('4Y4LMQLAKP10YFUE', ','.join(grids[key]))
            filedata = filedata.replace('QFCN2P56ZQSA7YNK', locs[key])
            filedata = filedata.replace('YSLTB459ZW0P84GE', args['dl_prefix']+'_'+str(key)+'.nc')
    
        with open(args['cmems_config'], 'w') as file:
            file.write(filedata)

        size_chk = Popen(['motuclient', '--size','--config-file', args['cmems_config']], stdout=PIPE, stderr=PIPE)
        stdout,stderr = size_chk.communicate()
        logger.info('checking size of request for variables '+' '.join(grids[key]))

        if 'ERROR' in stdout:
            idx = stdout.find('ERROR')
            status = stdout[idx-1:-1]
            return status

        if 'Done' in stdout:
            status = 0

        xml = locs[key]+args['dl_prefix']+'_'+key+ '.xml'
        root = ET.parse(xml).getroot()
        logger.info('size of request ' + root.attrib['size'])

        if 'OK' in root.attrib['msg']:
            logger.info('request valid, downloading now......')
            motu = Popen(['motuclient', '--config-file', args['cmems_config']], stdout=PIPE, stderr=PIPE)
            stdout, stderr = motu.communicate()

            if 'ERROR' in stdout:
                idx = stdout.find('ERROR')
                status = stdout[idx:-1]
                return status

            if 'Done' in stdout:
                logger.info('downloading of variables '+' '.join(grids[key])+' successful')
                status = 0

        elif 'too big' in root.attrib['msg']:

            status = 'file request too big reduce size of domain or length of time series'
            return status

        else:
            status = 'unable to determine if size request is valid (too big or not)'

    return status

