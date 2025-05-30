# pybdy.reader package

## Submodules

## pybdy.reader.directory module

Abstraction for the data repository.

@author: Mr. Srikanth Nagella.

### *class* pybdy.reader.directory.GridGroup

Bases: `object`

#### \_\_init\_\_()

#### get_meta_data(variable, source_dic)

Return a dictionary with meta data information correspoinding to the variable.

### *class* pybdy.reader.directory.Reader(directory, time_adjust)

Bases: `object`

Reader for all the files in the directory as one single object.

### Examples

```pycon
>>> reader = Reader("Folder path")
>>> reader["t"]["votemper"][:, :, :, :]
```

#### \_\_init\_\_(directory, time_adjust)

Take in directory path as input and return the required information to the bdy.

#### Keyword Arguments:

directory – The directory in which to look for the files
time_adjust – amount of time to be adjusted to the time read from file.

#### grid_type_list *= ['t', 'u', 'v', 'i']*

### *class* pybdy.reader.directory.Variable(filenames, variable)

Bases: `object`

#### \_\_init\_\_(filenames, variable)

#### get_attribute_values(attr_name)

Return the attribute value of the variable.

#### time_counter_const *= 'time_counter'*

## pybdy.reader.factory module

Generic file loader factory.

@author: Mr. Srikanth Nagella

### pybdy.reader.factory.GetFile(uri)

### pybdy.reader.factory.GetReader(uri, t_adjust, reader_type=None)

### *class* pybdy.reader.factory.NetCDFFile(filename)

Bases: `object`

#### \_\_init\_\_(filename)

#### close()

## pybdy.reader.ncml module

NcML reading implementation using pyjnius.

@author: Mr. Srikanth Nagella.

### *class* pybdy.reader.ncml.GridGroup(filename, dataset)

Bases: `object`

Class that provides an indirection to the grid type.

### Notes

Since ncml file has aggregation of all the variables this is just a place holder.

#### \_\_init\_\_(filename, dataset)

Source data that holds the dataset information.

#### get_meta_data(variable, source_dic)

Return a dictionary with meta data information correspoinding to the variable.

#### logger *= \<Logger pybdy.reader.ncml (INFO)>*

#### update_atrributes()

Update the units and calendar information for the grid.

### *class* pybdy.reader.ncml.NcMLFile(filename)

Bases: `object`

#### \_\_init\_\_(filename)

#### close()

### *class* pybdy.reader.ncml.Reader(uri, time_adjust)

Bases: `object`

High level object for the NCML reader, from here using grid type will return the grid data.

### Examples

```pycon
>>> reader = Reader("NCML Filename")
>>> reader["t"]["votemper"][:, :, :, :]
```

#### \_\_init\_\_(uri, time_adjust)

#### close()

Not yet implemented.

#### grid_type_list *= ['t', 'u', 'v', 'i']*

#### time_counter *= 'time_counter'*

### *class* pybdy.reader.ncml.Variable(dataset, variable)

Bases: `object`

#### \_\_init\_\_(dataset, variable)

#### get_attribute_value(attr_name)

Return the attribute value of the variable.

### pybdy.reader.ncml.init_jnius()

## Module contents
