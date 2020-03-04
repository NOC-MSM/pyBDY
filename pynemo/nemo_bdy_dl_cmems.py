# -*- coding: utf-8 -*-
"""
Set of functions to download CMEMS files using FTP (for static mask data) and MOTU (for subsetted variable data).

"""
# import modules
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import logging
import ftplib
import re
import pandas as pd
from datetime import datetime
import glob
import os
#local imports
from pynemo.utils import cmems_errors as errors

logger = logging.getLogger('CMEMS Downloader')

'''
This function checks to see if the MOTU client is installed on the PyNEMO python environment. If it is not installed
error code 1 is returned . If it is installed the version number of the installed client is returned as a string
'''
def chk_motu():
    stdout,stderr = Popen(['motuclient','--version'], stdout=PIPE, stderr=PIPE,universal_newlines=True).communicate()
    stdout = stdout.strip()
    stderr = stderr.strip()

    if len(stderr) > 0:
        return stderr
    
    if not 'motuclient-python' in stdout:
        return 1
    else:
        idx = stdout.find('v')
        return stdout[idx:-1]


'''
CMEMS holds mask data for the model grids as an FTP download only, i.e. it can't be used with the MOTU subsetter.
This code logs on to the FTP server and downloads the requested files. The config bdy file needs to provide location and 
filenames to download. These can be found using an FTP server or the CMEMS web portal. The credintials for the 
FTP connection (and MOTU client) are stored in a Credintials files called CMEMS_cred.py located in the utils folder.
If the download is successful a zero status code is returned. Other wise an error message is returned in the form of a string
'''
def get_static(args):
    try:
        from pynemo.utils import CMEMS_cred
    except ImportError:
        logger.error('Unable to import CMEMS creditials, see Readme for instructions on adding to PyNEMO')
        return 'Unable to import credintials file'
    try:
        ftp = ftplib.FTP(host=args['ftp_server'], user=CMEMS_cred.user, passwd=CMEMS_cred.pwd)
    except ftplib.error_temp:
        return 'temporary error in FTP connection, please try running PyNEMO again........'
    except ftplib.error_perm as err:
        return err
    except ftplib.error_reply as err:
        return err
    except ftplib.error_proto as err:
        return err
    # TODO: provide better returns for the various FTP errors
    # TODO: add try excepts to handle issues with files being missing etc.
    # TODO: Check there is enough space to download as well.....
    # TODO: Handle timeouts etc as well......
    ftp.cwd(args['static_dir'])
    filenames = args['static_filenames'].split(' ')
    for f in filenames:
        try:
            ftp.retrbinary("RETR " + f, open(args['cmems_dir']+f, 'wb').write)
        except ftplib.error_temp:
            return 'temporary error in FTP download, please try running PyNEMO again........'
        except ftplib.error_perm as err:
            return err
        except ftplib.error_reply as err:
            return err
        except ftplib.error_proto as err:
            return err
    ftp.quit()

    return 0

'''
The FTP download results in the whole product grid being downloaded, so this needs to be subset to match the data downloads
This functions uses CDO library to subset the netcdf file. Therefore CDO should be installed on the operating system.
For each of the defined static files this function subsets based on the defined extent in the settings bdy file, 
if 'Abort' is in the string returned by CDO then this is returned as an error string. 
If Abort is not in the returned string this indicates success, then a zero status code is returned.
'''
def subset_static(args):
    logger.info('subsetting static files now......')
    filenames = args['static_filenames'].split(' ')
    for f in filenames:
        v = f.split('_')
        v = args['dl_prefix']+'_'+v[-1]
        cdo = args['cdo_loc']
        sellon = 'sellonlatbox,'+str(args['longitude_min'])+','+str(args['longitude_max'])+','\
                 +str(args['latitude_min'])+','+str(args['latitude_max'])
        src_file = args['cmems_dir']+f
        dst_file = args['cmems_dir']+v
        stdout, stderr = Popen([cdo, sellon, src_file, dst_file],stdout=PIPE, stderr=PIPE,universal_newlines=True).communicate()
        stdout = stdout.strip()
        stderr = stderr.strip()

        # For some reason CDO seems to pipe output to stderr so check stderr for results and pass stdout
        # if it has length greater than zero i.e. not an empty string
        if 'Abort' in stderr:
            return stderr
        if len(stdout) > 0:
            return stdout
    return 0

