#!/usr/bin/env python
#
# File: voacapgui
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

from __future__ import with_statement
import sys
import os
import datetime
import subprocess
import time
import re
from dateutil.relativedelta import relativedelta

from ConfigParser import *
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


import gettext
import locale
GETTEXT_DOMAIN = 'voacapgui'
LOCALE_PATH = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), 'po')

langs = []
lc, enc = locale.getdefaultlocale()
if lc:
    langs = [lc]
language = os.environ.get('LANGUAGE', None)
if language:
    langs += language.split(':')
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)
lang = gettext.translation(GETTEXT_DOMAIN, LOCALE_PATH, languages=langs, fallback=True)
lang.install()

# glade file
# see http://bugzilla.gnome.org/show_bug.cgi?id=344926 for why the
# next two commands look repeated.
gtk.glade.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gtk.glade.textdomain(GETTEXT_DOMAIN)
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)


from voaTextFileViewDialog import *
from voaDatFile import *
from voaDefaults import *
from voaSiteChooser import *
from voaP2PPlot import *
from voaP2PPlotgui import *
from voaAreaPlotgui import *
from ssnFetch import *
from voaSSNThumb import *
from voaFile import *
from voaAreaChooser import *
from voaAntennaChooser import *


class VOACAP_GUI:
    """GUI to create VOAArea Input Files"""

    # Determine where the itshfbc and prefs files are, based on OS
    # The windows paths are guesses and need checking....
    if os.name == 'nt':
        itshfbc_path = 'C:\itshfbc'
        prefs_dir = 'C:\itshfbc\database\\'
    else:
        itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc'
        prefs_dir = os.path.expanduser("~")+os.sep+'.voacapgui'+os.sep


    prefs_path = prefs_dir + 'voacapgui.prefs'
    ssn_path = prefs_dir + 'sunspot.predict'
    # Check if the prefs directory exists, create one if if it doesn't
    # (This is probably not required as the installer will probbaly end up
    # creating and populating this directory.

    if not os.path.isdir(prefs_dir):
        os.makedirs(prefs_dir) 
    
    #ant_list = []

    firstCornerX = 0
    firstCornerY = 0

    area_rect = VOAAreaRect()
    
    model_list = ('CCIR', 'URSI88')
    path_list = (_('Short'), _('Long'))
    
    # These need to be lists later on to support multiple antennas    
    tx_antenna_path = ''
    rx_antenna_path = ''
   
    main_window_size = (560, 410)
    site_chooser_map_size = area_chooser_map_size = (384,192)
    antenna_chooser_size = (500,400)

    def __init__(self):
        self.area_templates_file = None
        #Set the GUI file    
        self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voacapgui.glade")
        self.wTree = gtk.Builder()
        self.wTree.add_from_file(self.uifile)

        self.get_objects("main_window", "statusbar", "notebook", 
                "tx_site_button", "tx_site_entry", "tx_lat_spinbutton",
                "tx_lon_spinbutton", "tx_antenna_button", "tx_antenna_entry",
                "tx_bearing_button", "tx_bearing_spinbutton",
                "tx_power_spinbutton", "rx_site_button", "rx_site_entry",
                "rx_lat_spinbutton", "rx_lon_spinbutton", "rx_antenna_button",
                "rx_antenna_entry", "rx_bearing_button",
                "rx_bearing_spinbutton", "ssn_tv", "ssn_plot_box",
                "ssn_file_data_label", "ssn_web_update_button",
                "foe_spinbutton", "fof1_spinbutton", "fof2_spinbutton",
                "foes_spinbutton", "model_combo", "path_combo",
                "mm_noise_spinbutton", "min_toa_spinbutton",
                "reliability_spinbutton", "snr_spinbutton", "mpath_spinbutton",
                "delay_spinbutton", "area_tv", "delbt", "savebt",
                "templatescb", "gridsizespinbutton", "addtemplbt", "areayearspinbutton",
                "freqspinbutton", "monthspinbutton", "utcspinbutton", "addbt",
                "rstbt", "areabt", "area_label", "arearunbt", "p2pmy_tv",
                "p2pfreq_tv", "p2pmydelbt", "p2pmyrstbt", "p2pfreqdelbt",
                "p2pfreqrstbt", "p2psavebt", "p2padd_mybt", "p2padd_freqbt",
                "p2pfreqspinbutton", "p2pdayspinbutton", "p2pmonthspinbutton",
                "p2pyearspinbutton", "p2pcircuitcb", "p2pgraphcb", "p2prunbt",
                "p2pcalbt", "p2pusedayck", "p2pmacrocb", "p2pmacroaddbt",
                )
        self.p2pcalbt.set_label(_('_Cal'))
        self.p2pcalbt.set_image(gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON))

        self.p2p_useday = False
        self.p2pdayspinbutton.set_sensitive(self.p2p_useday)
        self.p2puseday_handler_id = self.p2pusedayck.connect('toggled', self.p2p_useday_tog)
        today = datetime.today()
        self.p2pyearspinbutton.set_value(today.year)
        self.p2pmonthspinbutton.set_value(today.month)
        self.p2pdayspinbutton.set_value(today.day)
        self.p2pfreqspinbutton.set_value(14.2)

        self.main_window.resize(self.main_window_size[0], self.main_window_size[1])
        
        _model = gtk.ListStore(gobject.TYPE_STRING) 
        for item in self.model_list:
            _model.append([item])
        self.populate_combo(self.model_combo, _model)

        _model = gtk.ListStore(gobject.TYPE_STRING) 
        for item in self.path_list:
            _model.append([item])
        self.populate_combo(self.path_combo, _model)    
        
       
        self.max_vg_files_warn = False
        self.max_frequencies_warn = False
        if os.name == 'posix':
            self.max_vg_files = 25 #This was originally set to 12 in earlier versions of voacapl.
        else:
            self.max_vg_files = 9 # DOS 8.3 filenames
        self.gridsizespinbutton.set_value(125)
        self.areayearspinbutton.set_value(today.year)
        self.monthspinbutton.set_value(today.month)
        self.freqspinbutton.set_value(14.1)
        
        self.ssn_repo = SSNFetch(save_location = self.ssn_path, s_bar=self.statusbar)
        _min, _max = self.ssn_repo.get_data_range()
        self.p2pyearspinbutton.set_range(float(_min), float(_max))
        self.areayearspinbutton.set_range(float(_min), float(_max))
        #self.write_ssns(self.ssn_repo.get_ssn_list())
        
        self.build_area_tv()
        self.ssn_build_tv()
        self.build_p2p_tvs()
        self.build_circuitcb()
        self.build_graphcb()
        self.build_macrocb()
        self.read_user_prefs()
        
        if not self.area_templates_file:
            self.build_new_template_file()
        self.area_label.set_text(self.area_rect.get_formatted_string())
        self.build_area_template_ts()
        
        #Create event dictionay and connect it
        event_dic = { "on_main_window_destroy" : self.quit_application,
            "on_tx_site_button_clicked" : (self.choose_site, 'tx'),
            "on_rx_site_button_clicked" : (self.choose_site, 'rx'),
            "on_tx_antenna_button_clicked" : (self.choose_antenna, 'tx'),
            "on_rx_antenna_button_clicked" : (self.choose_antenna, 'rx'),
            "on_tx_bearing_button_clicked" : (self.calculate_antenna_bearing, 'tx'),
            "on_rx_bearing_button_clicked" : (self.calculate_antenna_bearing, 'rx'),
            "on_mi_circuit_activate" : self.verify_input_data,
            "on_mi_graph_activate" : self.verify_input_data,
            "on_mi_run_activate": self.run_prediction,
            "on_mi_about_activate" : self.show_about_dialog,
            "on_mi_quit_activate" : self.quit_application,
            "on_main_window_destroy" : self.quit_application,
            "on_ssn_web_update_button_clicked" : self.update_ssn_table,

            # notebook area page widgets event dict 
            'on_notebook_switch_page' : self.nb_switch_page,
            'on_addbt_clicked' : self.area_add_tv_row_from_user,
            'on_addtemplbt_clicked' : self.area_add_template,
            'on_templatescb_changed' : self.area_templatescb_change,
            'on_delbt_clicked' : self.area_del_tv_row,
            'on_savebt_clicked' : self.area_save_as_template,
            'on_rstbt_clicked' : self.area_clean_tv,
            'on_areabt_clicked' : self.show_area_chooser,
            'on_arearunbt_clicked' : self.run_prediction, 
            
            # notebook p2p page widgets event dict
            'on_p2padd_mybt_clicked' : self.p2pmy_add_tv_row_from_user,
            'on_p2padd_freqbt_clicked' : self.p2pfreq_add_tv_row_from_user,
            'on_p2pmydelbt_clicked' : self.p2p_del_my_tv_row,
            'on_p2pfreqdelbt_clicked' : self.p2p_del_freq_tv_row,
            'on_p2psavebt_clicked' : self.p2p_save_as_template,
            'on_p2pmyrstbt_clicked' : self.p2p_clean_my_tv,
            'on_p2pfreqrstbt_clicked' : self.p2p_clean_freq_tv,
            'on_p2prunbt_clicked' : self.run_prediction,
            'on_p2pcalbt_clicked' : self.p2p_calendar,
#            'on_p2pusedayck_toggled' : self.p2p_useday_tog,
            'on_p2pmacroaddbt_clicked' : self.p2p_add_macro,
            }
        self.wTree.connect_signals(event_dic)    

        # area plot accelgrp
        self.area_accelgrp = None

        # test for ~/itshfbc tree    
        if not os.path.exists(self.itshfbc_path):
            e = _("ITSHFBC directory not found")
            if os.name == 'posix':
                e_os = _("Please install voacap for Linux and run 'makeitshfbc'.\n")
            e_os += _("A 'itshfbc' directory cannot be found at: %s.\n") % (self.itshfbc_path)
            e_os += _("Please install voacap before running voacapgui.") 
            dialog = gtk.MessageDialog(self.main_window, 
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, e )
            dialog.format_secondary_text(e_os)     
            dialog.run()
            dialog.destroy()
            return -1
            
        

    def populate_combo(self, cb, model):
        cb.set_model(model)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)
        #cb.set_wrap_width(20)
        cb.set_active(0)    

            
    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError, "Widget '%s' not found" % name
            setattr(self, name, widget)
            
            
    def choose_antenna(self, widget, site):
        #print self.antenna_chooser_size
        dialog  = VOAAntennaChooser(self.itshfbc_path, size=self.antenna_chooser_size, parent=self.main_window) 
        return_code, return_antenna, antenna_description, self.antenna_chooser_size = dialog.run()  
        #print self.antenna_chooser_size  
        if ((return_code == 0) and (return_antenna)): # response_id: 0=OK, 1=Cancel  
            if site == 'tx':
                self.tx_antenna_entry.set_text(return_antenna + ' : ' + antenna_description)
                self.tx_antenna_path = return_antenna
            else:
                self.rx_antenna_entry.set_text(return_antenna + ' : ' + antenna_description)
                self.rx_antenna_path = return_antenna        
       

    def choose_site(self, widget, site):
        if site == 'tx':
            lat = self.tx_lat_spinbutton.get_value()
            lon = self.tx_lon_spinbutton.get_value()
            name = self.tx_site_entry.get_text()
        elif site == 'rx':
            lat = self.rx_lat_spinbutton.get_value()
            lon = self.rx_lon_spinbutton.get_value()
            name = self.rx_site_entry.get_text()
        else:
            lat = 0
            lon = 0
            name = ''

        dialog = VOASiteChooser(HamLocation(lat, lon, name), \
                            self.site_chooser_map_size, \
                            itshfbc_path=self.itshfbc_path, \
                            parent=self.main_window)
        return_code, location, self.site_chooser_map_size = dialog.run()
        if (return_code == 0): # response_id: 0=OK, 1=Cancel
            if site == 'tx':
                self.tx_site_entry.set_text(location.get_name())
                self.tx_lat_spinbutton.set_value(location.get_latitude())
                self.tx_lon_spinbutton.set_value(location.get_longitude())
            else:
                self.rx_site_entry.set_text(location.get_name())
                self.rx_lat_spinbutton.set_value(location.get_latitude())
                self.rx_lon_spinbutton.set_value(location.get_longitude())
                
                
    def calculate_antenna_bearing(self, widget, site):
        try:
            tx_loc = HamLocation(self.tx_lat_spinbutton.get_value(),
                                        lon = self.tx_lon_spinbutton.get_value())
            rx_loc = HamLocation(float(self.rx_lat_spinbutton.get_value()),
                                        lon = self.rx_lon_spinbutton.get_value())
        except Exception:
            #todo add a note to the status bar explaining the reason
            #for the failure to actually do anything
            return                            
        if site == 'tx':
            bearing, distance = tx_loc.path_to(rx_loc)
            self.tx_bearing_spinbutton.set_value(bearing)
        else:
            bearing, distance = rx_loc.path_to(tx_loc)
            self.rx_bearing_spinbutton.set_value(bearing)
                    

    
    def read_user_prefs(self) :
        config = ConfigParser(VOADefaultDictionary())
        config.read(self.prefs_path)
        #set some defaults here for the system variables
        try:
            self.foe_spinbutton.set_value(float(config.get('DEFAULT','foe')))
            self.fof1_spinbutton.set_value(float(config.get('DEFAULT','fof1')))                        
            self.fof2_spinbutton.set_value(float(config.get('DEFAULT','fof2')))                        
            self.foes_spinbutton.set_value(float(config.get('DEFAULT','foes')))
            self.model_combo.set_active(int(config.get('DEFAULT', 'model')))
            self.path_combo.set_active(int(config.get('DEFAULT', 'path')))            
    
            self.mm_noise_spinbutton.set_value(float(config.get('DEFAULT','mm_noise')))
            self.min_toa_spinbutton.set_value(float(config.get('DEFAULT','min_toa')))
            self.reliability_spinbutton.set_value(float(config.get('DEFAULT','required_reliability')))
            self.snr_spinbutton.set_value(float(config.get('DEFAULT','required_snr')))
            self.mpath_spinbutton.set_value(float(config.get('DEFAULT','mpath')))
            self.delay_spinbutton.set_value(float(config.get('DEFAULT','delay')))    
            
            self.tx_bearing_spinbutton.set_value(float(config.get('DEFAULT', 'tx_bearing')))
            self.tx_power_spinbutton.set_value(float(config.get('DEFAULT', 'tx_power')))
            self.rx_bearing_spinbutton.set_value(float(config.get('DEFAULT', 'rx_bearing')))
                            
            self.tx_site_entry.set_text(config.get('tx site','name'))
            self.tx_lat_spinbutton.set_value(float(config.get('tx site','lat')))
            self.tx_lon_spinbutton.set_value(float(config.get('tx site','lon')))
            self.tx_antenna_entry.set_text(config.get('tx site', 'antenna' )) 
            self.tx_antenna_path, sep, suffix = (config.get('tx site', 'antenna' )).partition(' :')
            self.tx_bearing_spinbutton.set_value(float(config.get('tx site', 'bearing')))
            self.tx_power_spinbutton.set_value(float(config.get('tx site', 'power')))
            self.rx_site_entry.set_text(config.get('rx site','name'))
            self.rx_lat_spinbutton.set_value(float(config.get('rx site','lat')))
            self.rx_lon_spinbutton.set_value(float(config.get('rx site','lon')))
            self.rx_antenna_entry.set_text(config.get('rx site', 'antenna' ))
            self.rx_antenna_path, sep, suffix = (config.get('rx site', 'antenna' )).partition(' :')
            self.rx_bearing_spinbutton.set_value(float(config.get('rx site', 'bearing')))    

            self.site_chooser_map_size = (config.getint('site chooser','map_width'), 
                                          config.getint('site chooser','map_height'))
            self.area_chooser_map_size = (config.getint('area chooser','map_width'), 
                                          config.getint('area chooser','map_height'))
            self.antenna_chooser_size = (config.getint('antenna chooser','width'), 
                                          config.getint('antenna chooser','height'))
            self.gridsizespinbutton.set_value(config.getint('area', 'gridsize'))
            self.areayearspinbutton.set_value(config.getint('area','year'))
            self.monthspinbutton.set_value(config.getint('area','month'))
            self.utcspinbutton.set_value(config.getint('area','utc'))
            self.freqspinbutton.set_value(config.getfloat('area', 'frequency'))
            self.area_templates_file = config.get('area', 'templates_file')
            self.area_rect=VOAAreaRect(config.getfloat('area','sw_lat'), 
                                        config.getfloat('area','sw_lon'),
                                        config.getfloat('area','ne_lat'),
                                        config.getfloat('area','ne_lon'))
            self.area_label.set_text(self.area_rect.get_formatted_string())
        except Exception, X:
            print 'Error reading the user prefs: %s - %s' % (Exception, X)
      

    def save_user_prefs(self):

        config = ConfigParser()
        # voaSiteChooser map size
        config.add_section('site chooser')
        config.set('site chooser', 'map_width', self.site_chooser_map_size[0])
        config.set('site chooser', 'map_height', self.site_chooser_map_size[1])
        # voaAreaChooser map size
        config.add_section('area chooser')
        config.set('area chooser', 'map_width', self.area_chooser_map_size[0])
        config.set('area chooser', 'map_height', self.area_chooser_map_size[1])
        # voaAreaChooser map size
        if self.antenna_chooser_size:
            config.add_section('antenna chooser')
            config.set('antenna chooser', 'width', self.antenna_chooser_size[0])
            config.set('antenna chooser', 'height', self.antenna_chooser_size[1])
        # Tx Site Parameters
        config.add_section('tx site')
        config.set('tx site', 'name', self.tx_site_entry.get_text())
        config.set('tx site', 'lat', self.tx_lat_spinbutton.get_value())
        config.set('tx site', 'lon', self.tx_lon_spinbutton.get_value())
        config.set('tx site', 'antenna', self.tx_antenna_entry.get_text())    
        config.set('tx site', 'bearing', self.tx_bearing_spinbutton.get_value())
        config.set('tx site', 'power', self.tx_power_spinbutton.get_value())
        # Rx Site Parameters
        config.add_section('rx site')
        config.set('rx site', 'name', self.rx_site_entry.get_text())
        config.set('rx site', 'lat', self.rx_lat_spinbutton.get_value())
        config.set('rx site', 'lon', self.rx_lon_spinbutton.get_value())
        config.set('rx site', 'antenna', self.rx_antenna_entry.get_text())    
        config.set('rx site', 'bearing', self.rx_bearing_spinbutton.get_value())   
        # Ionospheric Parameters
        config.set('DEFAULT', 'foe', self.foe_spinbutton.get_value())   
        config.set('DEFAULT', 'fof1', self.fof1_spinbutton.get_value())
        config.set('DEFAULT', 'fof2', self.fof2_spinbutton.get_value())    
        config.set('DEFAULT', 'foes', self.foes_spinbutton.get_value())    
        config.set('DEFAULT', 'model', self.model_combo.get_active())
        config.set('DEFAULT', 'path', self.path_combo.get_active())                
        # System parameters
        config.set('DEFAULT','mm_noise', self.mm_noise_spinbutton.get_value())    
        config.set('DEFAULT','min_toa', self.min_toa_spinbutton.get_value())
        config.set('DEFAULT','required_reliability', self.reliability_spinbutton.get_value())
        config.set('DEFAULT','required_snr', self.snr_spinbutton.get_value())                                    
        config.set('DEFAULT','mpath', self.mpath_spinbutton.get_value())    
        config.set('DEFAULT','delay', self.delay_spinbutton.get_value())
        # area parameters
        config.add_section('area')
        config.set('area','gridsize', self.gridsizespinbutton.get_value_as_int())
        config.set('area','year', self.areayearspinbutton.get_value_as_int())
        config.set('area','month', self.monthspinbutton.get_value_as_int())
        config.set('area','utc', self.utcspinbutton.get_value_as_int())
        config.set('area','frequency', self.freqspinbutton.get_value())
        config.set('area','sw_lat', self.area_rect.sw_lat)
        config.set('area','sw_lon', self.area_rect.sw_lon)
        config.set('area','ne_lat', self.area_rect.ne_lat)
        config.set('area','ne_lon', self.area_rect.ne_lon)
        config.set('area','templates_file', self.area_templates_file if self.area_templates_file else '')
        
        with open(self.prefs_path, 'w') as configfile:
            config.write(configfile)



    # This function is called everytime a run submenu is activated
    # It enables/disables further submenus until input data is valid
    # todo use the status bar to indicate the reason for any failure            
    def verify_input_data(self, widget):
        valid = (self.is_ssn_valid() and self.is_tx_site_data_valid())
        self.arearunbt.set_sensitive(self.savebt.props.sensitive & valid)

    def is_ssn_valid(self):
        _has_entry = False  
        # jwtodo check some ssn values exist 
        #
        # This obviously needs fixing.
        _has_entry = True
        #
        # 
        if _has_entry != True:
            context_id = self.statusbar.get_context_id("nossns")
            self.statusbar.push(context_id, _("No SSNs defined"))
        return _has_entry
        
        
    def is_tx_site_data_valid(self):
        _is_valid = True
        if self.tx_power_spinbutton.get_value == 0: _is_valid = False
        if self.tx_antenna_path == '': _is_valid = False
        return _is_valid

    def is_rx_site_data_valid(self):
        if self.rx_antenna_path == '': _is_valid = False
            
