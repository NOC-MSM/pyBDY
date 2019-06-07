# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

'''
Created on Wed Sep 12 08:02:46 2012

Parses a file to find out which nemo boundary settings to use 

@author John Kazimierz Farey
@author James Harle
$Last commit on:$
'''

# pylint: disable=E1103
# pylint: disable=no-name-in-module

#External imports
from collections import OrderedDict
import os
import logging

class Setup(object):
    '''
    Invoke with a text file location, class init reads and deciphers variables.

    attribute <settings> is a dict holding all the vars.
    '''
    """ This class holds the settings information """
    def __init__(self, setfile):
        """ Constructor, reads the settings file and sets the dictionary with setting name/key and
        it's value """
        #Logging for class
        self.logger = logging.getLogger(__name__)
        self.filename = setfile
        if not setfile: # debug
            self.filename = '../data/namelist.bdy'
        self._load_settings()
        self.variable_info = self.variable_info_reader(self.filename+'.info')

    def refresh(self):
        """ Re loads the settings from file """
        self._load_settings()
        
    def _load_settings(self):
        """ Loads the settings from file """
        try:
            namelist = open(self.filename, 'r')
        except:
            self.logger.error("Cannot open the file:"+self.filename)
            raise
        data = namelist.readlines()
        # Dictionary of all the vars in the file and a seperate settings for boolean values
        self.settings, self.bool_settings = _assign(_trim(data))
        namelist.close()
                
    def _get_var_name_value(self, line):
        """ splits the line into key value pair. """
        key_value = line.split("=", 2)
        name_prefix = key_value[0][0:2].lower()
        name = key_value[0][3:].lower().strip() # 3 -> 0 to keep type info
        value_str = key_value[1].strip()
        index = '-1'
        value = ''
        if name_prefix == 'ln':
            if value_str.find('true') is not -1:
                value = True
            elif value_str.find('false') is not -1:
                value = False
            else:
                raise ValueError('Cannot assign %s to %s, must be boolean' %(value_str, name))

        elif name_prefix == 'rn' or name_prefix == 'nn':
            if value_str.find('.') > -1 or value_str.find('e') > -1:
                try:
                    value = float(value_str)
                except ValueError:
                    self.logger.error('Cannot assign %s to %s, must be float')
                    raise
            else:
                try:
                    value = int(value_str)
                except ValueError:
                    self.logger.error('Cannot assign %s to %s, must be integer')
                    raise
        elif name_prefix == 'cn' or name_prefix == 'sn':
            value = value_str.strip("'")
            if name == 'dst_dir':
                value = os.path.join(value, '')
        elif name_prefix == 'cl':
            name = key_value[0].split('(')
            index = name[1].split(')')
            name = name[0].strip()
            index = index[0].strip()
            value = value_str
        else:
            raise ValueError('%s data type is ambiguous' %key_value)
        return name, index, value

    def write(self):
        '''
        This method write backs the variable data back into the file
        '''
        try:
            namelist = open(self.filename, 'r')
        except:
            self.logger.error("Cannot open the file:"+self.filename+" to write ")
            raise
        data = namelist.readlines()

        for name in self.settings:
            values = self.settings[name]
            if type(values).__name__ != 'dict':
                values = {'-1': values}
            for index, value in values.iteritems():
                count = -1
                for line in data:
#                    print line
                    count = count + 1
                    #find the variable
                    line_without_comments = strip_comments(line)
                    if line_without_comments == '':
                        continue
                    #print line_without_comments
                    data_name, data_index, data_value = self._get_var_name_value(line_without_comments)

                    if data_name == name:
                        #found the variable line
                        if data_index == index:
                            if type(data_value).__name__ == 'bool' \
                                and \
                               type(value).__name__ != 'bool':
                                data[count] = _replace_var_value(line, data_value,\
                                                                 self.bool_settings[name])
                                continue

                            if data_value == value:
                                break
                            else:
                                data[count] = _replace_var_value(line, data_value, value)
                                break
        namelist.close()
        namelist = open(self.filename, 'w')
        namelist.truncate()
        namelist.writelines(data)
        namelist.close()

    def variable_info_reader(self, filename):
        """ This method reads the variable description data from 'variable.info' file in the pynemo installation path
        if it can't find the file with the same name as input bdy file with extension .info
        Keyword arguments:
        filename -- filename of the variables information
        returns a dictionary with variable name and its description
        """
        variable_info = {}               
        if filename is None or not os.path.exists(filename):
            #Read the default file
            file_path, dummy = os.path.split(__file__)
            filename = os.path.join(file_path,'variable.info')
        try:
            namelist = open(filename, 'r')
            data = namelist.readlines()
            for line in data:
                name = _get_var_name(line)
                value = line.split("=", 1)[1]
                variable_info[name[0]] = value.strip()                           
        except IOError:
            self.logger.error("Cannot open the  variable file:"+filename)
        return variable_info
        
            
