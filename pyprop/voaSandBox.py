import voaAreaPlot

fileName    = '/home/w2naf/itshfbc/areadata/pyArea'
_data_type  = '2'
_vg_files   = [1]
_time_zone  = 0
_color_map  = 'jet'
_plot_contours    = False
_plot_meridians   = True
_plot_parallels   = True
_plot_terminator  = True
_run_quietly      = True
_save_file        = 'propMap.png'

plot = voaAreaPlot.VOAAreaPlot(fileName,
                data_type = _data_type,
                vg_files = _vg_files,
                time_zone = _time_zone,
                color_map = _color_map,
                plot_contours   = _plot_contours,
                plot_meridians  = _plot_meridians,
                plot_parallels  = _plot_parallels,
                plot_terminator = _plot_terminator,
                run_quietly     = _run_quietly,
                save_file       = _save_file
                )