#gettext here
#This function is used to force an update
    def update_ssn_table(self, widget):     
        self.ssn_repo.update_ssn_file() #Force an update
#        self.update_ssn_data_label()
        self.ssn_file_data_label.set_text(self.ssn_repo.get_file_data())
        #self.write_ssns(self.ssn_repo.get_ssn_list())
       
        
    def update_ssn_data_label(self):
        _text = _("SSN Data Last Updated:\n")
        _text += self.ssn_repo.get_file_mtime_str()
        self.ssn_file_data_label.set_text(_text)        
    
    #jwtodo figure out what this function does...
    #def write_ssns(self, ssns):
    #    print 'Normally around this time I like to write the SSNs...'
        

    def build_p2p_tvs(self):
       # grey out delete and save buttons, since there are no entries in the model
        self.p2pmydelbt.set_sensitive(False)
        self.p2pmyrstbt.set_sensitive(False)
        self.p2pfreqdelbt.set_sensitive(False)
        self.p2pfreqrstbt.set_sensitive(False)
        #?
        self.p2psavebt.set_sensitive(False)
        self.p2prunbt.set_sensitive(False)
        # model:  day, month name, month_ordinal, year
        col_t = [ gobject.TYPE_UINT,
                  gobject.TYPE_STRING, gobject.TYPE_UINT, gobject.TYPE_UINT]
        model_my = gtk.ListStore(*col_t)

        col_t = [gobject.TYPE_STRING]
        model_freq = gtk.ListStore(*col_t)

        self.p2pmy_tv.set_model(model_my)
        self.p2pfreq_tv.set_model(model_freq)

        self.p2pmy_tv.set_property("rules_hint", True)
        self.p2pmy_tv.set_property("enable_search", False)
        self.p2pmy_tv.set_headers_visible(True)
        self.p2pmy_tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self.p2pfreq_tv.set_property("rules_hint", True)
        self.p2pfreq_tv.set_property("enable_search", False)
        self.p2pfreq_tv.set_headers_visible(True)
        self.p2pfreq_tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        # col idx
        self.p2pmy_tv_idx_day = 0
        self.p2pmy_tv_idx_month_n = 1
        self.p2pmy_tv_idx_month_i = 2
        self.p2pmy_tv_idx_year = 3
        
        self.p2pfreq_tv_idx_freq = 0

        def dow_celldatafunction(column, cell, model, iter, user_data=None):
           t = ''
           d = model.get_value(iter, self.p2pmy_tv_idx_day)
           m = model.get_value(iter, self.p2pmy_tv_idx_month_i)
           y = model.get_value(iter, self.p2pmy_tv_idx_year)
           if d: t = datetime(y,m,d).strftime('%a %d')
           cell.set_property('text', t)

        title = _("Day")
        cell = gtk.CellRendererText()
        tvcol = gtk.TreeViewColumn(title, cell)