def _trim(data):
    """ Trims the sets of lines removing empty lines/whitespaces and removing comments
    which start with ! """
    newdata = []
    while data:
        line = data.pop(0)
        line = line.rsplit('!')[0].strip()
        if line is not '':
            newdata.append(line)
    return newdata

def _get_val(vars_dictionary, bool_vars_dictionary, line):
    """ traverses input string and appends the setting name and its value to dictionary
    of settings and also if the setting name holds a boolean value then to the dictionary
    of boolean variables. checks the type and raises error for ambiguous values"""

    logger = logging.getLogger(__name__)
    name_prefix = line[0][0:2].lower()
    name = line[0][3:].lower().strip() # 3 -> 0 to keep type info
    value = line[1].strip()

    if name_prefix == 'ln':
        if value.find('true') is not -1:
            if vars_dictionary.has_key(name) != True:
                vars_dictionary[name] = True
            bool_vars_dictionary[name] = True
        elif value.find('false') is not -1:
            if vars_dictionary.has_key(name) != True:
                vars_dictionary[name] = False
            bool_vars_dictionary[name] = False
        else:
            raise ValueError('Cannot assign %s to %s, must be boolean' %(value, name))

    elif name_prefix == 'rn' or name_prefix == 'nn':
        if value.find('.') > -1 or value.find('e') > -1:
            try:
                vars_dictionary[name] = float(value)
            except ValueError:
                logger.error('Cannot assign %s to %s, must be float')
                raise
        else:
            try:
                vars_dictionary[name] = int(value)
            except ValueError:
                logger.error('Cannot assign %s to %s, must be integer')
                raise
    elif name_prefix == 'cn' or name_prefix == 'sn':
        vars_dictionary[name] = value.strip("'")
        if name == 'dst_dir':
            vars_dictionary[name] = os.path.join(vars_dictionary[name], '')
    elif name_prefix == 'cl':
        name = line[0].split('(')
        index = name[1].split(')')
        if name[0].strip() not in vars_dictionary.keys():
            vars_dictionary[name[0].strip()] = {}
        vars_dictionary[name[0].strip()][index[0].strip()] = value.strip()
    else:
        raise ValueError('%s data type is ambiguous' %line)

def _replace_var_value(original_line, value, new_value):
    """ replaces the variable name value with new_value in the original_line"""
    if type(value).__name__ == 'bool':
        value = str(value).lower()
        new_value = str(new_value).lower()
    elif type(value).__name__ == 'str': #an empty string need to replace with ''
        print value, new_value
        if value == '':
            value = '\'\''
            new_value = '\''+new_value+'\''
    return original_line.replace(str(value), str(new_value), 1)

def _get_var_name(line):
    """ parses the line to find the name and if it is part of the array '()'
    then returns name of variable and index of the array. if variable is not
    array then only variable name and -1 in index"""
    name_value = line.split("=", 1)
    name_prefix = name_value[0][0:2].lower()
    name = name_value[0][3:].lower().strip() # 3 -> 0 to keep type info
    if name_prefix in ['ln', 'rn', 'nn', 'cn', 'sn']:
        return name, -1
    elif name_prefix == 'cl':
        name = name_value[0].split('(')
        index = name[1].split(')')
        return name[0], index[0]

    # Returns tidy dictionary of var names and values
def _assign(data):
    """ return a dictionary of variables and also special dictionary for boolean variable """
    vars_dictionary = OrderedDict({})
    bool_vars_dictionary = OrderedDict({})
    for line in data:
        keyvalue = line.split('=', 1)
        _get_val(vars_dictionary, bool_vars_dictionary, keyvalue)
    return vars_dictionary, bool_vars_dictionary

def strip_comments(line):
    """ strips the comments in the line. removes text after ! """
    line = line.rsplit('!')[0].strip()
    return line
