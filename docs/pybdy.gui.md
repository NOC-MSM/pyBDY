# pybdy.gui package

## Submodules

# pybdy.gui.mynormalize module

## *class* pybdy.gui.mynormalize.MyNormalize(stretch='linear', exponent=5, vmid=None, vmin=None, vmax=None, clip=False)

> Bases: `Normalize`<br>

A Normalize class for imshow that allows different stretching functions for astronomical images.

### *method* \_\_init\_\_(stretch='linear', exponent=5, vmid=None, vmin=None, vmax=None, clip=False)

Initialise an APLpyNormalize instance.

> Optional Keyword Parametersument<br>

> *vmin*: [ None | float ]<br>
> :   Minimum pixel value to use for the scaling.<br>

> *vmax*: [ None | float ]<br>
> :   Maximum pixel value to use for the scaling.<br>

> *stretch*: [ ‘linear’ | ‘log’ | ‘sqrt’ | ‘arcsinh’ | ‘power’ ]<br>
> :   The stretch function to use (default is ‘linear’).<br>

> *vmid*: [ None | float ]<br>
> :   Mid-pixel value used for the log and arcsinh stretches. If<br>
>     set to None, a default value is picked.<br>

> *exponent*: [ float ]<br>
> :   if self.stretch is set to ‘power’, this is the exponent to use.<br>

> *clip*: [ True | False ]<br>
> :   If clip is True and the given value falls outside the range,<br>
>     the returned value will be 0 or 1, whichever is closer.<br>

### *method* inverse(value)

Maps the normalized value (i.e., index in the colormap) back to image
data value.

> ### Parameters<br>

value

> \: Normalized value.<br>

# pybdy.gui.nemo_bdy_input_window module

Created on 21 Jan 2015.

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.gui.nemo_bdy_input_window.InputWindow(setup)

> Bases: `QDialog`<br>

Input Window for editing pyBDY settings.

### *method* \_\_init\_\_(setup)

Initialise the UI components.

# pybdy.gui.nemo_bdy_mask module

Mask Class to hold the mask information and operation on mask.

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.gui.nemo_bdy_mask.Mask(bathymetry_file=None, mask_file=None, min_depth=200.0, shelfbreak_dist=200.0)

> Bases: `object`<br>

Mask holder which reads from a netCDF bathymetry file and stores it in ‘data’ member variable.

### *method* \_\_init\_\_(bathymetry_file=None, mask_file=None, min_depth=200.0, shelfbreak_dist=200.0)

Initialise the Mask data.

### *method* add_mask(index, roi)

Add the masks for the given index values depending on the type of mask selected.

### *method* apply_border_mask(pixels)

Pixels is number of pixels in the border that need applying mask.

### *method* apply_mediterrian_mask()

Apply the mediterrian mask specific for the test bathymetry file.

### *method* fill_small_regions(index)

Fill the small regions of the selection area and fill them up.

### *method* mask_type *= 0*

### *method* min_depth *= 200.0*

### *method* remove_mask(index, roi)

Remove the mask for the given index values depending on the type of mask selected.

### *method* remove_small_regions(index)

Remove the small regions in the selection area and takes only the largest area for mask.

### *method* reset_mask()

Reset the data back to no mask with land fill.

### *method* save_mask(mask_file)

Read the mask data from the mask file.

### *method* select_the_largest_region()

Tide up the mask by selecting the largest masked region.

This is to avoid two disconnected masked regions.

### *method* set_bathymetry_file(bathy_file)

Read the bathymetry file and sets the land to 0 and ocean to 1.

### *method* set_mask_file(mask_file)

Read the mask data from the mask file.

Assumes the mask file is 2D.

### *method* set_mask_type(mask_type)

Set the mask type.

### *method* set_minimum_depth_mask(depth)

### *method* shelfbreak_dist *= 200.0*

# pybdy.gui.nemo_bdy_mask_gui module

Created on 12 Jan 2015.

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget(parent=None, mask=None, min_depth=200.0, shelfbreak_dist=200.0, \*args, \*\*kwargs)

> Bases: `QWidget`<br>

QWidget class for pyBDY mask plot.

### *method* \_\_init\_\_(parent=None, mask=None, min_depth=200.0, shelfbreak_dist=200.0, \*args, \*\*kwargs)

Initialise the mask, matplot and the navigation toolbar.

### *method* add_mask()

Add the selected region in the drawing tool to the mask.

### *method* apply_border_mask()

Apply a mask of given number of pixels at the border of the mask.

### *method* create_basemap()

Draws the basemap and contour with mask information.

### *method* drawing_tool_callback(toolname)

Run callback for the drawing tool when the signal of change of drawing tool is received.

### *method* mask_type *= 0*

### *method* min_depth *= 200.0*

### *method* remove_mask()

Remove the selected region in the drawing tool from the mask.

### *method* reset_mask()

### *method* save_mask_file(mask_file)

Save the mask data to mask_file.

### *method* set_bathymetry_file(bathymetry_filename, mask_file)

Set the bathymetry file.

### *method* set_mask_settings(min_depth, shelfbreak_dist)

Mask settings update.

### *method* set_mask_type(type)

Set the mask type.

### *method* shelfbreak_dist *= 200.0*

## *class* pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar(canvas, parent)

> Bases: `NavigationToolbar2QT`<br>

Custom toolbar for the nemo.

Includes additional buttons for drawing tool and (add,remove) for mask
in addtion to default NavigationToolbar provided by matplotlib.

### *method* \_\_init\_\_(canvas, parent)

Initialise the toolbar.

### *method* add_mask(\*dummy)

Run callback for add mask button clicked.

### *method* border(\*dummy)

Run callback for border button clicked.

### *method* drawing_tool

