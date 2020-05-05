#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri May 01 2020

@author: thopri
example usage:
from pynemo.tides import nemo_tide_test as tt
tt.main()

all parameters have defaults applied if not supplied:
location of bdy file - 'inputs/namelist_cmems.bdy'
amplitude threshold - 0.25 m
phase threshold - 10.00 degrees
model resolution - 1/16 degree
model - 'fes'

The script generates a excel spreadsheet that contains the locations and amplitudes and phases for all HC's
defined in the bdy file that exceed the default or defined the thresholds passed to the main function.
File locations e.g. model reference location etc are all taken from bdy file that is passed to the main function

To do this the script compiles a list of PyNEMO boundary amplitudes and phases and lat/lon's, finds the closest value
in the reference model (currently only FES is supported), and then compares them. If the absolute difference is greater
than defined threshold then the location and parameter (either Amp or Phase) is returned within a Pandas Dataframe
which is then written to a spreadsheet.

Notes:
The script checks the Amplitude and Phase independently, so lat/lons for each are also returned. Each HC is saved to
a separate sheet in the spreadsheet. The name of the spreadsheet contains meta data showing thresholds and reference
model used.

"""
from netCDF4 import Dataset
import numpy as np
import logging
import time
import pandas as pd
from pynemo import nemo_bdy_setup as setup

# log to PyNEMO log file
logger = logging.getLogger(__name__)
logging.basicConfig(filename='nrct.log', level=logging.INFO)

# TODO: add TPXO comparision functionality currently only uses FES as "truth"

def main(bdy_file='inputs/namelist_cmems.bdy',amplitude_threshold = 0.25,phase_threshold=10.00,model_res=1/16,model='fes'):
    logger.info('============================================')
    logger.info('Start Tide Test Logging: ' + time.asctime())
    logger.info('============================================')
    # get settings dict based on bdy file
    Setup = setup.Setup(bdy_file)  # default settings file
    settings = Setup.settings
    constituents = settings['clname']
    # TODO maybe define grids in bdy file? at the moment Z, U and Vs are generated no option for Z only.
    grids = ['Z','U','V']
    if model == 'fes':
        logger.info('using FES as reference.......')
        # open writer object to write pandas dataframes to spreadsheet
        writer = pd.ExcelWriter(settings['dst_dir'] + 'exceed_values_amp_thres-'+str(amplitude_threshold)+'_phase_thres-'+str(phase_threshold)+'_reference_model-'+str(model)+'.xlsx', engine='xlsxwriter')
        for key in constituents:
            for j in range(len(grids)):
                out_fname = settings['dst_dir']+settings['fn']+'_bdytide_'+constituents[key].strip("',/\n")+'_grd_'+grids[j]+'.nc'
                logger.info('processing output file '+out_fname)
                fes_fname = settings['tide_fes']+constituents[key].strip("',/\n")+'_'+grids[j]+'.nc'
                # read in FES data (whole globe)
                fes = read_fes(fes_fname, grids[j])
                grid = grids[j].lower()
                # extract PyNEMO data from output files (generate list of lats,lons etc)
                pynemo_out = extract_PyNEMO_output(out_fname, grid)
                # subset FES to match PyNEMO list of lat lons
                subset = subset_FES(pynemo_out, fes)
                # compare the two lists (or dicts really)
                error_log = compare_tides(pynemo_out, subset, amplitude_threshold, phase_threshold, model_res)
                # return differences above threshold as a Pandas Dataframe and name using HC and Grid
                error_log.name = constituents[key].strip("',/\n") + grids[j]
                # if the dataframe is empty (no exceedance) then discard dataframe and log
                if error_log.empty == True:
                    logger.info(
                        'output file does not exceed threshold when compared with reference model..... thats good!')
                # if dataframe has values then these exceed the threshold, log and save to excel spreadsheet using dataset
                # name e.g. M2Z (based on HC and grid) as name for the sheet
                if error_log.empty == False:
                    logger.warning(
                        'Exceedance in thesholds detected, check spreadsheet in dst_dir')
                    error_log.to_excel(writer,sheet_name=error_log.name)
                # close writer object and save excel spreadsheet
                writer.save()
    # code runs here if TPXO is requested as reference this hasn't been written yet so raises exception
    elif model == 'tpxo':
        logger.exception('not set up to use TPXO yet...... exiting')
        raise Exception('Not setup for TPXO use FES instead?')
    # everything else goes here which shouldn't happen so is raised as an exception
    else:
        logger.exception('Tide reference model not recognised.... exiting')
        raise Exception('Invalid tide referece model name provided')
    return 0

    # find nearest value in array used for finding subset of Lat and Lon
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

    # extract PyNEMO output from netcdf file, convert HcosG and HsinG to Amp and Phase
    # and extract lons and lats from I and J coords. return a dict
def extract_PyNEMO_output(out_fname,grid):
    tide_out = Dataset(out_fname)
    nav_lat = tide_out.variables['nav_lat'][:]
    nav_lon = tide_out.variables['nav_lon'][:]
    nbidta = tide_out.variables['nbidta'][:]
    nbjdta = tide_out.variables['nbjdta'][:]
    cosine = np.array(tide_out.variables[grid+'1'][:])
    sine = np.array(tide_out.variables[grid+'2'][:])
    amp = np.hypot(sine,cosine)
    phase = np.arctan2(sine[0,:],cosine[0,:])
    phase = np.degrees(phase)
    lat = np.array(nav_lat[nbjdta, nbidta])
    lon = np.array(nav_lon[nbjdta, nbidta])
    pynemo_out = {'lat':lat,'lon':lon,'amp':amp,'phase':phase}
    return pynemo_out

    # read FES netcdf file, convert lon to -180 to 180, rather than 0-360
    # return a dict
def read_fes(fes_fname,grid):
    fes_tide = Dataset(fes_fname)
    if grid == 'Z':
        fes_amp = np.array(fes_tide.variables['amplitude'][:])
        fes_phase = np.array(fes_tide.variables['phase'][:])
        fes_phase[fes_phase > 180.0] = fes_phase[fes_phase > 180.0] - 360.0
    if grid != 'Z':
        fes_amp = np.array(fes_tide.variables[grid+'a'][:])
        fes_phase = np.array(fes_tide.variables[grid+'g'][:])
        fes_phase[fes_phase > 180.0] = fes_phase[fes_phase > 180.0] - 360.0

    fes_lat = fes_tide.variables['lat'][:]
    fes_lon = fes_tide.variables['lon'][:]
    # change to -180 to 180 lonitude convention
    fes_lon[fes_lon > 180.0] = fes_lon[fes_lon > 180.0] - 360.0
    fes_dict = {'lat':fes_lat,'lon':fes_lon,'amp':fes_amp,'phase':fes_phase}
    return fes_dict

    # subset FES dict from read_FES, this uses find_nearest to find nearest FES point using PyNEMO dict from extract_PyNEMO
    # It also converts FES amplitude from cm to m.
def subset_FES(pynemo_out, fes):
    idx_lat = np.zeros(np.shape(pynemo_out['lat']))
    for i in range(np.shape(pynemo_out['lat'])[1]):
        idx_lat[0, i] = find_nearest(fes['lat'], pynemo_out['lat'][0, i])
    idx_lat = idx_lat.astype(np.int64)

    idx_lon = np.zeros(np.shape(pynemo_out['lon']))
    for i in range(np.shape(pynemo_out['lon'])[1]):
        idx_lon[0, i] = find_nearest(fes['lon'], pynemo_out['lon'][0, i])
    idx_lon = idx_lon.astype(np.int64)

    fes_amp_sub = fes['amp'][idx_lat, idx_lon]
    fes_amp_sub = fes_amp_sub/100
    fes_phase_sub = fes['phase'][idx_lat, idx_lon]
    fes_lat_sub = fes['lat'][idx_lat]
    fes_lon_sub = fes['lon'][idx_lon]
    subset = {'lat':fes_lat_sub,'lon':fes_lon_sub,'amp':fes_amp_sub,'phase':fes_phase_sub}
    return subset

    # takes pynemo extract dict, subset fes dict, and the thresholds and model res passed to main function.
    # returns a Pandas Dataframe with any PyNEMO values that exceed the nearest FES point by defined threshold
    # It also checks lats and lons are within the model reference resolution
    # i.e. ensure closest model reference point is used.
def compare_tides(pynemo_out,subset_fes,amp_thres,phase_thres,model_res):
    # compare lat and lons
    diff_lat = np.abs(pynemo_out['lat']-subset_fes['lat'])
    diff_lon = np.abs(pynemo_out['lon'] - subset_fes['lon'])
    exceed_lat = diff_lat > model_res
    exceed_lon = diff_lon > model_res
    exceed_sum = np.sum(exceed_lat+exceed_lon)
    if exceed_sum > 0:
        raise Exception('Dont Panic: Lat and/or Lon further away from model point than model resolution')
    # compare amp
    abs_amp = np.abs(pynemo_out['amp']-subset_fes['amp'])
    abs_amp_thres = abs_amp > amp_thres
    err_amp = pynemo_out['amp'][abs_amp_thres].tolist()
    err_amp_lats = pynemo_out['lat'][abs_amp_thres].tolist()
    err_amp_lons = pynemo_out['lon'][abs_amp_thres].tolist()

    # compare phase
    abs_ph = np.abs(pynemo_out['phase']-subset_fes['phase'])
    abs_ph_thres = abs_ph > phase_thres
    err_pha = pynemo_out['phase'][abs_ph_thres[0,:]].tolist()
    err_pha_lats = pynemo_out['lat'][abs_ph_thres].tolist()
    err_pha_lons = pynemo_out['lon'][abs_ph_thres].tolist()

    lerr_pha, lerr_amp = len(err_pha), len(err_amp)
    max_len = max(lerr_pha, lerr_amp)
    if not max_len == lerr_pha:
        err_pha.extend([''] * (max_len - lerr_pha))
        err_pha_lats.extend([''] * (max_len - lerr_pha))
        err_pha_lons.extend([''] * (max_len - lerr_pha))
    if not max_len == lerr_amp:
        err_amp.extend([''] * (max_len - lerr_amp))
        err_amp_lats.extend([''] * (max_len - lerr_amp))
        err_amp_lons.extend([''] * (max_len - lerr_amp))

    err_log = pd.DataFrame({'amp_lat':err_amp_lats,
                            'amp_lon':err_amp_lons,
                            'amp':err_amp,
                            'phase_lat':err_pha_lats,
                            'phase_lon':err_pha_lons,
                            'phase':err_pha})


    return err_log

if __name__ == '__main__':
    main()





