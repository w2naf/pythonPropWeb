#!/usr/bin/env python
#
# File: voacapAntennaChooser
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

# Dialog box that returns a voaLocation

import os
import re
import sys
import pango

try:
    import pygtk
    pygtk.require("2.0")
    import gobject
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

from treefilebrowser import *

class VOAAntennaChooser:
    
    """GUI to select VOACAP antennas."""
    
    def __init__(self, itshfbc_path=(), size=(), parent=None):
        self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaAntennaChooser.glade")
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.uifile)

        self.get_objects("antenna_chooser_dialog", 
                            "preview_textview",
                            "file_tv")

        self.preview_buffer = self.preview_textview.get_buffer()
        
        self.preview_textview.modify_font(pango.FontDescription("Luxi Mono 8"))
        if size == ():
            size = (700,400)
        #print size[0], size[1]
        self.antenna_chooser_dialog.set_size_request(size[0], size[1])
        self.antenna_chooser_dialog.set_transient_for(parent)
        self.antenna_path = itshfbc_path+os.sep+'antennas'
        
        # The tfb and tv aren't really OO at the moment and need tidying up.
        self.tfb = TreeFileBrowser(root = self.antenna_path, view = self.file_tv)
        self.file_tv.connect("cursor-changed", self.update_preview)
         
  
    def run(self):
        """This function runs the antenna selection dialog"""  
 
        return_code = self.antenna_chooser_dialog.run()
        
        try:
            antenna_file = self.tfb.get_selected()
            f = open(antenna_file)
            antenna_description = f.readline()
            testLine = f.readline()
            f.close()
            if (testLine.find("parameters") == 9):  
                antenna_file =  self.relpath(antenna_file, self.antenna_path)
                antenna_description = re.sub('\s+', ' ', antenna_description)
                # The line below should be reinstated once python >=2.6
                # becomes common on all distros.
            	#antenna_file = os.path.relpath(antenna_file, self.antenna_path)
            else:
            	antenna_file = None
            	antenna_description = None
        except:
            antenna_file = None
            antenna_description = None
        self.antenna_chooser_dialog.destroy()
        #print self.antenna_chooser_dialog.get_size()
        return return_code, antenna_file, antenna_description, self.antenna_chooser_dialog.get_size()


    def update_preview(self, file_chooser):
        filename = self.tfb.get_selected()
        try:
            f = open(filename)
            description = f.readline()
            params = f.readline().split()
            if (params[2] == 'parameters'):
                for i in range(int(params[0])):
                    description = description + f.readline()
                #description = re.sub(r'\s+', ' ', description)
            	self.preview_buffer.set_text(description)
            else:
               self.preview_buffer.set_text('')
            f.close()
        except:
            self.preview_buffer.set_text('')
        return

       
    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError, _("Widget '%s' not found") % name
            setattr(self, name, widget)
    
    # A crude home grown version of the python 2.6 os.path.relpath method
    # that will probably be replaced with the real thing once python
    # >=2.6 becomes wiidespread.
    def relpath(self, path, root):
        return path[len(root)+1:]
        

