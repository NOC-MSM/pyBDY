# pybdy.reader package

## Submodules

# pybdy.reader.directory module

Abstraction for the data repository.

> @author: Mr. Srikanth Nagella.<br>

## *class* pybdy.reader.directory.GridGroup

> Bases: `object`<br>

### *method* \_\_init\_\_()

### *method* get_meta_data(variable, source_dic)

Return a dictionary with meta data information correspoinding to the variable.

## *class* pybdy.reader.directory.Reader(directory, time_adjust)

> Bases: `object`<br>

Reader for all the files in the directory as one single object.

## Examples

reader = Reader(“Folder path”)

> reader[“t”][“votemper”][:, :, :, :]<br>

### *method* \_\_init\_\_(directory, time_adjust)

Take in directory path as input and return the required information to the bdy.

> ### Parameters<br>

> directory : The directory in which to look for the files<br>
> time_adjust : amount of time to be adjusted to the time read from file.<br>

> ### Returns<br>

> None : object<br>

### *method* calculate_time_interval()

Calculate the time interval of the each grid.

If all the grids get the same interval then it sets it to the days and hours.
Otherwise it throws an error.

### *method* delta_time_interval(time1, time2)

Get the difference between the two times in days and hours.

### *method* get_dir_list(grid)

Scan the directory for a input grid related NetCDF files (i.e., ending with the grid name.

> ### Parameters<br>

> grid (str) : grid name eg. ‘t’,’v’,’u’,’i’.<br>

> ### Returns<br>

> dir_list (list) : list of files<br>

### *method* get_source_timedata(grid, t_adjust)

Get the source time data information.

Builds up sourcedata objects of a given grid.

### *method* grid_type_list *= ['t', 'u', 'v', 'i']*

## *class* pybdy.reader.directory.Variable(filenames, variable)

> Bases: `object`<br>

### *method* \_\_init\_\_(filenames, variable)

### *method* get_attribute_values(attr_name)

Return the attribute value of the variable.

### *method* get_dimensions()

Return the dimensions of the variables.

### *method* set_time_dimension_index()

Set the time dimension index.

### *method* time_counter_const *= 'time_counter'*

# pybdy.reader.factory module

Generic file loader factory.

> @author: Mr. Srikanth Nagella<br>

## pybdy.reader.factory.GetFile(uri)

## pybdy.reader.factory.GetReader(uri, t_adjust, reader_type=None)

## *class* pybdy.reader.factory.NetCDFFile(filename)

> Bases: `object`<br>

### *method* \_\_init\_\_(filename)

### *method* close()

# pybdy.reader.ncml module

NcML reading implementation using pyjnius.

> @author: Mr. Srikanth Nagella.<br>

## *class* pybdy.reader.ncml.GridGroup(filename, dataset)

> Bases: `object`<br>

Class that provides an indirection to the grid type.

Since ncml file has aggregation of all the variables this is just a place holder.

### *method* \_\_init\_\_(filename, dataset)

Source data that holds the dataset information.

### *method* get_meta_data(variable, source_dic)

Return a dictionary with meta data information correspoinding to the variable.

### *method* logger *= \<Logger pybdy.reader.ncml (INFO)>*

### *method* update_atrributes()

Update the units and calendar information for the grid.

## *class* pybdy.reader.ncml.NcMLFile(filename)

> Bases: `object`<br>

### *method* \_\_init\_\_(filename)

### *method* close()

## *class* pybdy.reader.ncml.Reader(uri, time_adjust)

> Bases: `object`<br>

High level object for the NCML reader, from here using grid type will return the grid data.

## Examples

reader = Reader(“NCML Filename”)

> reader[“t”][“votemper”][:, :, :, :]<br>

### *method* \_\_init\_\_(uri, time_adjust)

### *method* close()

Not yet implemented.

### *method* grid_type_list *= ['t', 'u', 'v', 'i']*

### *method* time_counter *= 'time_counter'*

## *class* pybdy.reader.ncml.Variable(dataset, variable)

> Bases: `object`<br>

### *method* \_\_init\_\_(dataset, variable)

### *method* get_attribute_value(attr_name)

Return the attribute value of the variable.

## pybdy.reader.ncml.init_jnius()

## Module contents
