# pybdy package

## Subpackages

- [pybdy.gui package](pybdy.gui.md)
    - [Submodules](pybdy.gui.md#submodules)
    - [pybdy.gui.mynormalize module](pybdy.gui.md#module-pybdy.gui.mynormalize)
        - [`MyNormalize`](pybdy.gui.md#pybdy.gui.mynormalize.MyNormalize)
            - [`MyNormalize.__init__()`](pybdy.gui.md#pybdy.gui.mynormalize.MyNormalize.__init__)
            - [`MyNormalize.inverse()`](pybdy.gui.md#pybdy.gui.mynormalize.MyNormalize.inverse)
    - [pybdy.gui.nemo_bdy_input_window module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_input_window)
        - [`InputWindow`](pybdy.gui.md#pybdy.gui.nemo_bdy_input_window.InputWindow)
            - [`InputWindow.__init__()`](pybdy.gui.md#pybdy.gui.nemo_bdy_input_window.InputWindow.__init__)
    - [pybdy.gui.nemo_bdy_mask module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_mask)
        - [`Mask`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask)
            - [`Mask.__init__()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.__init__)
            - [`Mask.add_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.add_mask)
            - [`Mask.apply_border_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.apply_border_mask)
            - [`Mask.apply_mediterrian_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.apply_mediterrian_mask)
            - [`Mask.fill_small_regions()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.fill_small_regions)
            - [`Mask.mask_type`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.mask_type)
            - [`Mask.min_depth`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.min_depth)
            - [`Mask.remove_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.remove_mask)
            - [`Mask.remove_small_regions()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.remove_small_regions)
            - [`Mask.reset_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.reset_mask)
            - [`Mask.save_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.save_mask)
            - [`Mask.select_the_largest_region()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.select_the_largest_region)
            - [`Mask.set_bathymetry_file()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.set_bathymetry_file)
            - [`Mask.set_mask_file()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.set_mask_file)
            - [`Mask.set_mask_type()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.set_mask_type)
            - [`Mask.set_minimum_depth_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.set_minimum_depth_mask)
            - [`Mask.shelfbreak_dist`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask.Mask.shelfbreak_dist)
    - [pybdy.gui.nemo_bdy_mask_gui module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_mask_gui)
        - [`MatplotlibWidget`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget)
            - [`MatplotlibWidget.__init__()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.__init__)
            - [`MatplotlibWidget.add_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.add_mask)
            - [`MatplotlibWidget.apply_border_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.apply_border_mask)
            - [`MatplotlibWidget.create_basemap()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.create_basemap)
            - [`MatplotlibWidget.drawing_tool_callback()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.drawing_tool_callback)
            - [`MatplotlibWidget.mask_type`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.mask_type)
            - [`MatplotlibWidget.min_depth`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.min_depth)
            - [`MatplotlibWidget.remove_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.remove_mask)
            - [`MatplotlibWidget.reset_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.reset_mask)
            - [`MatplotlibWidget.save_mask_file()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.save_mask_file)
            - [`MatplotlibWidget.set_bathymetry_file()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.set_bathymetry_file)
            - [`MatplotlibWidget.set_mask_settings()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.set_mask_settings)
            - [`MatplotlibWidget.set_mask_type()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.set_mask_type)
            - [`MatplotlibWidget.shelfbreak_dist`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.MatplotlibWidget.shelfbreak_dist)
        - [`NemoNavigationToolbar`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar)
            - [`NemoNavigationToolbar.__init__()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.__init__)
            - [`NemoNavigationToolbar.add_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.add_mask)
            - [`NemoNavigationToolbar.border()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.border)
            - [`NemoNavigationToolbar.drawing_tool`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.drawing_tool)
            - [`NemoNavigationToolbar.freehand()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.freehand)
            - [`NemoNavigationToolbar.get_active_button()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.get_active_button)
            - [`NemoNavigationToolbar.max_depth_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.max_depth_mask)
            - [`NemoNavigationToolbar.normal_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.normal_mask)
            - [`NemoNavigationToolbar.rectangle()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.rectangle)
            - [`NemoNavigationToolbar.remove_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.remove_mask)
            - [`NemoNavigationToolbar.reset()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.reset)
            - [`NemoNavigationToolbar.shelf_break_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.shelf_break_mask)
            - [`NemoNavigationToolbar.update_height_mask()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.NemoNavigationToolbar.update_height_mask)
        - [`set_icon()`](pybdy.gui.md#pybdy.gui.nemo_bdy_mask_gui.set_icon)
    - [pybdy.gui.nemo_bdy_namelist_edit module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_namelist_edit)
        - [`NameListEditor`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor)
            - [`NameListEditor.__init__()`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.__init__)
            - [`NameListEditor.bathymetry_update`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.bathymetry_update)
            - [`NameListEditor.combo_index_changed()`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.combo_index_changed)
            - [`NameListEditor.init_ui()`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.init_ui)
            - [`NameListEditor.label_changed()`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.label_changed)
            - [`NameListEditor.mask_settings_update`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.mask_settings_update)
            - [`NameListEditor.mask_update`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.mask_update)
            - [`NameListEditor.new_settings`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.new_settings)
            - [`NameListEditor.state_changed()`](pybdy.gui.md#pybdy.gui.nemo_bdy_namelist_edit.NameListEditor.state_changed)
    - [pybdy.gui.nemo_ncml_generator module](pybdy.gui.md#module-pybdy.gui.nemo_ncml_generator)
        - [`Ncml_generator`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator)
            - [`Ncml_generator.__init__()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.__init__)
            - [`Ncml_generator.enable_btn_update()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.enable_btn_update)
            - [`Ncml_generator.enable_tab()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.enable_tab)
            - [`Ncml_generator.generate()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.generate)
            - [`Ncml_generator.generateNcML()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.generateNcML)
            - [`Ncml_generator.get_fname()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.get_fname)
            - [`Ncml_generator.get_fname_input()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.get_fname_input)
            - [`Ncml_generator.indent()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.indent)
            - [`Ncml_generator.initUI()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.initUI)
            - [`Ncml_generator.url_trawler()`](pybdy.gui.md#pybdy.gui.nemo_ncml_generator.Ncml_generator.url_trawler)
    - [pybdy.gui.nemo_ncml_tab_widget module](pybdy.gui.md#module-pybdy.gui.nemo_ncml_tab_widget)
        - [`Ncml_tab`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab)
            - [`Ncml_tab.__init__()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.__init__)
            - [`Ncml_tab.add_tab()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.add_tab)
            - [`Ncml_tab.initUI()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.initUI)
            - [`Ncml_tab.resetValues()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.resetValues)
            - [`Ncml_tab.reset_tab()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.reset_tab)
            - [`Ncml_tab.setWidgetStack()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.setWidgetStack)
            - [`Ncml_tab.src_combo_changed()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.src_combo_changed)
            - [`Ncml_tab.src_tedit_edited()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.Ncml_tab.src_tedit_edited)
        - [`ncml_variable`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.ncml_variable)
            - [`ncml_variable.__init__()`](pybdy.gui.md#pybdy.gui.nemo_ncml_tab_widget.ncml_variable.__init__)
    - [pybdy.gui.selection_editor module](pybdy.gui.md#module-pybdy.gui.selection_editor)
        - [`BoxEditor`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor)
            - [`BoxEditor.__init__()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.__init__)
            - [`BoxEditor.disable()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.disable)
            - [`BoxEditor.enable()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.enable)
            - [`BoxEditor.line_select_callback()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.line_select_callback)
            - [`BoxEditor.polygon`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.polygon)
            - [`BoxEditor.reset()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.reset)
            - [`BoxEditor.reset_polygon()`](pybdy.gui.md#pybdy.gui.selection_editor.BoxEditor.reset_polygon)
        - [`PolygonEditor`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor)
            - [`PolygonEditor.__init__()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.__init__)
            - [`PolygonEditor.add_point()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.add_point)
            - [`PolygonEditor.button_press_callback()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.button_press_callback)
            - [`PolygonEditor.button_release_callback()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.button_release_callback)
            - [`PolygonEditor.delete_datapoint()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.delete_datapoint)
            - [`PolygonEditor.disable()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.disable)
            - [`PolygonEditor.draw_callback()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.draw_callback)
            - [`PolygonEditor.draw_line()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.draw_line)
            - [`PolygonEditor.draw_polygon()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.draw_polygon)
            - [`PolygonEditor.enable()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.enable)
            - [`PolygonEditor.epsilon`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.epsilon)
            - [`PolygonEditor.get_index_under_point()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.get_index_under_point)
            - [`PolygonEditor.insert_datapoint()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.insert_datapoint)
            - [`PolygonEditor.motion_notify_callback()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.motion_notify_callback)
            - [`PolygonEditor.polygon_changed()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.polygon_changed)
            - [`PolygonEditor.refresh()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.refresh)
            - [`PolygonEditor.reset()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.reset)
            - [`PolygonEditor.reset_line()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.reset_line)
            - [`PolygonEditor.reset_polygon()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.reset_polygon)
            - [`PolygonEditor.set_visibility()`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.set_visibility)
            - [`PolygonEditor.show_verts`](pybdy.gui.md#pybdy.gui.selection_editor.PolygonEditor.show_verts)
    - [Module contents](pybdy.gui.md#module-pybdy.gui)
- [pybdy.reader package](pybdy.reader.md)
    - [Submodules](pybdy.reader.md#submodules)
    - [pybdy.reader.directory module](pybdy.reader.md#module-pybdy.reader.directory)
        - [`GridGroup`](pybdy.reader.md#pybdy.reader.directory.GridGroup)
            - [`GridGroup.__init__()`](pybdy.reader.md#pybdy.reader.directory.GridGroup.__init__)
            - [`GridGroup.get_meta_data()`](pybdy.reader.md#pybdy.reader.directory.GridGroup.get_meta_data)
        - [`Reader`](pybdy.reader.md#pybdy.reader.directory.Reader)
            - [`Reader.__init__()`](pybdy.reader.md#pybdy.reader.directory.Reader.__init__)
            - [`Reader.calculate_time_interval()`](pybdy.reader.md#pybdy.reader.directory.Reader.calculate_time_interval)
            - [`Reader.delta_time_interval()`](pybdy.reader.md#pybdy.reader.directory.Reader.delta_time_interval)
            - [`Reader.get_dir_list()`](pybdy.reader.md#pybdy.reader.directory.Reader.get_dir_list)
            - [`Reader.get_source_timedata()`](pybdy.reader.md#pybdy.reader.directory.Reader.get_source_timedata)
            - [`Reader.grid_type_list`](pybdy.reader.md#pybdy.reader.directory.Reader.grid_type_list)
        - [`Variable`](pybdy.reader.md#pybdy.reader.directory.Variable)
            - [`Variable.__init__()`](pybdy.reader.md#pybdy.reader.directory.Variable.__init__)
            - [`Variable.get_attribute_values()`](pybdy.reader.md#pybdy.reader.directory.Variable.get_attribute_values)
            - [`Variable.get_dimensions()`](pybdy.reader.md#pybdy.reader.directory.Variable.get_dimensions)
            - [`Variable.set_time_dimension_index()`](pybdy.reader.md#pybdy.reader.directory.Variable.set_time_dimension_index)
            - [`Variable.time_counter_const`](pybdy.reader.md#pybdy.reader.directory.Variable.time_counter_const)
    - [pybdy.reader.factory module](pybdy.reader.md#module-pybdy.reader.factory)
        - [`GetFile()`](pybdy.reader.md#pybdy.reader.factory.GetFile)
        - [`GetReader()`](pybdy.reader.md#pybdy.reader.factory.GetReader)
        - [`NetCDFFile`](pybdy.reader.md#pybdy.reader.factory.NetCDFFile)
            - [`NetCDFFile.__init__()`](pybdy.reader.md#pybdy.reader.factory.NetCDFFile.__init__)
            - [`NetCDFFile.close()`](pybdy.reader.md#pybdy.reader.factory.NetCDFFile.close)
    - [pybdy.reader.ncml module](pybdy.reader.md#module-pybdy.reader.ncml)
        - [`GridGroup`](pybdy.reader.md#pybdy.reader.ncml.GridGroup)
            - [`GridGroup.__init__()`](pybdy.reader.md#pybdy.reader.ncml.GridGroup.__init__)
            - [`GridGroup.get_meta_data()`](pybdy.reader.md#pybdy.reader.ncml.GridGroup.get_meta_data)
            - [`GridGroup.logger`](pybdy.reader.md#pybdy.reader.ncml.GridGroup.logger)
            - [`GridGroup.update_atrributes()`](pybdy.reader.md#pybdy.reader.ncml.GridGroup.update_atrributes)
        - [`NcMLFile`](pybdy.reader.md#pybdy.reader.ncml.NcMLFile)
            - [`NcMLFile.__init__()`](pybdy.reader.md#pybdy.reader.ncml.NcMLFile.__init__)
            - [`NcMLFile.close()`](pybdy.reader.md#pybdy.reader.ncml.NcMLFile.close)
        - [`Reader`](pybdy.reader.md#pybdy.reader.ncml.Reader)
            - [`Reader.__init__()`](pybdy.reader.md#pybdy.reader.ncml.Reader.__init__)
            - [`Reader.close()`](pybdy.reader.md#pybdy.reader.ncml.Reader.close)
            - [`Reader.grid_type_list`](pybdy.reader.md#pybdy.reader.ncml.Reader.grid_type_list)
            - [`Reader.time_counter`](pybdy.reader.md#pybdy.reader.ncml.Reader.time_counter)
        - [`Variable`](pybdy.reader.md#pybdy.reader.ncml.Variable)
            - [`Variable.__init__()`](pybdy.reader.md#pybdy.reader.ncml.Variable.__init__)
            - [`Variable.get_attribute_value()`](pybdy.reader.md#pybdy.reader.ncml.Variable.get_attribute_value)
        - [`init_jnius()`](pybdy.reader.md#pybdy.reader.ncml.init_jnius)
    - [Module contents](pybdy.reader.md#module-pybdy.reader)
- [pybdy.tide package](pybdy.tide.md)
    - [Submodules](pybdy.tide.md#submodules)
    - [pybdy.tide.fes2014_extract_HC module](pybdy.tide.md#module-pybdy.tide.fes2014_extract_HC)
        - [`FesExtract`](pybdy.tide.md#pybdy.tide.fes2014_extract_HC.FesExtract)
            - [`FesExtract.__init__()`](pybdy.tide.md#pybdy.tide.fes2014_extract_HC.FesExtract.__init__)
            - [`FesExtract.interpolate_constituents()`](pybdy.tide.md#pybdy.tide.fes2014_extract_HC.FesExtract.interpolate_constituents)
        - [`bilinear_interpolation()`](pybdy.tide.md#pybdy.tide.fes2014_extract_HC.bilinear_interpolation)
        - [`interpolate_data()`](pybdy.tide.md#pybdy.tide.fes2014_extract_HC.interpolate_data)
    - [pybdy.tide.nemo_bdy_tide module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide)
        - [`Extract`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide.Extract)
            - [`Extract.__init__()`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide.Extract.__init__)
            - [`Extract.extract_con()`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide.Extract.extract_con)
    - [pybdy.tide.nemo_bdy_tide3 module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide3)
        - [`constituents_index()`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide3.constituents_index)
        - [`nemo_bdy_tide_rot()`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide3.nemo_bdy_tide_rot)
    - [pybdy.tide.nemo_bdy_tide_ncgen module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide_ncgen)
        - [`CreateBDYTideNetcdfFile()`](pybdy.tide.md#pybdy.tide.nemo_bdy_tide_ncgen.CreateBDYTideNetcdfFile)
    - [pybdy.tide.tpxo_extract_HC module](pybdy.tide.md#module-pybdy.tide.tpxo_extract_HC)
        - [`TpxoExtract`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.TpxoExtract)
            - [`TpxoExtract.__init__()`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.TpxoExtract.__init__)
            - [`TpxoExtract.generate_landmask_from_bathymetry()`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.TpxoExtract.generate_landmask_from_bathymetry)
            - [`TpxoExtract.interpolate_constituents()`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.TpxoExtract.interpolate_constituents)
        - [`bilinear_interpolation()`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.bilinear_interpolation)
        - [`interpolate_data()`](pybdy.tide.md#pybdy.tide.tpxo_extract_HC.interpolate_data)
    - [Module contents](pybdy.tide.md#module-pybdy.tide)
- [pybdy.utils package](pybdy.utils.md)
    - [Submodules](pybdy.utils.md#submodules)
    - [pybdy.utils.Constants module](pybdy.utils.md#module-pybdy.utils.Constants)
    - [pybdy.utils.e3_to_depth module](pybdy.utils.md#module-pybdy.utils.e3_to_depth)
        - [`e3_to_depth()`](pybdy.utils.md#pybdy.utils.e3_to_depth.e3_to_depth)
    - [pybdy.utils.gcoms_break_depth module](pybdy.utils.md#module-pybdy.utils.gcoms_break_depth)
        - [`gcoms_boundary_masks()`](pybdy.utils.md#pybdy.utils.gcoms_break_depth.gcoms_boundary_masks)
        - [`gcoms_break_depth()`](pybdy.utils.md#pybdy.utils.gcoms_break_depth.gcoms_break_depth)
        - [`polcoms_select_domain()`](pybdy.utils.md#pybdy.utils.gcoms_break_depth.polcoms_select_domain)
    - [pybdy.utils.nemo_bdy_lib module](pybdy.utils.md#module-pybdy.utils.nemo_bdy_lib)
        - [`bdy_sections()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.bdy_sections)
        - [`bdy_transport()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.bdy_transport)
        - [`dist()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.dist)
        - [`dist_point_to_segment()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.dist_point_to_segment)
        - [`get_output_filename()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.get_output_filename)
        - [`get_output_tidal_filename()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.get_output_tidal_filename)
        - [`psi_field()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.psi_field)
        - [`rot_rep()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.rot_rep)
        - [`sub2ind()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.sub2ind)
        - [`velocity_field()`](pybdy.utils.md#pybdy.utils.nemo_bdy_lib.velocity_field)
    - [Module contents](pybdy.utils.md#module-pybdy.utils)

## Submodules

# pybdy.nemo_bdy_chunk module

> Created on Thu Dec 19 10:39:46 2024.<br>

@author James Harle
@author Benjamin Barton

## pybdy.nemo_bdy_chunk.chunk_bdy(bdy)

Master chunking function.

Takes the boundary indicies and turns them into a list of boundary chunks.
The boundary is first split at natural breaks like land or the east-west wrap.
The chunks are then split near corners.
The chunks are then optionally split in the middle if they’re above a certain size
after attempting to split at corners.

> ### Parameters<br>

> bdy (obj) : organised as bdy_i[point, i/j grid] and rim width bdy_r[point]<br>
> logger : log error and messages<br>

> ### Returns<br>

> chunk_number (numpy.array) : array of chunk numbers<br>

## pybdy.nemo_bdy_chunk.chunk_corner(ibdy, jbdy, rbdy, chunk_number, rw)

Find corners and split along the change in direction.

To do this we look for a change in direction along each rim.

> ### Parameters<br>

> ibdy (numpy.array) : index in i direction<br>
> jbdy (numpy.array) : index in j direction<br>
> rbdy (numpy.array) : rim index<br>
> chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number<br>
> rw (int) : rimwidth<br>

> ### Returns<br>

> chunk_number (numpy.array) : array of chunk numbers<br>

## pybdy.nemo_bdy_chunk.chunk_land(ibdy, jbdy, chunk_number, rw)

Find natural breaks in the boundary looking for gaps in i and j.

> ### Parameters<br>

> ibdy (numpy.array) : index in i direction<br>
> jbdy (numpy.array) : index in j direction<br>
> chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number<br>
> rw (int) : rimwidth<br>

> ### Returns<br>

> chunk_number (numpy.array) : array of chunk numbers<br>

## pybdy.nemo_bdy_chunk.chunk_large(ibdy, jbdy, chunk_number)

Split boundaries that have too much white space and are too large.

> ### Parameters<br>

> ibdy (numpy.array) : index in i direction<br>
> jbdy (numpy.array) : index in j direction<br>
> chunk_number (numpy.array) : array of chunk numbers. -1 means an unassigned chunk number<br>

> ### Returns<br>

> chunk_number (numpy.array) : array of chunk numbers<br>

# pybdy.nemo_bdy_dst_coord module

## *class* pybdy.nemo_bdy_dst_coord.DstCoord

> Bases: `object`<br>

Object is currently empty and has data bound to it externally.

Equivalent to Matlab dst_coord.

# pybdy.nemo_bdy_extr_assist module

> Created on Thu Dec 21 17:34:00 2024.<br>

@author James Harle
@author Benjamin Barton

## pybdy.nemo_bdy_extr_assist.check_wrap(imin, imax, sc_lon)

Check if source domain wraps and dst spans the wrap.

> ### Parameters<br>

> imin (int) : minimum i index<br>
> imax (int) : maximum i index<br>
> sc_lon (np.array) : the longitude of the source grid<br>

> ### Returns<br>

> wrap_flag (bool) : if true the sc wraps and dst spans wrap<br>

## pybdy.nemo_bdy_extr_assist.distance_weights(sc_bdy, dist_tot, sc_z_len, r0, logger)

Find the distance weightings for averaging source data to destination.

> ### Parameters<br>

> sc_bdy (numpy.array) : source data<br>
> dist_tot (numpy.array) : distance from dst point to 9 nearest sc points<br>
> sc_z_len (int) : the number of depth levels<br>
> r0 (float) : correlation distance<br>
> logger : log of statements<br>

> ### Returns<br>

> dist_wei (numpy.array) : weightings for averaging<br>
> dist_fac (numpy.array) : total weighting factor<br>

## pybdy.nemo_bdy_extr_assist.flood_fill(sc_bdy, isslab, logger)

Fill the data horizontally then downwards to remove nans before interpolation.

> ### Parameters<br>

> sc_bdy (np.array) : souce data [nz_sc, nbdy, 9]<br>
> isslab (bool) : if true data has vertical cells for vertical flood fill<br>
> logger : log of statements<br>

> ### Returns<br>

> sc_bdy (np.array) : souce data [nz_sc, nbdy, 9]<br>

## pybdy.nemo_bdy_extr_assist.get_ind(dst_lon, dst_lat, sc_lon, sc_lat)

Calculate indicies of max and min for data extraction.

> ### Parameters<br>

> dst_lon (np.array) : the longitude of the destination grid<br>
> dst_lat (np.array) : the latitude of the destination grid<br>
> sc_lon (np.array) : the longitude of the source grid<br>
> sc_lat (np.array) : the latitude of the source grid<br>

> ### Returns<br>

> imin (int) : minimum i index<br>
> imax (int) : maximum i index<br>
> jmin (int) : minimum j index<br>
> jmax (int) : maximum j index<br>

## pybdy.nemo_bdy_extr_assist.get_vertical_weights(dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len, ind, zco)

Determine 3D depth vertical weights for the linear interpolation onto Dst grid.

Selects 9 source points horizontally around a destination grid point.
Calculated the distance from each source point to the destination to
be used in weightings. The resulting arrays are [nz * nbdy * 9, 2].

> ### Parameters<br>

> dst_dep (np.array) : the depth of the destination grid chunk [nz, nbdy]<br>
> dst_len_z (int) : the length of depth axis of the destination grid<br>
> num_bdy (int) : number of boundary points in chunk<br>
> sc_z (np.array) : the depth of the source grid [k, j, i]<br>
> sc_z_len (int) : the length of depth axis of the source grid<br>
> ind (np.array) : indices of bdy and 9 nearest neighbours flattened “F” j,i [nbdy, 9]<br>
> zco (bool) : if True z levels are not spatially varying<br>

> ### Returns<br>

> z9_dist (np.array) : the distance weights of the selected points<br>
> z9_ind (np.array) : the indices of the sc depth above and below bdy<br>

## pybdy.nemo_bdy_extr_assist.get_vertical_weights_zco(dst_dep, dst_len_z, num_bdy, sc_z, sc_z_len)

Determine vertical weights for the linear interpolation onto Dst grid.

Calculated the vertical distance from each source point to the destination to
be used in weightings. The resulting arrays are [nbdy * nz, 2].

> Note: z_dist and z_ind are [nbdy\*nz, 2] where [:, 0] is the nearest vertical index<br>
> and [:, 1] is the index above or below i.e. the vertical index -1 for sc_z > dst_z<br>
> and vertical index +1 for sc_z \<= dst_z

> ### Parameters<br>

> dst_dep (np.array) : the depth of the destination grid chunk [nz, nbdy]<br>
> dst_len_z (int) : the length of depth axis of the destination grid<br>
> num_bdy (int) : number of boundary points in chunk<br>
> sc_z (np.array) : the depth of the source grid [k, j, i]<br>
> sc_z_len (int) : the length of depth axis of the source grid<br>

> ### Returns<br>

> z_dist (np.array) : the distance weights of the selected points<br>
> z_ind (np.array) : the indices of the sc depth above and below bdy<br>

## pybdy.nemo_bdy_extr_assist.interp_horizontal(sc_bdy, dist_wei, dist_fac, logger)

Interpolate the source data to the destination grid using weighted average.

> ### Parameters<br>

> sc_bdy (numpy.array) : source data<br>
> dist_wei (numpy.array) : weightings for interpolation<br>
> dist_fac (numpy.array) : sum of weightings<br>
> logger : log of statements<br>

> ### Returns<br>

> dst_bdy (numpy.array) : destination bdy points with data from source grid<br>

## pybdy.nemo_bdy_extr_assist.interp_vertical(sc_bdy, dst_dep, bdy_bathy, z_ind, z_dist, num_bdy, zinterp=True)

Interpolate source data onto destination vertical levels.

> ### Parameters<br>

> sc_bdy (np.array) : souce data [nz_sc, nbdy, 9]<br>
> dst_dep (np.array) : the depth of the destination grid chunk [nz, nbdy]<br>
> bdy_bathy (np.array): the destination grid bdy points bathymetry<br>
> z_ind (np.array) : the indices of the sc depth above and below bdy<br>
> z_dist (np.array) : the distance weights of the selected points<br>
> num_bdy (int) : number of boundary points in chunk<br>
> zinterp (bool) : vertical interpolation flag<br>

> ### Returns<br>

> data_out (np.array) : source data on destination depth levels<br>

## pybdy.nemo_bdy_extr_assist.valid_index(sc_bdy, logger)

Find an array of valid indicies.

> ### Parameters<br>

> sc_bdy (numpy.array) : source data<br>
> logger : log of statements<br>

> ### Returns<br>

> data_ind (numpy.array) : indicies of max depth of valid data<br>
> nan_ind (numpy.array) : indicies where source is land<br>

# pybdy.nemo_bdy_extr_tm3 module

> Created on Wed Sep 12 08:02:46 2012.<br>

This Module defines the extraction of the data from the source grid and does
the interpolation onto the destination grid.

@author James Harle
@author John Kazimierz Farey

> @author: Mr. Srikanth Nagella<br>

## *class* pybdy.nemo_bdy_extr_tm3.Extract(setup, SourceCoord, DstCoord, Grid, var_nam, grd, pair)

> Bases: `object`<br>

### *method* \_\_init\_\_(setup, SourceCoord, DstCoord, Grid, var_nam, grd, pair)

Initialise the Extract object.

Parent grid to child grid weights are defined along with rotation
weightings for vector quantities.

> ### Parameters<br>

> setup (list) : settings for bdy<br>
> SourceCoord (obj) : source grid information<br>
> DstCoord (obj) : destination grid information<br>
> Grid (dict) : containing grid type ‘t’, ‘u’, ‘v’ and source time<br>
> var_name (list) : netcdf file variable names (str)<br>
> years (list) : years to extract (default [1979])<br>
> months (list) : months to extract (default [11])<br>

> ### Returns<br>

> Extract (obj) : Object with indexing arrays and weightings ready for interpolation<br>

### *method* cal_trans(source, dest, year, month)

Translate between calendars and return scale factor and number of days in month.

> ### Parameters<br>

> source : source calendar<br>
> dest : destination calendar<br>
> year : input year<br>
> month : input month<br>

> ### Returns<br>

> sf : scale factor<br>
> ed : number of days in month<br>

### *method* extract_month(year, month)

Extract monthly data and interpolates onto the destination grid.

> ### Parameters<br>

> year : year of data to be extracted<br>
> month : month of the year to be extracted<br>

> ### Returns<br>

> self.data_out : data from source on bdy locations and depths<br>

### *method* time_delta(time_counter)

Get time delta and number of time steps per day.

Calculates difference between time steps for time_counter and checks
these are uniform. Then retrives the number of time steps per day.

> ### Parameters<br>

> time_counter : model time coordinate<br>

> ### Returns<br>

> deltaT : length of time step<br>
> dstep : number of time steps per day<br>

### *method* time_interp(year, month)

Perform a time interpolation of the BDY data to daily frequency.

This method performs a time interpolation (if required). This is
necessary if the time frequency is not a factor of monthly output or the
input and output calendars differ. CF compliant calendar options

> accepted: gregorian | standard, proleptic_gregorian, noleap | 365_day,<br>
> 360_day or julian.\*

### *method* write_out(year, month, ind, unit_origin)

Write monthy BDY data to netCDF file.

This method writes out all available variables for a given grid along with
any asscoaied metadata. Currently data are only written out as monthly
files.

> ### Parameters<br>

> year (int) : year to write out<br>
> month (int) : month to write out<br>
> ind (dict): dictionary holding grid information<br>
> unit_origin (str) : time reference ‘%d 00:00:00’ %date_origin<br>

> ### Returns<br>

> None<br>

# pybdy.nemo_bdy_gen_c module

NEMO Boundary module.

Creates indices for t, u and v points, plus rim gradient.
The variable names have been renamed to keep consistent with python standards and generalizing
the variable names eg. bdy_i is used instead of bdy_t

Ported from Matlab code by James Harle

> @author: John Kazimierz Farey<br>
> @author: Srikanth Nagella.<br>

## *class* pybdy.nemo_bdy_gen_c.Boundary(boundary_mask, settings, grid)

> Bases: `object`<br>

Class for boundary definitions.

### *method* \_\_init\_\_(boundary_mask, settings, grid)

Generate the indices for NEMO Boundary and returns a Grid object with indices.

> ### Parameters<br>

> boundary_mask : boundary mask<br>
> settings : dictionary of setting values<br>
> grid : type of the grid ‘t’, ‘u’, ‘v’<br>

> ### Returns<br>

> Boundary (object) : where bdy_i is index and bdy_r is the r index<br>

### *method* fill(mask, ref, brg)

### *method* find_bdy(igrid, jgrid, mask, brg)

Find the border indexes by checking the change from ocean to land.

> Returns the i and j index array where the shift happens.<br>

> ### Parameters<br>

> igrid : I x direction indexes<br>
> jgrid : J y direction indexes<br>
> mask : mask data<br>
> brg : mask index range<br>

> ### Returns<br>

> bdy_i : bdy indexes<br>
> bdy_r : bdy rim values.<br>

### *method* remove_duplicate_points(bdy_i, bdy_r)

Remove the duplicate points in the bdy_i and return the bdy_i and bdy_r.

> ### Parameters<br>

> bdy_i : bdy indexes<br>
> bdy_r : bdy rim values.<br>

> ### Returns<br>

> bdy_i : bdy indexes<br>
> bdy_r : bdy rim values.<br>

### *method* remove_landpoints_open_ocean(mask, bdy_i, bdy_r)

Remove the land points and open ocean points.

### *method* unique_rows(t)

Find indexes of unique rows in the input 2D array.

> ### Parameters<br>

> t : input 2D array.<br>

> ### Returns<br>

> indx : indexes of unique rows<br>

# pybdy.nemo_bdy_grid_angle module

## *class* pybdy.nemo_bdy_grid_angle.GridAngle(hgr, imin, imax, jmin, jmax, cd_type)

> Bases: `object`<br>

Class to get orientation of grid from I and J offsets for different grid types.

### *method* \_\_init\_\_(hgr, imin, imax, jmin, jmax, cd_type)

Get sin and cosin files for the grid angle from North.

> ### Parameters<br>

> hgr : grid object<br>
> imin : minimum model zonal indices<br>
> imax : maximum model zonal indices<br>
> jmin : minimum model meridional indices<br>
> jmax : maximum model meridional indices<br>
> cd_type: define the nature of pt2d grid points<br>

> ### Returns<br>

> None : object<br>

### *method* get_lam_phi(map=False, i=0, j=0, single=False)

Get lam/phi in (offset) i/j range for init grid type.

Data must be converted to float64 to prevent dementation of later results.

### *method* get_north_dir()

Find North pole direction and modulus of some point.

### *method* get_seg_dir(north_n)

Find segmentation direction of some point.

### *method* get_sin_cos(nx, ny, nn, sx, sy, sn)

Get sin and cos from lat and lon using using scaler/vectorial products.

### *method* trig_eq(x, eq, z_one, z_two)

Calculate long winded equation of two vars; some lam and phi.

# pybdy.nemo_bdy_ice module

## *class* pybdy.nemo_bdy_ice.BoundaryIce

> Bases: `object`<br>

### *method* \_\_init\_\_()

# pybdy.nemo_bdy_ncgen module

Create a Nemo Bdy netCDF file ready for population.

Written by John Kazimierz Farey, started August 30, 2012
Port of Matlab code of James Harle

## pybdy.nemo_bdy_ncgen.CreateBDYNetcdfFile(filename, xb_len, x_len, y_len, depth_len, rw, h, orig, fv, calendar, grd)

Create a template of bdy netcdf files. A common for T, I, U, V, E grid types.

# pybdy.nemo_bdy_ncpop module

Created on 3 Oct 2014.

> @author: Mr. Srikanth Nagella<br>
> Netcdf writer for the bdy output

## pybdy.nemo_bdy_ncpop.write_data_to_file(filename, variable_name, data)

Write the data to the netcdf templete file.

> ### Parameters<br>

filename – output filename
variable_name – variable name into which the data is written to.
data – data that will be written to variable in netcdf.

# pybdy.nemo_bdy_scr_coord module

## *class* pybdy.nemo_bdy_scr_coord.ScrCoord

> Bases: `object`<br>

### *method* \_\_init\_\_()

# pybdy.nemo_bdy_setup module

> Created on Wed Sep 12 08:02:46 2012.<br>

Parses a file to find out which nemo boundary settings to use

@author John Kazimierz Farey
@author James Harle

## *class* pybdy.nemo_bdy_setup.Setup(setfile)

> Bases: `object`<br>

Invoke with a text file location, class init reads and deciphers variables.

This class holds the settings information

### *method* \_\_init\_\_(setfile)

Set up the constructor.

This constructor reads the settings file and sets the dictionary with
setting name/key and it’s value.

> ### Parameters<br>

> setfile (str) : settings file<br>

### *method* refresh()

Reload the settings from file.

### *method* variable_info_reader(filename)

Read the variable description data from the ‘variable.info’ file.

This method reads the variable description data from ‘variable.info’ file
in the pybdy installation path if it can’t find the file with the same
name as input bdy file with extension .info

> ### Parameters<br>

filename – filename of the variables information
returns a dictionary with variable name and its description.

> ### Returns<br>

> variable_info : dict<br>

### *method* write()

Write backs the variable data back into the file.

## pybdy.nemo_bdy_setup.strip_comments(line)

Strip the comments in the line. removes text after !.

# pybdy.nemo_bdy_source_coord module

## *class* pybdy.nemo_bdy_source_coord.SourceCoord

> Bases: `object`<br>

### *method* \_\_init\_\_()

Initialise the source coordinates attributes of the object.

# pybdy.nemo_bdy_zgrv2 module

Created.

@author John Kazimierz Farey
@author Benjamin Barton.

## pybdy.nemo_bdy_zgrv2.get_bdy_depths(DstCoord, bdy_i, grd)

Depth levels on the destination grid at bdy points.

> ### Parameters<br>

> DstCoord (object) : Object containing destination grid info<br>
> bdy_i (np.array) : indices of the i, j bdy points [bdy, 2]<br>
> grd (str) : grid type t, u, v<br>

> ### Returns<br>

> bdy_tz (array) : sc depths on bdy points on t levels<br>
> bdy_wz (array) : sc depths on bdy points on w levels<br>
> bdy_e3 (array) : sc level thickness on bdy points on t levels<br>

## pybdy.nemo_bdy_zgrv2.get_bdy_depths_old(bdy_t, bdy_u, bdy_v, DstCoord, settings)

Generate Depth information.

Written by John Kazimierz Farey, Sep 2012
Port of Matlab code of James Harle

Generates depth points for t, u and v in one loop iteration.
Initialise with bdy t, u and v grid attributes (Grid.bdy_i) and settings dictionary.

## pybdy.nemo_bdy_zgrv2.get_bdy_sc_depths(SourceCoord, DstCoord, grd)

Depth levels from the nearest neighbour on the source grid.

> ### Parameters<br>

> SourceCoord (object) : Object containing source grid info<br>
> DstCoord (object) : Object containing destination grid info<br>
> grd (str) : grid type t, u, v<br>

> ### Returns<br>

> bdy_tz (array) : sc depths on bdy points on t levels<br>
> bdy_wz (array) : sc depths on bdy points on w levels<br>
> bdy_e3 (array) : sc level thickness on bdy points on t levels<br>

# pybdy.nemo_coord_gen_pop module

Module that combines matlab coord gen and pop.

Initialise with netcdf file name and dictionary containing all bdy grids (objects).

## *class* pybdy.nemo_coord_gen_pop.Coord(fname, bdy_ind)

> Bases: `object`<br>

Class for writing boundayr coordinate data to netcdf file.

### *method* \_\_init\_\_(fname, bdy_ind)

Create Nemo bdy indices for t, u, v points.

> ### Parameters<br>

> fname (str) : file name of coords file for output<br>
> bdy_ind (numpy.array) : indicies of bdy points<br>

> ### Returns<br>

> None : object<br>

### *method* add_vars(dim, grd, unt)

Create a var w/ attributes.

### *method* build_dict(dim, units)

Set up a grid dictionary.

### *method* closeme()

### *method* create_dims()

Create dims and returns a dictionary of them.

### *method* populate(hgr)

Populate the file with indices, lat, lon, and e dimensions.

### *method* set_lenvar(vardic, hgr=None, unt=None)

Set the len var of each array in the var dictionary.

Use by specifying hgr and unt which pulls data from loaded grid data.
Otherwise pull it from the class dict.

# pybdy.profiler module

> Created on Wed Sep 12 08:02:46 2012.<br>

The main application script for the NRCT.

@author James Harle
@author John Kazimierz Farey
@author Srikanth Nagella

## *class* pybdy.profiler.Grid

> Bases: `object`<br>

A Grid object that stores bdy grid information.

### *method* \_\_init\_\_()

## pybdy.profiler.process_bdy(setup_filepath=0, mask_gui=False)

Handle all the calls to generate open boundary conditions for a given regional domain.

This is main entry for processing BDY lateral boundary conditions.
This is the main script that handles all the calls to generate open
boundary conditions for a given regional domain. Input options are handled
in a NEMO style namelist (namelist.bdy). There is an optional GUI allowing
the user to create a mask that defines the extent of the regional model.

> ### Parameters<br>

> setup_filepath (str) : file path to find namelist.bdy<br>
> mask_gui (bool): whether use of the GUI is required<br>

> ### Returns<br>

> None : bdy data is written out to NetCDF file<br>

## pybdy.profiler.write_tidal_data(setup_var, dst_coord_var, grid, tide_cons, cons)

Write the tidal data to a NetCDF file.

> ### Parameters<br>

> setup_var (list): Description of arg1<br>
> dst_coord_var (obj) : Description of arg1<br>
> grid (dict): Description of arg1<br>
> tide_cons (list): Description of arg1<br>
> cons (data): cosz, sinz, cosu, sinu, cosv, sinv<br>

> ### Returns<br>

> None : tidal data is written to NetCDF file<br>

# pybdy.pybdy_exe module

Entry for the project.

> @author: Mr. Srikanth Nagella<br>

## pybdy.pybdy_exe.main()

Run main function.

Checks the command line parameters and passes them to the profile module for processing.

# pybdy.pybdy_ncml_generator module

Created on 2 Jul 2015.

The main application object for hosting the pybdy ncml editor.
Used for development purposes to display the ncml editor dialog.

> @author: Shirley Crompton, UK Science and Technology Facilities Council<br>

## pybdy.pybdy_ncml_generator.main()

Command line execution method.

Checks the input arguments and passes on to method to open the ncml generator window.

# pybdy.pybdy_settings_editor module

Created on 7 Jan 2015.

> @author: Mr. Srikanth Nagella<br>

## pybdy.pybdy_settings_editor.main()

Command line execution method.

Checks the input arguments and passes on to method to open the settings window.

## pybdy.pybdy_settings_editor.open_settings_dialog(setup)

Start the settings window using the setup settings provided in the input.

On clicking the cancel button it doesn’t shutdown the applicaiton but carries on with the execution.

## pybdy.pybdy_settings_editor.open_settings_window(fname)

Start a Qt application.

This method gives the user the option to pick a namelist.bdy file to edit.
Once user selects it it will open a dialog box where users can edit the parameters.

# pybdy.version module

## Module contents

a Python based regional NEMO model configuration toolbox.
