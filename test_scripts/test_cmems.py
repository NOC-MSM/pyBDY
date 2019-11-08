#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 15:49:52 2019

Test script to test download CMEMS data function in PyNEMO. To be incorprated
into profile.py

@author: thopri
"""
# import nemo_bdy_dl_cmems as dl_cmems
# import logging
# import nemo_bdy_setup as setup
# from calendar import monthrange
#
# logger = logging.getLogger(__name__)
# logging.basicConfig(filename='/Users/thopri/Projects/PyNEMO/test_scripts/cmems_test.log', level=logging.INFO)
#
# Setup = setup.Setup('/Users/thopri/Projects/PyNEMO/inputs/namelist_cmems.bdy') # default settings file
# settings = Setup.settings
#
# if settings['use_cmems'] == True:
#
#     if settings['year_end'] - settings['year_000'] > 0:
#         date_min = settings['year_000']+'-01-01'
#         date_max = settings['year_end']+'-12-31'
#
#     days_mth = monthrange(settings['year_end'],settings['month_end'])
#
#     date_min = str(settings['year_000'])+'-'+str(settings['month_000'])+'-01'
#
#     date_max = str(settings['year_end'])+'-'+str(settings['month_end'])+'-'+str(days_mth[1])
#
#     cmes_config= {
#            'ini_config_template'    : settings['cmes_config_template'],
#            'user'                   : settings['cmes_usr'],
#            'pwd'                    : settings['cmes_pwd'],
#            'motu_server'            : settings['motu_server'],
#            'service_id'             : settings['cmes_model'],
#            'product_id'             : settings['cmes_product'],
#            'date_min'               : date_min,
#            'date_max'               : date_max,
#            'latitude_min'           : settings['latitude_min'],
#            'latitude_max'           : settings['latitude_max'],
#            'longitude_min'          : settings['longitude_min'],
#            'longitude_max'          : settings['longitude_max'],
#            'depth_min'              : settings['depth_min'],
#            'depth_max'              : settings['depth_max'],
#            'variable'               : settings['cmes_variable'],
#            'src_dir'                : settings['src_dir'],
#            'out_name'               : settings['cmes_output'],
#            'config_out'             : settings['cmes_config']
#            }
#
#     chk = dl_cmems.chk_motu()
#
#     if chk == 1:
#         logger.error('motuclient not installed, please install by running $ pip install motuclient')
#
#     else:
#         logger.info('version ' +chk+ ' of motuclient is installed')
#     logger.info('requesting CMES download now (this can take a while)...')
#     dl = dl_cmems.request_CMEMS(cmes_config)
#
#     if dl == 0:
#         logger.info('CMES data downloaded successfully')
#
#     if type(dl) == str:
#         logger.error(dl)
#

import sys
import requests, json

#my_config = {'verbose': sys.stderr }
cmems_URL = 'http://nrt.cmems-du.eu/motu-web/Motu'
cas_url = 'https://cmems-cas.cls.fr/cas/login'

#payload = {'user':'tprime','pwd':'*5TrsWI8i&Ds','action':'describeproduct','service':'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS','product':'global-analysis-forecast-phy-001-024'}

#with requests.Session() as session:
#    r = session.post(cmems_URL,data=payload)

response = requests.get(cmems_URL, verify=False)

cookies = response.cookies

payload = {'_eventId': 'submit','lt':'e1s1', 'submit': 'LOGIN', 'username': 'tprime', 'password': '*5TrsWI8i&Ds'}
sessionResp = requests.post(cas_url, data=payload,params=cookies,verify=False)

print sessionResp.status_code
print sessionResp.content

#data = { 'user' : 'tprime', 'pwd' : '*5TrsWI8i&Ds' }
#r = requests.post(cmems_URL, data=json.dumps(data), verify=False)
#token = json.loads(r.text)['session']