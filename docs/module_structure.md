All Module Structure

- [grid package](grid.md)
    - [Submodules](grid.md#submodules)
    - [grid.hgr module](grid.md#module-grid.hgr)
        - [`H_Grid`](grid.md#grid.hgr.H_Grid)
            - [`H_Grid.__init__()`](grid.md#grid.hgr.H_Grid.__init__)
            - [`H_Grid.find_hgrid_type()`](grid.md#grid.hgr.H_Grid.find_hgrid_type)
            - [`H_Grid.get_vars()`](grid.md#grid.hgr.H_Grid.get_vars)
        - [`calc_e1_e2()`](grid.md#grid.hgr.calc_e1_e2)
        - [`calc_grid_from_t()`](grid.md#grid.hgr.calc_grid_from_t)
        - [`fill_hgrid_vars()`](grid.md#grid.hgr.fill_hgrid_vars)
    - [grid.zgr module](grid.md#module-grid.zgr)
        - [`Z_Grid`](grid.md#grid.zgr.Z_Grid)
            - [`Z_Grid.__init__()`](grid.md#grid.zgr.Z_Grid.__init__)
            - [`Z_Grid.find_zgrid_type()`](grid.md#grid.zgr.Z_Grid.find_zgrid_type)
            - [`Z_Grid.get_vars()`](grid.md#grid.zgr.Z_Grid.get_vars)
        - [`calc_gdepw()`](grid.md#grid.zgr.calc_gdepw)
        - [`fill_zgrid_vars()`](grid.md#grid.zgr.fill_zgrid_vars)
        - [`horiz_interp_e3_old()`](grid.md#grid.zgr.horiz_interp_e3_old)
        - [`horiz_interp_lev()`](grid.md#grid.zgr.horiz_interp_lev)
        - [`vert_calc_e3()`](grid.md#grid.zgr.vert_calc_e3)
    - [Module contents](grid.md#module-grid)
- [pybdy package](pybdy.md)
    - [Subpackages](pybdy.md#subpackages)
        - [pybdy.gui package](pybdy.gui.md)
            - [Submodules](pybdy.gui.md#submodules)
            - [pybdy.gui.mynormalize module](pybdy.gui.md#module-pybdy.gui.mynormalize)
            - [pybdy.gui.nemo_bdy_input_window module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_input_window)
            - [pybdy.gui.nemo_bdy_mask module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_mask)
            - [pybdy.gui.nemo_bdy_mask_gui module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_mask_gui)
            - [pybdy.gui.nemo_bdy_namelist_edit module](pybdy.gui.md#module-pybdy.gui.nemo_bdy_namelist_edit)
            - [pybdy.gui.nemo_ncml_generator module](pybdy.gui.md#module-pybdy.gui.nemo_ncml_generator)
            - [pybdy.gui.nemo_ncml_tab_widget module](pybdy.gui.md#module-pybdy.gui.nemo_ncml_tab_widget)
            - [pybdy.gui.selection_editor module](pybdy.gui.md#module-pybdy.gui.selection_editor)
            - [Module contents](pybdy.gui.md#module-pybdy.gui)
        - [pybdy.reader package](pybdy.reader.md)
            - [Submodules](pybdy.reader.md#submodules)
            - [pybdy.reader.directory module](pybdy.reader.md#module-pybdy.reader.directory)
            - [pybdy.reader.factory module](pybdy.reader.md#module-pybdy.reader.factory)
            - [pybdy.reader.ncml module](pybdy.reader.md#module-pybdy.reader.ncml)
            - [Module contents](pybdy.reader.md#module-pybdy.reader)
        - [pybdy.tide package](pybdy.tide.md)
            - [Submodules](pybdy.tide.md#submodules)
            - [pybdy.tide.fes2014_extract_HC module](pybdy.tide.md#module-pybdy.tide.fes2014_extract_HC)
            - [pybdy.tide.nemo_bdy_tide module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide)
            - [pybdy.tide.nemo_bdy_tide3 module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide3)
            - [pybdy.tide.nemo_bdy_tide_ncgen module](pybdy.tide.md#module-pybdy.tide.nemo_bdy_tide_ncgen)
            - [pybdy.tide.tpxo_extract_HC module](pybdy.tide.md#module-pybdy.tide.tpxo_extract_HC)
            - [Module contents](pybdy.tide.md#module-pybdy.tide)
        - [pybdy.utils package](pybdy.utils.md)
            - [Submodules](pybdy.utils.md#submodules)
            - [pybdy.utils.Constants module](pybdy.utils.md#module-pybdy.utils.Constants)
            - [pybdy.utils.e3_to_depth module](pybdy.utils.md#module-pybdy.utils.e3_to_depth)
            - [pybdy.utils.gcoms_break_depth module](pybdy.utils.md#module-pybdy.utils.gcoms_break_depth)
            - [pybdy.utils.nemo_bdy_lib module](pybdy.utils.md#module-pybdy.utils.nemo_bdy_lib)
            - [Module contents](pybdy.utils.md#module-pybdy.utils)
    - [Submodules](pybdy.md#submodules)
    - [pybdy.nemo_bdy_chunk module](pybdy.md#module-pybdy.nemo_bdy_chunk)
        - [`chunk_bdy()`](pybdy.md#pybdy.nemo_bdy_chunk.chunk_bdy)
        - [`chunk_corner()`](pybdy.md#pybdy.nemo_bdy_chunk.chunk_corner)
        - [`chunk_land()`](pybdy.md#pybdy.nemo_bdy_chunk.chunk_land)
        - [`chunk_large()`](pybdy.md#pybdy.nemo_bdy_chunk.chunk_large)
    - [pybdy.nemo_bdy_dst_coord module](pybdy.md#module-pybdy.nemo_bdy_dst_coord)
        - [`DstCoord`](pybdy.md#pybdy.nemo_bdy_dst_coord.DstCoord)
    - [pybdy.nemo_bdy_extr_assist module](pybdy.md#module-pybdy.nemo_bdy_extr_assist)
        - [`check_wrap()`](pybdy.md#pybdy.nemo_bdy_extr_assist.check_wrap)
        - [`distance_weights()`](pybdy.md#pybdy.nemo_bdy_extr_assist.distance_weights)
        - [`flood_fill()`](pybdy.md#pybdy.nemo_bdy_extr_assist.flood_fill)
        - [`get_ind()`](pybdy.md#pybdy.nemo_bdy_extr_assist.get_ind)
        - [`get_vertical_weights()`](pybdy.md#pybdy.nemo_bdy_extr_assist.get_vertical_weights)
        - [`get_vertical_weights_zco()`](pybdy.md#pybdy.nemo_bdy_extr_assist.get_vertical_weights_zco)
        - [`interp_horizontal()`](pybdy.md#pybdy.nemo_bdy_extr_assist.interp_horizontal)
        - [`interp_vertical()`](pybdy.md#pybdy.nemo_bdy_extr_assist.interp_vertical)
        - [`valid_index()`](pybdy.md#pybdy.nemo_bdy_extr_assist.valid_index)
    - [pybdy.nemo_bdy_extr_tm3 module](pybdy.md#module-pybdy.nemo_bdy_extr_tm3)
        - [`Extract`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract)
            - [`Extract.__init__()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.__init__)
            - [`Extract.cal_trans()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.cal_trans)
            - [`Extract.extract_month()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.extract_month)
            - [`Extract.time_delta()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.time_delta)
            - [`Extract.time_interp()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.time_interp)
            - [`Extract.write_out()`](pybdy.md#pybdy.nemo_bdy_extr_tm3.Extract.write_out)
    - [pybdy.nemo_bdy_gen_c module](pybdy.md#module-pybdy.nemo_bdy_gen_c)
        - [`Boundary`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary)
            - [`Boundary.__init__()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.__init__)
            - [`Boundary.fill()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.fill)
            - [`Boundary.find_bdy()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.find_bdy)
            - [`Boundary.remove_duplicate_points()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.remove_duplicate_points)
            - [`Boundary.remove_landpoints_open_ocean()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.remove_landpoints_open_ocean)
            - [`Boundary.unique_rows()`](pybdy.md#pybdy.nemo_bdy_gen_c.Boundary.unique_rows)
    - [pybdy.nemo_bdy_grid_angle module](pybdy.md#module-pybdy.nemo_bdy_grid_angle)
        - [`GridAngle`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle)
            - [`GridAngle.__init__()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.__init__)
            - [`GridAngle.get_lam_phi()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.get_lam_phi)
            - [`GridAngle.get_north_dir()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.get_north_dir)
            - [`GridAngle.get_seg_dir()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.get_seg_dir)
            - [`GridAngle.get_sin_cos()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.get_sin_cos)
            - [`GridAngle.trig_eq()`](pybdy.md#pybdy.nemo_bdy_grid_angle.GridAngle.trig_eq)
    - [pybdy.nemo_bdy_ice module](pybdy.md#module-pybdy.nemo_bdy_ice)
        - [`BoundaryIce`](pybdy.md#pybdy.nemo_bdy_ice.BoundaryIce)
            - [`BoundaryIce.__init__()`](pybdy.md#pybdy.nemo_bdy_ice.BoundaryIce.__init__)
    - [pybdy.nemo_bdy_ncgen module](pybdy.md#module-pybdy.nemo_bdy_ncgen)
        - [`CreateBDYNetcdfFile()`](pybdy.md#pybdy.nemo_bdy_ncgen.CreateBDYNetcdfFile)
    - [pybdy.nemo_bdy_ncpop module](pybdy.md#module-pybdy.nemo_bdy_ncpop)
        - [`write_data_to_file()`](pybdy.md#pybdy.nemo_bdy_ncpop.write_data_to_file)
    - [pybdy.nemo_bdy_scr_coord module](pybdy.md#module-pybdy.nemo_bdy_scr_coord)
        - [`ScrCoord`](pybdy.md#pybdy.nemo_bdy_scr_coord.ScrCoord)
            - [`ScrCoord.__init__()`](pybdy.md#pybdy.nemo_bdy_scr_coord.ScrCoord.__init__)
    - [pybdy.nemo_bdy_setup module](pybdy.md#module-pybdy.nemo_bdy_setup)
        - [`Setup`](pybdy.md#pybdy.nemo_bdy_setup.Setup)
            - [`Setup.__init__()`](pybdy.md#pybdy.nemo_bdy_setup.Setup.__init__)
            - [`Setup.refresh()`](pybdy.md#pybdy.nemo_bdy_setup.Setup.refresh)
            - [`Setup.variable_info_reader()`](pybdy.md#pybdy.nemo_bdy_setup.Setup.variable_info_reader)
            - [`Setup.write()`](pybdy.md#pybdy.nemo_bdy_setup.Setup.write)
        - [`strip_comments()`](pybdy.md#pybdy.nemo_bdy_setup.strip_comments)
    - [pybdy.nemo_bdy_source_coord module](pybdy.md#module-pybdy.nemo_bdy_source_coord)
        - [`SourceCoord`](pybdy.md#pybdy.nemo_bdy_source_coord.SourceCoord)
            - [`SourceCoord.__init__()`](pybdy.md#pybdy.nemo_bdy_source_coord.SourceCoord.__init__)
    - [pybdy.nemo_bdy_zgrv2 module](pybdy.md#module-pybdy.nemo_bdy_zgrv2)
        - [`get_bdy_depths()`](pybdy.md#pybdy.nemo_bdy_zgrv2.get_bdy_depths)
        - [`get_bdy_depths_old()`](pybdy.md#pybdy.nemo_bdy_zgrv2.get_bdy_depths_old)
        - [`get_bdy_sc_depths()`](pybdy.md#pybdy.nemo_bdy_zgrv2.get_bdy_sc_depths)
    - [pybdy.nemo_coord_gen_pop module](pybdy.md#module-pybdy.nemo_coord_gen_pop)
        - [`Coord`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord)
            - [`Coord.__init__()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.__init__)
            - [`Coord.add_vars()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.add_vars)
            - [`Coord.build_dict()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.build_dict)
            - [`Coord.closeme()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.closeme)
            - [`Coord.create_dims()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.create_dims)
            - [`Coord.populate()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.populate)
            - [`Coord.set_lenvar()`](pybdy.md#pybdy.nemo_coord_gen_pop.Coord.set_lenvar)
    - [pybdy.profiler module](pybdy.md#module-pybdy.profiler)
        - [`Grid`](pybdy.md#pybdy.profiler.Grid)
            - [`Grid.__init__()`](pybdy.md#pybdy.profiler.Grid.__init__)
        - [`process_bdy()`](pybdy.md#pybdy.profiler.process_bdy)
        - [`write_tidal_data()`](pybdy.md#pybdy.profiler.write_tidal_data)
    - [pybdy.pybdy_exe module](pybdy.md#module-pybdy.pybdy_exe)
        - [`main()`](pybdy.md#pybdy.pybdy_exe.main)
    - [pybdy.pybdy_ncml_generator module](pybdy.md#module-pybdy.pybdy_ncml_generator)
        - [`main()`](pybdy.md#pybdy.pybdy_ncml_generator.main)
    - [pybdy.pybdy_settings_editor module](pybdy.md#module-pybdy.pybdy_settings_editor)
        - [`main()`](pybdy.md#pybdy.pybdy_settings_editor.main)
        - [`open_settings_dialog()`](pybdy.md#pybdy.pybdy_settings_editor.open_settings_dialog)
        - [`open_settings_window()`](pybdy.md#pybdy.pybdy_settings_editor.open_settings_window)
    - [pybdy.version module](pybdy.md#module-pybdy.version)
    - [Module contents](pybdy.md#module-pybdy)
