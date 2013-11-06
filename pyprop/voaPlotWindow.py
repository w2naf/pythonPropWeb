#! /usr/bin/env python
#
# File: voaPlotWindow.py
#
# Copyright (c) 2009 J.Watson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
# 02110-1301, USA.
# 
# todo consider using a scrolled pane here...
# add buttons to move between plots
# double clicking an all plot should zoom in to an individual plot
try:
    import pygtk
    pygtk.require("2.0")
    import gobject
except:
    pass
try:
    import gtk
except:
    sys.exit(1)

class VOAPlotWindow():

    def __init__(self, title, canvas, parent=None, dpi=150):
        self.dpi = dpi
        self._dia = gtk.Dialog(title, parent=parent, flags=gtk.DIALOG_DESTROY_WITH_PARENT)
        self._dia.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_OK, gtk.STOCK_CLOSE, gtk.RESPONSE_NONE)
        self._dia.vbox.pack_start(canvas)
        self._dia.set_default_size(700, 600)
        self._dia.show()


        _response = None
        while _response != gtk.RESPONSE_NONE and _response != gtk.RESPONSE_DELETE_EVENT:
            _response = self._dia.run()
            if _response == gtk.RESPONSE_OK:
                _chooser = gtk.FileChooserDialog(_("Save Image..."),
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                _filter = gtk.FileFilter()
                _filter.set_name("PNG Images")
                _filter.add_mime_type("image/png")
                _filter.add_pattern("*.png")
                _chooser.add_filter(_filter)
                _save_response = _chooser.run()
                if _save_response == gtk.RESPONSE_OK:
                    save_file = _chooser.get_filename()
                    if not save_file.endswith('.png'):
                        save_file = save_file + '.png'
                    self.save_plot(canvas, save_file)
                _chooser.destroy()
        self._dia.destroy()
        
        
    def save_plot(self, canvas, filename=None):
        canvas.print_figure(filename, dpi=self.dpi, facecolor='white', edgecolor='white')