### *method* freehand(\*dummy)

Run callback for freehand button clicked.

### *method* get_active_button()

Return the current active button between freehand and rectangle.

### *method* max_depth_mask(\*dummy)

Enable the minimum height mask.

### *method* normal_mask(\*dummy)

Enable the normal mask button.

### *method* rectangle(\*dummy)

Run callback for rectangel button clicked.

### *method* remove_mask(\*dummy)

Run callback for remove mask button clicked.

### *method* reset(\*dummy)

Run callback for reset button clicked.

### *method* shelf_break_mask(\*dummy)

Enable the shelf break mask button.

### *method* update_height_mask(btn_id)

Update the height mask buttons in the interface.

## pybdy.gui.nemo_bdy_mask_gui.set_icon(name)

Create an icon based on the file found in the module directory with input name.

# pybdy.gui.nemo_bdy_namelist_edit module

Editor for namelist.bdy file.

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.gui.nemo_bdy_namelist_edit.NameListEditor(setup)

> Bases: `QWidget`<br>

GUI for the Namelist file options.

### *method* \_\_init\_\_(setup)

Initialise the constructor for setting up the gui using the settings.

### *method* bathymetry_update

### *method* combo_index_changed(value, name)

Run callback for the dropdown in the settings.

Run callback when the True/False dropdown for the settings,

> \: which has a boolean value, is changed.<br>

### *method* init_ui()

Initialise the UI components of the GUI.

### *method* label_changed(value, name)

Run callback when the text is changed in the text box.

### *method* mask_settings_update

### *method* mask_update

### *method* new_settings *= {}*

### *method* state_changed(state, name)

Run callback when the check box state is changed.

This updates the bool_setting.

# pybdy.gui.nemo_ncml_generator module

Created on 6 Aug 2015.

> @author: Shirley Crompton, UK Science and Technology Facilities Council<br>

## *class* pybdy.gui.nemo_ncml_generator.Ncml_generator(basefile)

> Bases: `QDialog`<br>

Gui editor to capture user input.

This is done for the purpose of generating NCML representation of pybdy source datasets.

### *method* \_\_init\_\_(basefile)

Initialise the UI components.

### *method* enable_btn_update(enable_btn)

### *method* enable_tab(enable_btn)

### *method* generate()

### *method* generateNcML(tabsList)

### *method* get_fname()

### *method* get_fname_input()

### *method* indent(elem, level=0)

### *method* initUI()

### *method* url_trawler(url, expr)

# pybdy.gui.nemo_ncml_tab_widget module

Created on 2 Jul 2015.

> @author: Shirley Crompton, UK Science and Technology Facilities Council<br>

## *class* pybdy.gui.nemo_ncml_tab_widget.Ncml_tab(tabName)

> Bases: `QWidget`<br>

Tab contents to define child aggregation.

### *method* \_\_init\_\_(tabName)

Initialise the UI components.

### *method* add_tab()

### *method* initUI()

### *method* resetValues(currentValues=None)

### *method* reset_tab()

### *method* setWidgetStack()

### *method* src_combo_changed(var_name)

### *method* src_tedit_edited()

## *class* pybdy.gui.nemo_ncml_tab_widget.ncml_variable(varName, old_name='')

> Bases: `object`<br>

convenient class to hold the values for a ncml variable.

### *method* \_\_init\_\_(varName, old_name='')

# pybdy.gui.selection_editor module

Code has been taken from matlibplot polygon interaction.

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.gui.selection_editor.BoxEditor(axes, canvas)

> Bases: `object`<br>

Box editor is to select area using rubber band sort of drawing rectangle.

It uses matplotlib RectangleSelector under the hood.

### *method* \_\_init\_\_(axes, canvas)

Initialise class and creates a rectangle selector.

### *method* disable()

Disable or removes the box selector.

### *method* enable()

Enable the box selector.

### *method* line_select_callback(eclick, erelease)

Run callback to the rectangleselector.

### *method* polygon *= None*

### *method* reset()

Reset the Box selector.

### *method* reset_polygon()

Reset rectangle polygon.

## *class* pybdy.gui.selection_editor.PolygonEditor(axis, canvas)

> Bases: `object`<br>

Editor for the polygons drawn on the map.

### *method* \_\_init\_\_(axis, canvas)

Initialise the editable polygon object.

### *method* add_point(xval, yval)

Add an new point to the selection list and redraws the selection tool.

### *method* button_press_callback(event)

Run callback to mouse press event.

### *method* button_release_callback(event)

Run callback to mouse release event.

### *method* delete_datapoint(event)

Delete the data point under the point in event.

### *method* disable()

Disable the events and the selection.

### *method* draw_callback(dummy_event)

Draw the selection object.

### *method* draw_line()

Draw the line if available.

### *method* draw_polygon()

Draw polygon if available.

### *method* enable()

Enable the selection.

### *method* epsilon *= 3*

### *method* get_index_under_point(event)

Get the index of the point under the event (mouse click).

### *method* insert_datapoint(event)

Insert a new data point between the segment that is closest in polygon.

### *method* motion_notify_callback(event)

Run callback for the mouse motion with button press.

This is to move the edge points of the polygon.

### *method* polygon_changed(poly)

Redraw the polygon.

### *method* refresh()

Refresh the canvas.

This method looks at the list of points available and depending on the number of points

> \: in the list creates a point or line or a polygon and draws them.<br>

### *method* reset()

Reset the points in the selection deleting the line and polygon.

### *method* reset_line()

Reset the line i.e removes the line from the axes and resets to None.

### *method* reset_polygon()

Reset the polygon ie. removes the polygon from the axis and reset to None.

### *method* set_visibility(status)

Set the visibility of the selection object.

### *method* show_verts *= True*

## Module contents
