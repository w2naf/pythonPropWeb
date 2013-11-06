#!/usr/bin/env python
#
# File: voacapSiteChooser
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
import itertools

from hamlocation import *
from treefilebrowser import *

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

class VOASiteChooser:
    
    """GUI to select tx/rx locations fromVOAArea Input Files"""

    lcase_letters = map(chr, range(97, 123))
    ucase_letters = map(chr, range(65, 91))
    
    def __init__(self, location=HamLocation(), map_size=(), itshfbc_path = '', parent=None):
        # Delete any trailing locator from the site name
        #_name = location.get_name()
        #_loc = re.compile (r"\[\D\D\d\d\D\D\]\s*$")
        #if re.search(_loc, _name):
        #    print "found locator"
        #self.locator_append_checkbutton.set_state(re.search(_loc, _name))
        #location.set_name(_loc.split(_name)[0])
        self.return_location = location
        self.map_size = map_size
        
        #load the dialog from the glade file      
        self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaSiteChooser.glade")
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.uifile)

        self.get_objects("site_chooser_dialog", "eventbox1", 
                                "lat_spinbutton", "lon_spinbutton", "name_entry", 
                                "locator_combo1", "locator_combo2", "locator_combo3",
                                "locator_combo4", "locator_combo5", "locator_combo6",
                                "locator_append_checkbutton", "geo_tv", "file_tv")

        self.site_chooser_dialog.set_transient_for(parent)
        # put the image from pixbuf, to make it resizable
        self.map_image_aspect_ratio = None

        evb = self.wTree.get_object('eventbox1')
        
        map_file = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "map.jpg")

        # the original clean pixbuf map
        self.o_pixbuf = gtk.gdk.pixbuf_new_from_file(map_file)

        w, h = self.o_pixbuf.get_width(), self.o_pixbuf.get_height()
        if not self.map_size:
            self.map_size = (w,h)
        self.map_image = gtk.image_new_from_pixbuf(self.o_pixbuf)
        self.map_image.set_size_request(w,h) # allow to downsize to map_file original size

        points = []
        points.append(self.location2map_point(self.return_location))
        self.set_map_points(points) # this sets up self.map_image

        evb.add(self.map_image) 
        self.map_image.show()

        # Delete any trailing locator from the site name
        _name = location.get_name()
        _loc = re.compile (r"\[\D\D\d\d\D\D\]\s*$")
        if re.search(_loc, _name):
            self.locator_append_checkbutton.set_active(True)
        self.return_location.set_name(_loc.split(_name)[0])
        

        #run the dialog and store the response      
        self.populate_locator_combos()
        self.update_spinbuttons(self.return_location)
        self.set_locator_ui(self.return_location.get_locator())
        self.name_entry.set_text(self.return_location.get_name())

        #Create event dictionay and connect it
        event_dic = { 
                        "on_lat_spinbutton_value_changed" : self.update_locator_ui,
                        "on_lon_spinbutton_value_changed" : self.update_locator_ui,
                        "on_eventbox1_size_allocate" : self.resize_image,
                        "on_eventbox1_button_press_event" : self.set_location_from_map
                        }
        self.wTree.connect_signals(event_dic)
       

        # The locator widgets need to be connected individually.  The handlerIDs are 
        # used to block signals when setting the loctaor widget programatically
        
        self.locator_combo1_handler_id = self.locator_combo1.connect("changed", self.set_location_from_locator)
        self.locator_combo2_handler_id = self.locator_combo2.connect("changed", self.set_location_from_locator)
        self.locator_combo3_handler_id = self.locator_combo3.connect("changed", self.set_location_from_locator)
        self.locator_combo4_handler_id = self.locator_combo4.connect("changed", self.set_location_from_locator)
        self.locator_combo5_handler_id = self.locator_combo5.connect("changed", self.set_location_from_locator)
        self.locator_combo6_handler_id = self.locator_combo6.connect("changed", self.set_location_from_locator)
        
        self.locator_combos = ((self.locator_combo1,self.locator_combo1_handler_id), 
                                            (self.locator_combo2, self.locator_combo2_handler_id),
                                            (self.locator_combo3, self.locator_combo3_handler_id), 
                                            (self.locator_combo4, self.locator_combo4_handler_id),
                                            (self.locator_combo5, self.locator_combo5_handler_id), 
                                            (self.locator_combo6, self.locator_combo6_handler_id))
        # Set up the file selection area
        self.tfb = TreeFileBrowser(root = itshfbc_path, view = self.file_tv, file_types = ('*.geo', '*.GEO'))
        self.file_tv.connect("cursor-changed", self.update_geo_tv)
        
        sm = self.geo_tv.get_selection()
        sm.set_mode(gtk.SELECTION_SINGLE)
        sm.set_select_function(self.geo_tv_selected)
        
        self.alpha_numeric_re = re.compile('[\W_]+')
        self.latitude_column = 0
        self.longitude_column = 0
         

    def run(self):
        """This function runs the site selection dialog"""  
        self.result = self.site_chooser_dialog.run()
        _site_name = self.name_entry.get_text()
        if self.locator_append_checkbutton.get_active():
            _site_name = _site_name + ' ['+self.return_location.get_locator()+']'
        self.return_location.set_name(_site_name)
        self.site_chooser_dialog.destroy()
        return self.result, self.return_location, self.map_size
        

    def set_map_points(self, points=[]):
        # points is list of tuples (w,h)
        # get a clean pixbuf and set it's size as indicated by map_size
        w,h = self.map_size