#        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_month_n)
#        tvcol.set_sort_column_id(self.p2pmy_tv_idx_month_n)
        tvcol.set_cell_data_func(cell, dow_celldatafunction)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Month")
        cell = gtk.CellRendererText()
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_month_n)
        tvcol.set_sort_column_id(self.p2pmy_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Year")
        cell = gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_year)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.p2pmy_tv_idx_year)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Frequency (MHz)")
        cell = gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pfreq_tv_idx_freq)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.p2pfreq_tv_idx_freq)
        self.p2pfreq_tv.append_column(tvcol)

        
    
    def build_circuitcb(self):
        col_t = [gobject.TYPE_UINT, gobject.TYPE_STRING]
        model = gtk.ListStore(*col_t)
        [ model.append( [i, label]) for i, label in [
                 (0, _("Select method to run")),
                (30, _("Method 30 (Smoothed LP/SP Model)")),
                (25, _("Method 25 (All Modes SP Model)")),
                (22, _("Method 22 (Forced SP Model)")),
                (21, _("Method 21 (Forced LP Model)")),
                (20, _("Method 20 (Complete System Performance)")),
                (15, _("Method 15 (Tx. &amp; Rx. Antenna Pattern)")),
                (14, _("Method 14 (Rx. Antenna Pattern)")),
                (13, _("Method 13 (Tx. Antenna Pattern)")),
                 (9, _("Method 9 (HPF-MUF-FOT Text Graph)"))
                 ]]
        self.p2pcircuitcb.set_model(model)
        cell = gtk.CellRendererText()
        self.p2pcircuitcb.pack_start(cell, True)
        self.p2pcircuitcb.add_attribute(cell, 'text', 1)
        self.p2pcircuitcb.set_active(0)

    def build_graphcb(self):
        col_t = [gobject.TYPE_UINT, gobject.TYPE_STRING]
        model = gtk.ListStore(*col_t)
        [ model.append([i, label]) for i, label in [
            (0, _("Select method to run")),
            (30, _("Method 30 (Smoothed LP/SP Model)")),
            (22, _("Method 22 (Forced SP Model)")),
            (21, _("Method 21 (Forced LP Model)")),
            (20, _("Method 20 (Complete System Performance)")) ]]
        self.p2pgraphcb.set_model(model)
        cell = gtk.CellRendererText()
        self.p2pgraphcb.pack_start(cell, True)
        self.p2pgraphcb.add_attribute(cell, 'text', 1)
        self.p2pgraphcb.set_active(0)

    def build_macrocb(self):
        col_t = [gobject.TYPE_STRING, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT]
        model = gtk.ListStore(*col_t)
        [ model.append([l,f,a]) for l,f,a in [
            (_("Select set to load"), None, None),
            (_("Next 3 months"), self.p2p_macro_next_months, [3]),
            (_("Next 6 months"), self.p2p_macro_next_months, [6]),
            (_("Next 12 months"), self.p2p_macro_next_months, [12]),
            (_("Next 24 months"), self.p2p_macro_next_months, [24]),
            (_("Next 30 days"), self.p2p_macro_next_days, [30]),
            (_("Annual (Quarters)"), self.p2p_macro_annual, [4]),
            (_("Annual (bi-month)"), self.p2p_macro_annual, [6]),
            ]]
        self.p2pmacrocb.set_model(model)
        cell = gtk.CellRendererText()
        self.p2pmacrocb.pack_start(cell, True)
        self.p2pmacrocb.add_attribute(cell, 'text', 0)
        self.p2pmacrocb.set_active(0)


    def p2p_macro_next_months(self, vals):
        day = 0
	
        # if the tv has any entries, use the last one as our
        # start in the sequence.
        tv_model = self.p2pmy_tv.get_model()
        tv_iter = tv_model.get_iter_first()
        if tv_iter == None:
            #empty model
            #so let's add this month to the model
            today = date.today()
            self.p2pmy_add_tv_rows([(day, today.month, today.year)])
        else:
            # the table has entries.  find the last entry and use that 
            # as our starting point for the 'next' months
            last_iter = None
            while tv_iter:
                last_iter = tv_iter
                tv_iter = tv_model.iter_next(tv_iter)
            month = tv_model.get_value(last_iter, self.p2pmy_tv_idx_month_i)
            year = tv_model.get_value(last_iter, self.p2pmy_tv_idx_year)
            today = date(year, month, 1)
            #get the last entry
            #build the value for today
            
        
        mr = relativedelta(months=+1)
        if len(vals) == 1:
            next = today + mr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(day, next.month, next.year)])
                next = next + mr
        elif len(vals) >1:
            pass

    def p2p_macro_next_days(self, vals):
        if not self.p2p_useday:
            self.p2pusedayck.set_active(True)
        today = date.today()
        dr = relativedelta(days=+1)
        if len(vals) == 1:
            next = today + dr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(next.day, next.month, next.year)])
                next = next + dr
        elif len(vals) >1:
            pass

    def p2p_macro_annual(self, vals):
        day = 0
        # start the count from Jan of the current year
        year = self.p2pyearspinbutton.get_value_as_int()
        today = date(year, 1, 1)     
        self.p2pmy_add_tv_rows([(day, today.month, today.year)])
        mr = relativedelta(months=+(12/vals[0]))
        if len(vals) == 1:
            next = today + mr
            for n in range(vals[0]-1):
                self.p2pmy_add_tv_rows([(day, next.month, next.year)])
                next = next + mr
        elif len(vals) >1:
            pass

    def p2p_macro_next_days(self, vals):
        if not self.p2p_useday:
            self.p2pusedayck.set_active(True)
        today = date.today()
        dr = relativedelta(days=+1)
        if len(vals) == 1:
            next = today + dr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(next.day, next.month, next.year)])
                next = next + dr
        elif len(vals) >1:
            pass

    def p2p_add_macro(self, *args):
        model = self.p2pmacrocb.get_model()
        f, args = model.get(self.p2pmacrocb.get_active_iter(),1,2)
        if not f: return
        f(args)

    def build_area_tv(self):
        # grey out delete and save buttons, since there are no entries in the model
        self.delbt.set_sensitive(False)
        self.rstbt.set_sensitive(False)
        self.savebt.set_sensitive(False)
        self.arearunbt.set_sensitive(False)
        # model: year, month name, month_ordinal, utc time hour, freq in Hz
        col_t = [gobject.TYPE_UINT, gobject.TYPE_STRING, gobject.TYPE_UINT, gobject.TYPE_UINT, gobject.TYPE_STRING]
        model = gtk.ListStore(*col_t)
        self.area_tv.set_model(model)
        self.area_tv.set_property("rules_hint", True)
        self.area_tv.set_property("enable_search", False)
        self.area_tv.set_headers_visible(True)
        self.area_tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        # col idx
        self.area_tv_idx_year = 0
        self.area_tv_idx_month_n = 1
        self.area_tv_idx_month_i = 2
        self.area_tv_idx_utc = 3
        self.area_tv_idx_freq = 4
        
        title = _("Year")
        cell = gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_year)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_year)
        self.area_tv.append_column(tvcol)

        title = _("Month")
        cell = gtk.CellRendererText()
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_month_n)
        tvcol.set_sort_column_id(self.area_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.area_tv.append_column(tvcol)

        title = _("Time (UTC)")
        cell = gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_utc)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_utc)
        self.area_tv.append_column(tvcol)

        title = _("Frequency (MHz)")
        cell = gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_freq)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_freq)
        self.area_tv.append_column(tvcol)

    def build_area_template_ts(self):
        # loads templates from a file and populates the combobox
        model = self.templatescb.get_model()
        if not model:
            col_t =  [gobject.TYPE_STRING, gobject.TYPE_PYOBJECT] # name, (year,month,utc,freq)
            model = gtk.ListStore(*col_t)
            self.templatescb.set_model(model)
            cell = gtk.CellRendererText()
            self.templatescb.pack_start(cell, True)
            self.templatescb.add_attribute(cell, 'text', 0)
        model.clear()

        # this hack for letting the templates subdir be parth of the path
        # so the templates/*.py can import between themselves
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(os.path.join(current_dir, 'templates'))
        ##


        # scan the dir for scripts
        import glob
        import imp
        tmplt_fs = []
        pattern = os.path.join(current_dir, 'templates', "*.py")

        for f in glob.glob(pattern):
          if os.path.isfile(f):
            tmplt_fs.append(f)

        for f in tmplt_fs:
            name, ext = os.path.splitext(f)
            mod = imp.load_source(name, f)
            try:
                t_o = mod.templates(self.main_window)
            except Exception, X:
                print _("Can't import template module %s: %s") % (f, X)
                continue

            # set module parameters
            ps = t_o.get_params()
            for p in ps: 
                try:
                    t_o.__dict__[p] = self.__dict__[p]
                except Exception, X:
                    print _("Fail to set property %s in template %s: %s") % (p, f, X)
            # make the module get ready for use later
            ret = t_o.load()
            if ret:
                print _("Can't load() template module %s") % f
                continue
                
            for tname in t_o.get_names():
                model.append([tname, t_o])

        if not len(model):
            # put an informative entry in the model
            model.append([_('There are no templates available'), None])
        else:
            model.prepend([_('Select a template to load'), None])
        self.templatescb.set_active(0)
        self.addtemplbt.set_sensitive(False)


    def area_templatescb_change(self, *args):
        active = self.templatescb.get_active()
        if not active:# 0 is the indicative default, not a real template
            self.addtemplbt.set_sensitive(False)
        else:
            self.addtemplbt.set_sensitive(True)

    def p2p_useday_tog(self, *args):
        change_to = None
        e = ee = ''
        #we only need to display a warning if the coeffs change.
        if self.p2pusedayck.get_active():
            e = _("URSI88 coefficients")
            ee = _("Specifying days forces the use of URSI88 coefficients. ")
            if len(self.p2pmy_tv.get_model()):
                ee += _("Values of 'day' in existing entries will be set to '1'.")
                change_to = 1
        else: 
            e = _("Not specifing days reverts the forced use of URSI88 coefficients. \
The current setting is %s.") % ('CCIR' if (self.model_combo.get_active()==0) else 'URSI88')
            if len(self.p2pmy_tv.get_model()):
                ee = _("All existing day values will be deleted.")
                change_to = 0
        dialog = gtk.MessageDialog(self.main_window, 
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, e)
        dialog.set_title(_('Warning'))
        dialog.format_secondary_text(ee)
        ret = dialog.run()
        dialog.destroy()
        if ret != -5:
            self.p2pusedayck.handler_block(self.p2puseday_handler_id)
            if self.p2pusedayck.get_active():
                self.p2pusedayck.set_active(False)
            else:
                self.p2pusedayck.set_active(True)
            self.p2pusedayck.handler_unblock(self.p2puseday_handler_id)
            return

        self.p2p_useday = self.p2pusedayck.get_active()
        if self.p2p_useday:
            self.model_combo.set_active(1)
            self.model_combo.set_sensitive(False)
        else:
            self.model_combo.set_sensitive(True)

        self.p2pdayspinbutton.set_sensitive(self.p2p_useday)
        model = self.p2pmy_tv.get_model()
        iter = model.get_iter_first()
        while iter:
            model.set_value(iter, self.p2pmy_tv_idx_day, change_to)
            iter = model.iter_next(iter)


    def p2p_calendar(self, *args):
        def calendar_retval(cal, dialog):
            dialog.response(gtk.RESPONSE_ACCEPT)
        dialog = gtk.Dialog(_("Select date"), self.main_window,
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.WIN_POS_CENTER_ON_PARENT,
                              (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                              gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        cal = gtk.Calendar()
        cal.connect('day-selected-double-click', calendar_retval, dialog)
        dialog.vbox.pack_start(cal)
        dialog.show_all()
        # set def date as the last date used, else let it default to today
        try:
            cal.select_month(self.p2pcal_last[1], self.p2pcal_last[0])
            cal.select_day(self.p2pcal_last[2])
        except:
            pass
        ret = dialog.run()
        dialog.destroy()
        if ret != -3: #ok
            return
        self.p2pcal_last = cal.get_date()
        self.p2pmy_add_tv_rows([(self.p2pcal_last[2], self.p2pcal_last[1]+1, self.p2pcal_last[0])])

    def p2pmy_add_tv_row_from_user(self, *args):
        day = self.p2pdayspinbutton.get_value_as_int()
        month_i = self.p2pmonthspinbutton.get_value_as_int()
        year = self.p2pyearspinbutton.get_value_as_int()
        self.p2pmy_add_tv_rows([(day, month_i, year)])

    def p2pfreq_add_tv_row_from_user(self, *args):
        freq = self.p2pfreqspinbutton.get_value()
        self.p2pfreq_add_tv_rows([(freq)])

    def p2pmy_add_tv_rows(self, rows):
        # rows: a list of (day, month_i, year) tuples
        tv_model = self.p2pmy_tv.get_model()
        had_rows = len(tv_model)
        for (day, month_i, year) in rows:
            day = day if self.p2p_useday else 0
            month_n = time.strftime('%B', time.strptime(str(month_i), '%m'))
            row = []
            row.insert(self.p2pmy_tv_idx_day, day)
            row.insert(self.p2pmy_tv_idx_month_n, month_n)
            row.insert(self.p2pmy_tv_idx_month_i, month_i)
            row.insert(self.p2pmy_tv_idx_year, year)
            iter = tv_model.append(row)
        self.p2pmydelbt.set_sensitive(True)
        self.p2pmyrstbt.set_sensitive(True)
        self.p2prunbt.set_sensitive(True)
#       if self.area_templates_file:
#           self.p2psavebt.set_sensitive(True)
#        self.verify_input_data(None)
        # def focus first row if the tv was previously empty
        if not had_rows:
            self.p2pmy_tv.set_cursor(0)

    def p2pfreq_add_tv_rows(self, rows):
        # rows: a list of (freq) tuples
        tv_model = self.p2pfreq_tv.get_model()
        had_rows = len(tv_model)
        for (freq) in rows:
            row = []
            row.insert(self.p2pfreq_tv_idx_freq, '%.3f' % freq)
            iter = tv_model.append(row)
        self.p2pfreqdelbt.set_sensitive(True)
        self.p2pfreqrstbt.set_sensitive(True)
#        if self.area_templates_file:
#            self.p2psavebt.set_sensitive(True)
#        self.verify_input_data(None)
        # def focus first row if the tv was previously empty
        if not had_rows:
            self.p2pfreq_tv.set_cursor(0)
        if len(tv_model) > 11 and not self.max_frequencies_warn:
            e = _("VOACAP can only process 11 frequencies")
            dialog = gtk.MessageDialog(self.main_window, 
                    gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, e)
            dialog.format_secondary_text(_('Only the first 11 entries will \
be processed, all other entries will be ignored.  Please delete some entries \
from the frequency table.'))
            dialog.run()
            dialog.destroy()
            self.max_frequencies_warn = True 

    def area_add_tv_row_from_user(self, *args):
        year = self.areayearspinbutton.get_value_as_int()
        month_i = self.monthspinbutton.get_value_as_int()
        utc = self.utcspinbutton.get_value_as_int()
        freq = self.freqspinbutton.get_value()
        self.area_add_tv_rows([(year, month_i, utc, freq)])

    def area_add_tv_rows(self, rows):#month_i, utc, freq, model=self.area_tv.get_model()):
        # rows: a list of (month_i, utc, freq) tuples
        tv_model = self.area_tv.get_model()
        had_rows = len(tv_model)
        for (year, month_i, utc, freq) in rows:
            month_n = time.strftime('%B', time.strptime(str(month_i), '%m'))
            row = []
            row.insert(self.area_tv_idx_year, year)
            row.insert(self.area_tv_idx_month_n, month_n)
            row.insert(self.area_tv_idx_month_i, month_i)
            row.insert(self.area_tv_idx_utc, utc)
            row.insert(self.area_tv_idx_freq, '%.3f' % freq)
            iter = tv_model.append(row)
        self.delbt.set_sensitive(True)
        self.rstbt.set_sensitive(True)
        if self.area_templates_file:
            self.savebt.set_sensitive(True)
        self.verify_input_data(None)
        # def focus first row if the tv was previously empty
        if not had_rows:
            self.area_tv.set_cursor(0)
        #let the user know we did not run all their data
        if len(tv_model) > self.max_vg_files and not self.max_vg_files_warn:
            e = _("VOACAP can only process %d area entries") % self.max_vg_files
            dialog = gtk.MessageDialog(self.main_window, 
                    gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, e)
            dialog.format_secondary_text(_('Only the first 12 entries will \
be processed, all other entries will be ignored.  Please delete some entries.'))
            dialog.run()
            dialog.destroy()
            self.max_vg_files_warn = True 

    def p2p_clean_my_tv(self, *args):
        self.p2pmy_tv.get_model().clear()
        self.p2pmydelbt.set_sensitive(False)
        self.p2pmyrstbt.set_sensitive(False)
        #?
        self.p2psavebt.set_sensitive(False)
        self.p2prunbt.set_sensitive(False)

    def p2p_clean_freq_tv(self, *args):
        self.p2pfreq_tv.get_model().clear()
        self.p2pfreqdelbt.set_sensitive(False)
        self.p2pfreqrstbt.set_sensitive(False)
        #?
        self.p2psavebt.set_sensitive(False)
#        self.p2prunbt.set_sensitive(False)

    def area_clean_tv(self, *args):
        self.area_tv.get_model().clear()
        self.delbt.set_sensitive(False)
        self.rstbt.set_sensitive(False)
        self.savebt.set_sensitive(False)
        self.arearunbt.set_sensitive(False)

    def p2p_del_my_tv_row(self, *args):
        selection = self.p2pmy_tv.get_selection()
        if not selection.count_selected_rows(): return 
        model, paths = selection.get_selected_rows()
        self.p2pmy_tv.freeze_child_notify()
        self.p2pmy_tv.set_model(None)
        iters = []
        for path in paths: 
            iters.append(model.get_iter(path))        
        for iter in iters: 
            model.remove(iter)
        if not len(model):
            self.p2pmydelbt.set_sensitive(False)
            self.p2pmyrstbt.set_sensitive(False)
            #?
            self.savebt.set_sensitive(False)
            self.p2prunbt.set_sensitive(False)
        self.p2pmy_tv.set_model(model)
        self.p2pmy_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.p2pmy_tv.set_cursor((last_path,))
                return

    def p2p_del_freq_tv_row(self, *args):
        selection = self.p2pfreq_tv.get_selection()
        if not selection.count_selected_rows(): return 
        model, paths = selection.get_selected_rows()
        self.p2pfreq_tv.freeze_child_notify()
        self.p2pfreq_tv.set_model(None)
        iters = []
        for path in paths: 
            iters.append(model.get_iter(path))        
        for iter in iters: 
            model.remove(iter)
        if not len(model):
            self.p2pfreqdelbt.set_sensitive(False)
            self.p2pfreqrstbt.set_sensitive(False)
            #?
 #          self.savebt.set_sensitive(False)
 #          self.p2prunbt.set_sensitive(False)
        self.p2pfreq_tv.set_model(model)
        self.p2pfreq_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.p2pfreq_tv.set_cursor((last_path,))
                return


    def area_del_tv_row(self, *args):
        selection = self.area_tv.get_selection()
        if not selection.count_selected_rows(): return 
        model, paths = selection.get_selected_rows()
        self.area_tv.freeze_child_notify()
        self.area_tv.set_model(None)
        iters = []
        for path in paths: 
            iters.append(model.get_iter(path))        
        for iter in iters: 
            model.remove(iter)
        if not len(model):
            self.delbt.set_sensitive(False)
            self.rstbt.set_sensitive(False)
            self.savebt.set_sensitive(False)
            self.arearunbt.set_sensitive(False)
        self.area_tv.set_model(model)
        self.area_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.area_tv.set_cursor((last_path,))
                return
	
	
    def p2p_save_as_template(self, *args):
        pass


    def area_save_as_template(self, *args):
        ''' saves area_tv model content as a template '''
        global ok_bt
        global nentry

        def text_change(self, *args):
            global ok_bt
            global nentry
            if len(nentry.get_text()):
                ok_bt.set_sensitive(True)
            else:
                ok_bt.set_sensitive(False)

        dialog = gtk.Dialog(_("Creating new area template"),
                   self.main_window,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        hb = gtk.HBox(2)
        label = gtk.Label(_("Template name"))
        hb.pack_start(label)
        nentry = gtk.Entry(max=50)
        nentry.connect("changed", text_change)
        hb.pack_start(nentry)
        hb.show_all()
        dialog.vbox.pack_start(hb)
       
        ok_bt = gtk.Button(None, gtk.STOCK_OK)
        ok_bt.set_sensitive(False)
        ok_bt.show()
        dialog.add_action_widget(ok_bt, gtk.RESPONSE_ACCEPT)

        response = dialog.run()
        if response == -3: # accept
            # save it
            fd = open(os.path.expandvars(self.area_templates_file), 'a')
            fd.write(_('\n#template created by voacap GUI'))
            title = nentry.get_text()
            fd.write('\n[%s]' % title)
            fd.write(_('\n#month utchour  freq'))
            model = self.area_tv.get_model()
            iter = model.get_iter_first()
            while iter:
                m,u,f = model.get(iter,1,2,3)
                fd.write('\n%02d      %02d      %.3f' % (m,u,float(f)))
                iter = model.iter_next(iter)
            fd.write(_('\n#End of %s') % title)
            fd.close() 
            # reload templates_file to repopulate templatescb, then
            # select this recently saved as the active one
            self.build_area_template_ts()
            model = self.templatescb.get_model()
            iter = model.get_iter_first()
            while iter:
                if model.get_value(iter, 0) == title:
                    self.templatescb.set_active_iter(iter)
                    break
                iter = model.iter_next(iter)
        dialog.destroy()


    def area_add_template(self, *args):
        active = self.templatescb.get_active()
        if not active:# 0 is the indicative default, not a real template
            return
        model = self.templatescb.get_model()
        t_n = model.get_value(model.get_iter(active), 0)
        t_o = model.get_value(model.get_iter(active), 1)
        model = self.area_tv.get_model()
        if t_o.set_ini(model):
            print "Can't initialize module %s" % t_n
            return 
        if t_o.run(): return
        try:
            templ_tups = t_o.ret_templates[t_n]
        except: pass
        if templ_tups:
            self.area_add_tv_rows(templ_tups)




#####################SSN Tab functions follow
    def ssn_build_tv(self):
        self.ssn_tv.set_model(self.ssn_repo)
        
        self.ssn_file_data_label.set_text(self.ssn_repo.get_file_data())

        self.ssn_tv.set_property("rules_hint", True)
        self.ssn_tv.set_property("enable_search", False)
        self.ssn_tv.set_headers_visible(True)

        # col idx
        self.ssn_tv_idx_year = 0
        
        title = _("Year")
        cell = gtk.CellRendererText()
        font = pango.FontDescription('bold')
        cell.set_property('font-desc', font)
        tvcol = gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text', self.ssn_tv_idx_year)
        tvcol.set_sort_column_id(self.area_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        tvcol.set_expand(True)
        self.ssn_tv.append_column(tvcol)
        
        for i in range (1,13):
            cell = gtk.CellRendererText()
            cell.set_property('xalign', 0.5)
            tvcol = gtk.TreeViewColumn(calendar.month_abbr[i], cell)
            tvcol.set_alignment(0.5)
            tvcol.add_attribute(cell, 'text', i)
            tvcol.add_attribute(cell, 'font', i+13)
            tvcol.set_resizable(True)
            tvcol.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            tvcol.set_expand(True)
            self.ssn_tv.append_column(tvcol)
            
        ssn_thumb = VOASSNThumb(self.ssn_repo)
        _th = ssn_thumb.get_thumb()
        _th.show()
        self.ssn_plot_box.pack_start(_th, True, True)
        
        # scroll to the current year
        iter = self.ssn_repo.get_iter_first()
        while iter:
            if self.ssn_repo.get_value(iter, self.ssn_tv_idx_year) == str(datetime.today().year):
                path = self.ssn_repo.get_path(iter)
                self.ssn_tv.set_cursor(path)
                self.ssn_tv.scroll_to_cell(path, None)
                break
            iter = self.ssn_repo.iter_next(iter)
            

    def nb_switch_page(self, *args):
        # area is the last page in the nb
        if self.notebook.get_n_pages() == args[2] +1:
            if not self.area_accelgrp:
                self.area_accelgrp = gtk.AccelGroup()
                self.area_accelgrp.connect_group(0xffff, 0, 0, self.area_del_tv_row)
            self.main_window.add_accel_group(self.area_accelgrp)
        else:
            if self.area_accelgrp:
                self.main_window.remove_accel_group(self.area_accelgrp)
                self.area_accelgrp = None


    def show_area_chooser(self, widget):    
        dialog = VOAAreaChooser(self.area_rect, self.area_chooser_map_size, parent=self.main_window)
        return_code, return_rect, return_size = dialog.run()
        if (return_code == 0): # 0=ok, 1=cancel
            self.area_rect = return_rect
            self.area_chooser_map_size = return_size
            self.area_label.set_text(self.area_rect.get_formatted_string())


    def run_prediction(self, button):
        voacapl_args = ''


        if button == self.arearunbt:
            voacapl_args = self.itshfbc_path
            ###################################################################
            vf = VOAFile(os.path.join(os.path.expanduser("~"),'itshfbc','areadata','pyArea.voa'))
            vf.set_gridsize(self.gridsizespinbutton.get_value())
            vf.set_location(vf.TX_SITE,
                            self.tx_site_entry.get_text(),
                            self.tx_lon_spinbutton.get_value(),
                            self.tx_lat_spinbutton.get_value()) 
            vf.P_CENTRE = vf.TX_SITE

            vf.set_xnoise(abs(self.mm_noise_spinbutton.get_value()))
            vf.set_amind(self.min_toa_spinbutton.get_value())
            vf.set_xlufp(self.reliability_spinbutton.get_value())
            vf.set_rsn(self.snr_spinbutton.get_value())
            vf.set_pmp(self.mpath_spinbutton.get_value())
            vf.set_dmpx(self.delay_spinbutton.get_value())

            vf.set_psc1(self.foe_spinbutton.get_value())
            vf.set_psc2(self.fof1_spinbutton.get_value())
            vf.set_psc3(self.fof2_spinbutton.get_value())
            vf.set_psc4(self.foes_spinbutton.get_value())

            vf.set_area(self.area_rect)

            # Antennas, gain, tx power, bearing
            #def set_rx_antenna(self, data_file, gain=0.0, bearing=0.0):
            #rel_dir, file, description = self.ant_list[self.rx_ant_combobox.get_active()]
            vf.set_rx_antenna(self.rx_antenna_path.ljust(21), 0.0, 
                self.rx_bearing_spinbutton.get_value())

            #def set_tx_antenna(self, data_file, design_freq=0.0, bearing=0.0, power=0.125):
            #rel_dir, file, description = self.ant_list[self.tx_ant_combobox.get_active()]
            vf.set_tx_antenna(self.tx_antenna_path.ljust(21), 0.0, 
                self.tx_bearing_spinbutton.get_value(), 
                self.tx_power_spinbutton.get_value()/1000.0)

            vf.clear_plot_data()
            # treeview params            
            model = self.area_tv.get_model()
            iter = model.get_iter_first()
            # we're limited to 12 entries here
            i = 0
            while iter and i < self.max_vg_files:
                year = int(model.get_value(iter, self.area_tv_idx_year))
                month_i = float(model.get_value(iter, self.area_tv_idx_month_i))
                utc = model.get_value(iter, self.area_tv_idx_utc)
                freq = model.get_value(iter, self.area_tv_idx_freq)
                # ssn entries are named as months (jan_ssn_entry) so to be sure 
                # we're getting the correct one, we need to map them
                ssn = self.ssn_repo.get_ssn(month_i, year)
                vf.add_plot((freq, utc, month_i, ssn))
                iter = model.iter_next(iter)
                i = i+1
            vf.write_file()
            #let the user know we did not run all their data
            if iter:
                e = _("VOACAP can only process %d area entries") % self.max_vg_files
                dialog = gtk.MessageDialog(self.main_window, 
                    gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, e)
                dialog.format_secondary_text(_('Only the first 12 entries will be processed,\
all other entries will be ignored.'))
                dialog.run()
                dialog.destroy()
 
            print "executing vocapl..."
#            os.system('voacapl ~/itshfbc area calc pyArea.voa')
#            print  os.path.join(os.path.expanduser("~"), 'itshfbc')
            ret = os.spawnlp(os.P_WAIT, 'voacapl', 'voacapl', os.path.join(os.path.expanduser("~"), 'itshfbc'), "area", "calc",  "pyArea.voa")

            if ret: 
                e = "voacapl returned %s. Can't continue." % ret
                dialog = gtk.MessageDialog(self.main_window, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, e )
                dialog.run()
                dialog.destroy()
                return -1
            print "done voacapl"

            s = os.path.join(os.path.expanduser("~"), 'itshfbc','areadata','pyArea.voa')
            graph = VOAAreaPlotGUI(s, parent=self.main_window, exit_on_close=False)
            graph.quit_application()

        #P2P Predictions follow
        if button == self.p2prunbt:
            runs = []
            iter = self.p2pcircuitcb.get_active_iter()
            c_method = self.p2pcircuitcb.get_model().get_value(iter, 0)
            if c_method:
                runs.append('c')
            iter = self.p2pgraphcb.get_active_iter()
            g_method = self.p2pgraphcb.get_model().get_value(iter, 0)
            if g_method:
                runs.append('g')

            _coeff = 'CCIR' if (self.model_combo.get_active()==0) else 'URSI88'
            _path = VOADatFile.SHORT_PATH if (self.path_combo.get_active()==0) else VOADatFile.LONG_PATH

            for rt in runs:
                input_filename = 'voacapg.dat' if rt == 'g' else  'voacapx.dat'
                output_filename = 'voacapg.out' if rt == 'g' else 'voacapx.out'
                data_file_format = VOADatFile.GRAPHICAL_FORMAT if rt == 'g' else VOADatFile.CIRCUIT_FORMAT
                df = VOADatFile(self.itshfbc_path + os.sep + 'run'  + os.sep + input_filename)
                voacapl_args = self.itshfbc_path + ' ' + input_filename + ' ' + output_filename
                df.set_title([_('File generated by voacap-gui (www.qsl.net/hz1jw)'), _('File created: ')+datetime.now().strftime('%X %a %d %b %y')])
                df.set_linemax(55)
                method = g_method if rt == 'g' else c_method
                df.set_method(method)
                df.set_coeffs(_coeff)
                df.set_sites(HamLocation(self.tx_lat_spinbutton.get_value(), 
                                        self.tx_lon_spinbutton.get_value(),
                                        self.tx_site_entry.get_text()), 
                            HamLocation(self.rx_lat_spinbutton.get_value(), 
                                        self.rx_lon_spinbutton.get_value(),
                                        self.rx_site_entry.get_text()), _path)
                df.set_system(self.tx_power_spinbutton.get_value()/1000.0,\
                                abs(self.mm_noise_spinbutton.get_value()),\
                                self.min_toa_spinbutton.get_value(),\
                                self.reliability_spinbutton.get_value(),\
                                self.snr_spinbutton.get_value(),\
                                self.mpath_spinbutton.get_value(),\
                                self.delay_spinbutton.get_value())
                if rt == 'c':
                    # The frequencies are only applicable when performing text based predictions.
                    # voacap can accep up to 11 entries in the list.
                    # entries may be specified up to 3 decimal places.
                    # longer lists, additional prescision will be truncated
                    # by the set_frequency_list method.
                    # (The example freqs below are PSK31 calling freqs...)
                    #   df.set_frequency_list((3.580, 7.035, 10.140, 14.070, 18.1, 21.08, 28.12))
                    freqs = []
                    model = self.p2pfreq_tv.get_model()
                    iter = model.get_iter_first()
                    while iter:
                        try:
                            freqs.append(float(model.get_value(iter, self.p2pfreq_tv_idx_freq)))
                        except:
                            pass                        
                        iter = model.iter_next(iter)
                    df.set_frequency_list(tuple(freqs))

                df.set_antenna(VOADatFile.TX_ANTENNA, self.tx_antenna_path.ljust(21),
                    self.tx_bearing_spinbutton.get_value(), 
                    self.tx_power_spinbutton.get_value()/1000.0)
                df.set_antenna(VOADatFile.RX_ANTENNA, self.rx_antenna_path.ljust(21), 
                    self.rx_bearing_spinbutton.get_value()) 
                df.set_fprob(self.foe_spinbutton.get_value(), 
                    self.fof1_spinbutton.get_value(), self.fof2_spinbutton.get_value(),
                    self.foes_spinbutton.get_value())
                # ssn_list is a list of tuples (day, month, year, ssn)            
                ssn_list = []
                model = self.p2pmy_tv.get_model()
                iter = model.get_iter_first()
                day = 0
                while iter:
                    if rt == 'c':
                        day = model.get_value(iter, self.p2pmy_tv_idx_day)
                        if day:
                            df.set_coeffs('URSI88')
                    month = model.get_value(iter, self.p2pmy_tv_idx_month_i)
                    year = model.get_value(iter, self.p2pmy_tv_idx_year)
                    ssn = self.ssn_repo.get_ssn(month, year)
                    if not ssn:
                        e = _("Can't find SSN number for <%(m)s>-<%(y)s>. Can't continue without all SSNs.") % {'m':month, 'y':year}
                        dialog = gtk.MessageDialog(self.main_window, 
                            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                            gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, e )
                        dialog.run()
                        dialog.destroy()
                        return -1
                    ssn_list.append((day, month, year, ssn))
                    iter = model.iter_next(iter)
                df.set_ssn(ssn_list)
                df.write_file(data_file_format)

                try:
                    retcode = subprocess.call("voacapl -s " + voacapl_args, shell=True)
                    if rt == 'c':
                        result_dialog = VOATextFileViewDialog(self.itshfbc_path+os.sep+'run'+os.sep+output_filename)
                        return_code = result_dialog.run()
                    if rt == 'g':
                        graph = VOAP2PPlotGUI(self.itshfbc_path+os.sep+'run'+os.sep+output_filename,
                            parent=self.main_window, exit_on_close=False)
                        graph.quit_application()
                except OSError, e:
                        print "Voacapl execution failed:", e
                        break


    def show_about_dialog(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("voacap-gui")
        about.set_version("0.10")
        about.set_authors(("J.Watson (HZ1JW/M0DNS)", "Fernando M. Maresca (LU2DFM)"))
        about.set_comments(_("A voacap GUI"))
        about.set_website("http://www.qsl.net/hz1jw")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voacap.png")))
        about.run()
        about.destroy()
        
    def build_new_template_file(self):
        fn = os.path.join(self.prefs_dir,'area_templ.ex')
        s = _('''# rough format for area plot templates:
# lines starting with # are ignored
# each line consist in three values separated by spaces
# each template is preceded by a name enclosed in square brackets:
# [template name]
# tags
# month utchour freq
# 11    22      14.250
# month: number month, 1=January
# utchour: UTC time HOUR, 00 to 23
# freq: frequecy in MHz
# example: all months at midnight on 14.100 MHz
[All months midnight 14.100 Mhz]
#year month utchour freq
2010      01      00      14.10
2010      02      00      14.10
2010      03      00      14.10
2010      04      00      14.10
2010      05      00      14.10
2010      06      00      14.10
2010      07      00      14.10
2010      08      00      14.10
2010      09      00      14.10
2010      10      00      14.10
2010      11      00      14.10
2010      12      00      14.10

[All months at 1600z 7.500 MHz]
#month utchour freq
2010      01      16      7.5
2010      02      16      7.5
2010      03      16      7.5
2010      04      16      7.5
2010      05      16      7.5
2010      06      16      7.5
2010      07      16      7.5
2010      08      16      7.5
2010      09      16      7.5
2010      10      16      7.5
2010      11      16      7.5
2010      12      16      7.5
\n
''')
        with open(fn, 'w') as templates_def_fd:
            templates_def_fd.write(s)
        self.area_templates_file = fn


    def quit_application(self, widget):
        self.save_user_prefs()
        gtk.main_quit 
        sys.exit(0)
            
if __name__ == "__main__":
    app = VOACAP_GUI()
    try:
        gtk.main()
    except KeyboardInterrupt:
        sys.exit(1)