'''
Request CMEMS data in either monthly, weekly, and daily intervals. Depending on the character passed to the function 'F'
the function will split the requests into monthly, weekly or daily intervals. The function splits the requested period into 
the relevent intervals and passes the interval into the request_cmems function below. If request_cmems returns a zero then
the next interval is downloaded. If there is an error then the string containing the error is returned. Part of request_cmems
is that it returns a 1 if the interval is too large.
'''
def MWD_request_cmems(args,date_min,date_max,F):
    if F == 'M':
        month_start = pd.date_range(date_min, date_max,
                                freq='MS').strftime("%Y-%m-%d").tolist()
        month_end = pd.date_range(date_min, date_max,
                              freq='M').strftime("%Y-%m-%d").tolist()
        for m in range(len(month_end)):
            mnth_dl = request_cmems(args, month_start[m], month_end[m])
            if mnth_dl == 0:
                logger.info('CMEMS month request ' + str((m + 1)) + 'of' + (str(len(month_end))) + ' successful')
            if type(mnth_dl) == str:
                logger.error(
                    'CMEMS month request ' + str((m + 1)) + 'of' + str((len(month_end))) + ' unsuccessful: Error Msg below')
                logger.error(mnth_dl)
                return mnth_dl
            if mnth_dl == 1:
                return 1

    if F == 'W':
        week_start = pd.date_range(date_min, date_max,
                                   freq='W').strftime("%Y-%m-%d").tolist()
        week_end = []
        for w in range(len(week_start)):
            week_end.append((datetime.strptime(week_start[w], '%Y-%m-%d')
                             + datetime.timedelta(days=6)).strftime('%Y-%m-%d'))
        for w in range(len(week_end)):
            wk_dl = request_cmems(args, week_start[w], week_end[w])
            if wk_dl == 0:
                logger.info('CMEMS week request ' + str((w + 1)) + 'of' + str((len(week_end))) + ' successful')
                if type(wk_dl) == str:
                    logger.error(
                        'CMEMS week request ' + str((m + 1)) + 'of' + str((len(week_end))) + ' unsuccessful: Error Msg below')
                    logger.error(wk_dl)
                    return wk_dl
                if wk_dl == 1:
                    return 1

    if F == 'D':
        days = pd.date_range(date_min, date_max,
                             freq='D').strftime("%Y-%m-%d").tolist()
        for d in range(len(days)):
            dy_dl = request_cmems(args, days[d], days[d])
            if dy_dl == 0:
                logger.info('CMEMS day request ' + str((d + 1)) + 'of' + str((len(week_end) + 1)) + ' successful')
            if dy_dl == 1:
                logger.error('CMEMS day request still too big, please make domain smaller, or use less variables')
                return
            if type(dy_dl) == str:
                logger.error('CMEMS day request ' + str((d + 1)) + 'of' + (
                        str(len(days))) + ' unsuccessful: Error Msg below')
                logger.error(dy_dl)
                return dy_dl

    if F not in ('MWD'):
        time_int_err = 'incorrect string used to define time download interval please use M, W or D'
        logger.error(time_int_err)
        return time_int_err

    return 0