#        print "point ms", self.map_size
        pixbuf = self.o_pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        # the point size is 1% of map width, minimum 3px
        radius = 3 if (w / 200.0) < 3 else int(round(w/200.0))
        drawable, mask = pixbuf.render_pixmap_and_mask()
        cmap = drawable.get_colormap()
        gc = drawable.new_gc() 
        fill = False
        for point in points:
#            print "drawing circle at ", point
            red = cmap.alloc_color("red")
            gc.set_foreground(red)
            gc.set_background(red)
            drawable.draw_arc(gc, fill, point[0] - radius, point[1] - radius, radius*2, radius*2, 0, 23040)
            drawable.draw_line(gc, point[0] - 4 - radius,  point[1], 
                                   point[0] + 4 + radius,  point[1])
            drawable.draw_line(gc, point[0], point[1] - 4 - radius,
                                   point[0], point[1] + 4 + radius )
        pixbuf.get_from_drawable(drawable, cmap, 0, 0, 0,0, w,h)
        self.map_image.set_from_pixbuf(pixbuf)


    def resize_image(self, widget, rect):
        new_w = rect[2]
        new_h = rect[3]
        if self.map_size == (new_w, new_h):
            return False
#        print "map size: %s new_size %s" % (self.map_size, (new_w, new_h))
        self.map_size = (new_w, new_h)
        points = []
        points.append(self.location2map_point(self.return_location))
        self.set_map_points(points) # this sets up self.map_image
        return False


    def populate_locator_combos(self):
        self.populate_combo(self.locator_combo1, map(chr, range(65, 83)))
        self.populate_combo(self.locator_combo2, map(chr, range(65, 83)))
        self.populate_combo(self.locator_combo3, range(0, 10))
        self.populate_combo(self.locator_combo4, range(0, 10))
        self.populate_combo(self.locator_combo5, map(chr, range(97, 121)))
        self.populate_combo(self.locator_combo6, map(chr, range(97, 121)))
        
        
    def populate_combo(self, cb, list):
        list_model = gtk.ListStore(gobject.TYPE_STRING) 
        for af in list:
            list_model.append([af])
        cb.set_model(list_model)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)
        #cb.set_wrap_width(20)
        cb.set_active(0)    

        
    # Function called when the lat/lon is changed in the entry boxes
    def update_locator_ui(self, widget):
        if widget == self.lat_spinbutton:
            self.return_location.set_latitude(self.lat_spinbutton.get_value())
        elif widget == self.lon_spinbutton:
            self.return_location.set_longitude(self.lon_spinbutton.get_value())
        self.block_locator_combos(True)
        self.set_locator_ui(self.return_location.get_locator())
        points = [self.location2map_point(self.return_location)]
        self.set_map_points(points)
        self.block_locator_combos(False)            
        # Unblock the locator ombo signals
        

    def block_locator_combos(self, block):
        if (block):
            for combo, handler in self.locator_combos:
                combo.handler_block(handler)
        else:
            for combo, handler in self.locator_combos:
                combo.handler_unblock(handler)                                  
        
    # Updates the locator UI elements to the argument passed in 'locator'
    # todo some error checking would be nice....
    def set_locator_ui(self, locator):
        locator = locator.upper()
        self.locator_combo1.set_active(self.ucase_letters.index(locator[0]))
        self.locator_combo2.set_active(self.ucase_letters.index(locator[1]))    
        self.locator_combo3.set_active(int(locator[2]))
        self.locator_combo4.set_active(int(locator[3]))                     
        # todo make this an 'if' in case we get a four digit locator    
        self.locator_combo5.set_active(self.ucase_letters.index(locator[4]))
        self.locator_combo6.set_active(self.ucase_letters.index(locator[5]))    

    def location2map_point(self, location):
        w,h = self.map_size
#        print "self.map_size", self.map_size
        lat = location.get_latitude()
        lon = location.get_longitude()
        #lon = ((event.x/w) * 360.0) - 180.0
        pw = ((lon + 180.0) / 360.0) * w
        #lat = 90.0 - ((event.y/h) * 180)
        ph = abs( ((lat - 90.0) / 180) * h)
