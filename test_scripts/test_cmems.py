#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 15:49:52 2019

Test script to test download CMEMS data function in PyNEMO. To be incorprated
into profile.py

@author: thopri
"""
from pynemo import nemo_bdy_dl_cmems as dl_cmems
from pynemo import nemo_bdy_setup as setup
from calendar import monthrange
import sys
import time
import threading

Setup = setup.Setup('/Users/thopri/Projects/PyNEMO/inputs/namelist_cmems.bdy') # default settings file
settings = Setup.settings

if settings['use_cmems'] == True:

    if settings['year_end'] - settings['year_000'] > 0:
        date_min = settings['year_000']+'-01-01'
        date_max = settings['year_end']+'-12-31'

    days_mth = monthrange(settings['year_end'],settings['month_end'])

    date_min = str(settings['year_000'])+'-'+str(settings['month_000'])+'-01'

    date_max = str(settings['year_end'])+'-'+str(settings['month_end'])+'-'+str(days_mth[1])

    cmes_config= {
           'ini_config_template'    : settings['cmes_config_template'],
           'user'                   : settings['cmes_usr'],
           'pwd'                    : settings['cmes_pwd'],
           'motu_server'            : settings['motu_server'],
           'service_id'             : settings['cmes_model'],
           'product_id'             : settings['cmes_product'],
           'date_min'               : date_min,
           'date_max'               : date_max,
           'latitude_min'           : settings['latitude_min'],
           'latitude_max'           : settings['latitude_max'],
           'longitude_min'          : settings['longitude_min'],
           'longitude_max'          : settings['longitude_max'],
           'depth_min'              : settings['depth_min'],
           'depth_max'              : settings['depth_max'],
           'variable'               : settings['cmes_variable'],
           'src_dir'                : settings['src_dir'],
           'out_name'               : settings['cmes_output'],
           'config_out'             : settings['cmes_config']
           }

    chk = dl_cmems.chk_motu()

    dl = dl_cmems.request_CMEMS(cmes_config)

class progress_bar_loading(threading.Thread):

    def run(self):
            global stop
            global kill
            print 'Loading....  ',
            sys.stdout.flush()
            i = 0
            while stop != True:
                    if (i%4) == 0:
                        sys.stdout.write('\b/')
                    elif (i%4) == 1:
                        sys.stdout.write('\b-')
                    elif (i%4) == 2:
                        sys.stdout.write('\b\\')
                    elif (i%4) == 3:
                        sys.stdout.write('\b|')

                    sys.stdout.flush()
                    time.sleep(0.2)
                    i+=1

            if kill == True:
                print '\b\b\b\b ABORT!',
            else:
                print '\b\b done!',


kill = False
stop = False
p = progress_bar_loading()
p.start()

try:
    #anything you want to run.
    time.sleep(1)
    stop = True
except KeyboardInterrupt or EOFError:
         kill = True
         stop = True