'''
Main request cmems download function. First tries to import CMEMS creditials as per FTP function. This function reads
the defined NCML file from the bdy file. This gives the number of variables to populate the MOTU download config file.
For each variable, the name and grid type are pulled from the NCML and populated into a python dictionary.

For each item in the dictionary the relevent request is populated in the CMEMS config file. The first request has
 a size flag applied and a xml file is downloaded containing details of the request. 
 If the request is valid a field in the XML is set to OK and then the request is repeated with the size flag removed
resulting in the download of the relevent netcdf file. The console information is parsed to check for errors 
and for confirmation of the success of the download. If there are errors the error string is returned otherwise a
success message is written to the log file. If the request is too big than a 1 error code is returned. 
Otherwise if all requests are successful then a zero status code is returned.
'''
def request_cmems(args, date_min, date_max):
    try:
        from pynemo.utils import CMEMS_cred
    except ImportError:
        logger.error('Unable to import CMEMS credentials, see Readme for instructions on adding to PyNEMO')
        return 'Unable to import credentials file'

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
        logger.info('Variable '+ str(n+1)+' is '+Type['name']+' (Variable name: '+var_name+')')
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
            filedata = filedata.replace('YSLTB459ZW0P84GE', args['dl_prefix']+'_'+str(date_min)+'_'+str(date_max)+'_'+str(key)+'.nc')
    
        with open(args['cmems_config'], 'w') as file:
            file.write(filedata)

        stdout,stderr = Popen(['motuclient', '--size','--config-file', args['cmems_config']], stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate()
        stdout = stdout.strip()
        stderr = stderr.strip()
        logger.info('checking size of request for variables '+' '.join(grids[key]))

        if 'ERROR' in stdout:
            idx = stdout.find('ERROR')
            return stdout[idx-1:-1]

        if 'Done' in stdout:
            logger.info('download of request xml file for variable ' + ' '.join(grids[key]) + ' successful')

        if len(stderr) > 0:
            return stderr

        xml = locs[key]+args['dl_prefix']+'_'+str(date_min)+'_'+str(date_max)+'_'+str(key)+ '.xml'
        try:
            root = ET.parse(xml).getroot()
        except ET.ParseError:
            return 'Parse Error in XML file, This generally occurs when CMEMS service is down and returns an unexpected XML.'

        logger.info('size of request ' + root.attrib['size'])

        if 'OK' in root.attrib['msg']:
            logger.info('request valid, downloading now......')
            stdout,stderr = Popen(['motuclient', '--config-file', args['cmems_config']], stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate()
            stdout = stdout.strip()
            stderr = stderr.strip()

            if 'ERROR' in stdout:
                idx = stdout.find('ERROR')
                return stdout[idx:-1]

            if 'Done' in stdout:
                logger.info('downloading of variables '+' '.join(grids[key])+' successful')

            if len(stderr) > 0:
                return stderr

        elif 'too big' in root.attrib['msg']:
            return 1
        else:
            return 'unable to determine if size request is valid (too big or not)'

    return 0

'''
Function to check errors from both FTP or MOTU. This checks a python file containing dictionaries for different error types,
(currently FTP and MOTU) with the error from the download. If the error code is present as a key, then the system will retry
or exit. This depends which error dictionary the type is in. i.e. restart errors result in restart and critical errors result
in sys exit. The number of restarts is defined in the BDY file and once expired results in sys exit. Finally if the error is 
not in the type dictionaries the system will exit. Unlogged errors can be added so that a restart or exit occurs when they occur.
'''
def err_parse(error, err_type):

    if err_type == 'FTP':
        for key in errors.FTP_retry:
            if key in error:
                logger.info('retrying FTP download....')
                return 0
        for key in errors.FTP_critical:
            if key in error:
                logger.info('critical FTP error, stopping')
                return 1
        logger.critical('unlogged FTP error, stopping')
        logger.critical(error)
        return 2

    if err_type == 'MOTU':
        for key in errors.MOTU_retry:
            if key in error:
                logger.info('non critical error')
                logger.info('restarting download....')
                return 0
        for key in errors.MOTU_critical:
            if key in error:
                logger.critical('critical error found: please see below')
                logger.critical(error)
                return 1
        logger.critical('unlogged error: please see below')
        logger.critical(error)
        return 2

'''
Function to clean up the download process, this is called before every sys exit and at the end of the download function
At the moment it only removes the xml size files that are no longer required. Other functionality maybe added in the future
'''
def clean_up(settings):
    # remove size check XML files that are no longer needed.
    try:
        for f in glob.glob(settings['cmems_dir'] + "*.xml"):
            os.remove(f)
    except OSError:
        logger.info('no xml files found to remove')
        return
    logger.info('removed size check xml files successfully')
    return