#        print "loc lat %s lon %s" % (lat, lon)
#        print "loc lat p %s lon p %s" % (ph,pw)
        return (int(round(pw)), int(round(ph)))

    def set_location_from_map(self, widget, event):
        pixbuf = self.map_image.get_pixbuf()
        w,h = pixbuf.get_width(), pixbuf.get_height()
        if not (w > event.x > 0)  or not (h > event.y > 0): return  # out of map bounds
        lon = ((event.x/w) * 360.0) - 180.0
        lat = 90.0 - ((event.y/h) * 180)
#        print "click on %s map_size %s" % ((event.x, event.y), self.map_size) 
#        print "click lon ", lon, "lat", lat
        self.return_location.set_latitude_longitude(lat, lon)
        self.update_spinbuttons(self.return_location)
        self.set_locator_ui(self.return_location.get_locator())
        # redraw-point
        points = [(int(event.x), int(event.y))]
        self.set_map_points(points)
        

    def set_location_from_locator(self, widget):
        loc = ''        
        for cb, handlerID in self.locator_combos:
            loc = loc + self.get_active_text(cb)
        self.return_location.set_locator(loc)
        self.update_spinbuttons(self.return_location)
        points = [self.location2map_point(self.return_location)]
        self.set_map_points(points)
        
    def update_spinbuttons(self,location):
        self.lat_spinbutton.set_value(location.get_latitude())
        self.lon_spinbutton.set_value(location.get_longitude())
        self.name_entry.set_text(location.get_name())
    
    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return ''
        return model[active][0]

    ####################################################
    # File Selection methods follow
    ####################################################
    def update_geo_tv(self, file_chooser):
        filename = self.tfb.get_selected()
        try:
            if filename.endswith('.geo'):
                f = open(filename)
                header_is_defined = False
                for line in f:
                    if line.startswith('|'):
                        start_index = 0
                        end_index = 0
                        headers = []
                        while end_index >= 0:
                            end_index = line.find('|', start_index)
                            heading = line[start_index:end_index].strip()
                            heading = re.sub(r'=', '', heading)
                            heading = heading.title()
                            if len(heading) > 0:
                                headers.append((heading, int(start_index)-1, int(end_index), len(headers)))
                            start_index = end_index + 1
                        self.geo_model = gtk.ListStore(*([str] * len(headers)))
                        self.build_geo_tv(headers)
                        header_is_defined = True
                    elif header_is_defined:
                        try:
                            row = []
                            for column in headers:
                                row.append((line[column[1]:column[2]]).strip())
                            self.geo_model.append(row)       
                        except:
                            print 'Failed to read line: ', line
                            print 'with error ',sys.exc_info()
                f.close()
                self.geo_tv.set_model(self.geo_model)
        except:
            pass
            #print 'Error parsing geo file.'
            #print sys.exc_info()
            try:
                self.geo_model.clear()
            except AttributeError:
                pass
        return

    
    def remove_all_tv_columns(self, tv):
        columns = tv.get_columns()
        for col in columns:
            tv.remove_column(col)


    def build_geo_tv(self, headers):
        self.remove_all_tv_columns(self.geo_tv)
        for column in headers:
            title = column[0]
            cell = gtk.CellRendererText()
            cell.set_property('xalign', 1.0)
            tvcol = gtk.TreeViewColumn(title, cell)
            tvcol.add_attribute(cell, 'text' , int(column[3]))
            if title.startswith('Lat'):
                self.latitude_column = int(column[3])
            elif title.startswith('Lon'):
                self.longitude_column = int(column[3])
            tvcol.set_resizable(True)
            tvcol.set_reorderable(True)
            tvcol.set_sort_column_id(int(column[3]))
            self.geo_tv.append_column(tvcol)


    def geo_tv_selected(self, path):
        geo_iter = self.geo_model.get_iter(path)
        title = ''
        for col in range(0, self.geo_model.get_n_columns()):
            if col == self.latitude_column:
                self.return_location.set_latitude(self.get_decimal_coordinate(self.geo_model.get_value(geo_iter, col)))
            elif col == self.longitude_column:
                self.return_location.set_longitude(self.get_decimal_coordinate(self.geo_model.get_value(geo_iter, col)))
            else:
                title = title + ' ' + self.geo_model.get_value(geo_iter, col)
        self.return_location.set_name(title)
        self.update_spinbuttons(self.return_location)        
        return True

    def get_decimal_coordinate(self, ll):
        val = ll.split()
        dec = float(val[0]) + float(val[1])/60.0
        if ((val[2] == 'S') or (val[2] == 'W')):
            dec = -dec
        return dec
        
        
    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError, _("Widget '%s' not found") % name
            setattr(self, name, widget)

