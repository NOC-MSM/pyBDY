#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 15:49:52 2019

@author: thopri
"""

import nemo_bdy_dl_cmes as dl_cmes
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='cmes_test.log', level=logging.INFO)
# These are from the bdy file.
settings = {
       'ini_config_template' : './config/motu_config_template.ini',
       'cmes_user'           : 'tprime',
       'cmes_pwd'            : '*5TrsWI8i&Ds',
       'motu_server'         : 'http://nrt.cmems-du.eu/motu-web/Motu',  
       'cmes_model'          : 'NORTHWESTSHELF_ANALYSIS_FORECAST_PHY_004_013-TDS',
       'cmes_product'        : 'MetO-NWS-PHY-dm-SAL',
       'date_min'            : '2019-03-27',
       'date_max'            : '2019-03-28',
       'latitude_min'        : '46',
       'latitude_max'        : '62',
       'longitude_min'       : '-16',
       'longitude_max'       : '13',
       'depth_min'           : '-1',
       'depth_max'           : '1',
       'cmes_variable'       : 'so',
       'dst_dir'             : './outputs',
       'cmes_output'         : 'test.nc',
       'config_location'     : './config/motu_config.ini'
       }

use_CMES = True

if use_CMES == True:

    cmes_config= {
           'ini_config_template'    : settings['cmes_config_template'],
           'user'                   : settings['cmes_user'],
           'pwd'                    : settings['cmes_pwd'],
           'motu_server'            : settings['motu_server'],  
           'service_id'             : settings['cmes_model'],
           'product_id'             : settings['cmes_product'],
           'date_min'               : '2019-03-27',
           'date_max'               : '2019-03-28',
           'latitude_min'           : '46',
           'latitude_max'           : '62',
           'longitude_min'          : '-16',
           'longitude_max'          : '13',
           'depth_min'              : '-1',
           'depth_max'              : '1',
           'variable'               : settings['cmes_variable'],
           'out_dir'                : settings['dst_dir'],
           'out_name'               : settings['cmes_output'],
           'config_out'             : settings['config_location']
           }        
    
    chk = dl_cmes.chk_motu()
    
    if chk == 1:
        logger.error('motuclient not installed, please install by running $ pip install motuclient')
        
    else:
        logger.info('version ' +chk+ ' of motuclient is installed')
        
    dl = dl_cmes.request_cmes(cmes_config)


    
