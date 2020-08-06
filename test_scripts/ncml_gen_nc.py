# import os
# import jnius_config
# ncmlpath, file_name = os.path.split(__file__)
# ncmlpath = os.path.join(ncmlpath, "jars", "netcdfAll-4.6.jar")
# jnius_config.set_classpath('.',ncmlpath)
#
# from jnius import autoclass
#
# ncml_template = "/Users/thopri/Projects/PyNEMO/inputs/NEMO_output_T.ncml"
# nc_file = "/Users/thopri/Projects/PyNEMO/test_scripts/test.nc"
#
# NcMLReader = autoclass('ucar.nc2.ncml.NcMLReader')
# dataset2 = NcMLReader.writeNcMLToFile(ncml_template,nc_file)


#NetcdfDataset ncfileIn = NcMLReader.readNcML (ncml_filename, null);

import xml.etree.ElementTree as ET
import xmltodict
ncml = "/Users/thopri/Projects/PyNEMO/inputs/NEMO_output_T.ncml"
ncml_xml = xmltodict.parse(ET.tostring(ET.parse(ncml).getroot()))

dimensions = ncml_xml['ns0:netcdf']['ns0:dimension']
variables = ncml_xml['ns0:netcdf']['ns0:variable']
nc_attrib = ncml_xml['ns0:netcdf']['ns0:attribute']
var_attrib = ncml_xml['ns0:netcdf']['ns0:variable'][0]['ns0:attribute']

print('the end')
# for key in ncml_meta:
#     for key2 in ncml_meta[key]:
#         if 'dimension' in key2:
#             print(key2)


# def find(key, dictionary):
#     for k, v in dictionary.items():
#         if k in key:
#             yield dictionary
#         elif isinstance(v, dict):
#             for result in find(key, v):
#                 yield result
#         elif isinstance(v, list):
#             for d in v:
#                 if isinstance(d, dict):
#                     for result in find(key, d):
#                         yield result
#
# print(list(find("ns0:dimension", ncml_meta)))