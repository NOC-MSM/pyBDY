'''
NCML python parser using XML to Dict
'''

import xml.etree.ElementTree as ET
import xmltodict
import logging

logger = logging.getLogger(__name__)

def gen_dims_NCML(ncmlfile,orgName):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    dimensions = ncml_dict['ns0:netcdf']['ns0:dimension']
    if type(dimensions) is not list:
        dimensions = [dimensions]
    if not any(d['@orgName'] == orgName for d in dimensions):
        raise ValueError('dimension name not defined in NCML output specification file')
    for i in range(len(dimensions)):
        if dimensions[i]['@orgName'] == orgName:
            dim_name = dimensions[i]['@name']
            break
    return dim_name

def gen_var_list_NCML(ncmlfile, time):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    variables = ncml_dict['ns0:netcdf']['ns0:variable']
    var_3D = []
    var_2D = []
    for i in range(len(variables)):
        if len(variables[i]['@shape'].split(' ')) == 4 and variables[i]['@shape'].split(' ')[0] == time:
            var_3D.append(variables[i]['@name'])
        if len(variables[i]['@shape'].split(' ')) == 3 and variables[i]['@shape'].split(' ')[0] == time:
            var_2D.append(variables[i]['@name'])
    var_type = {'3D_vars': var_3D,
                '2D_vars': var_2D,
                }
    return var_type

def gen_src_var_list_NCML(ncmlfile):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    variables = ncml_dict['ns0:netcdf']['ns0:variable']
    var_list = []
    for i in range(len(variables)):
        var_list.append(variables[i]['@name'])
    return var_list

def gen_var_NCML(ncmlfile, orgName):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    variables = ncml_dict['ns0:netcdf']['ns0:variable']
    if type(variables) is not list:
        variables = [variables]
    if not any(d['@orgName'] == orgName for d in variables):
        raise ValueError('variable name not defined in NCML output specification file')
    var = {}
    for i in range(len(variables)):
        if variables[i]['@orgName'] == orgName:
            var['name'] = variables[i]['@name']
            var['shape'] = variables[i]['@shape'].split(' ')
            if variables[i]['@type'] == 'float':
                var['type'] = 'f4'
            if variables[i]['@type'] == 'int':
                var['type'] = 'i4'
            break
    return var

def gen_attrib_NCML(ncmlfile,name):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    nc_attrib = ncml_dict['ns0:netcdf']['ns0:attribute']
    if type(nc_attrib) is not list:
        nc_attrib = [nc_attrib]
    if not any(d['@name'] == name for d in nc_attrib):
        logger.warning('Global attribute name not found, writing attribute not specified')
        return 'Global attribute not specified in NCML file'
    for i in range(len(nc_attrib)):
        if nc_attrib[i]['@name'] == name:
            attrib_val = nc_attrib[i]['@value']
    return attrib_val

def gen_var_attrib_NCML(ncmlfile, variable,name):
    ncml_dict = xmltodict.parse(ET.tostring(ET.parse(ncmlfile).getroot()))
    variables = ncml_dict['ns0:netcdf']['ns0:variable']
    if type(variables) is not list:
        variables = [variables]
    for i in range(len(variables)):
        if variables[i]['@name'] == variable:
            if not any(d['@name'] == name for d in variables[i]['ns0:attribute']):
                logging.warning('variable attribute name not found, writing attribute not specified')
                return 'Variable attribute not specified in NCML file'
            for j in range(len(variables[i]['ns0:attribute'])):
                if variables[i]['ns0:attribute'][j]['@name'] == name:
                    attrib = variables[i]['ns0:attribute'][j]['@value']
                    break
            break
    return attrib