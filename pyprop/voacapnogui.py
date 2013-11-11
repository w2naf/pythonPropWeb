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

import gettext
import locale
GETTEXT_DOMAIN = 'voacapgui'
LOCALE_PATH = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), 'po')


gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)

from voaTextFileViewDialog import *
from voaDatFile import *
from voaDefaults import *
from voaSiteChooser import *
#from voaP2PPlot import *
#from voaP2PPlotgui import *
#from voaAreaPlotgui import *
from ssnFetch import *
#from voaSSNThumb import *
from voaFile import *
#from voaAreaChooser import *
#from voaAntennaChooser import *


class paramsObj: pass

class VOACAP_GUI:
    params = paramsObj()

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

    def __init__(self,path=None):
        if path == None:
          self.itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc'
          self.prefs_dir    = os.path.expanduser("~")+os.sep+'.voacapgui'+os.sep
        else:
          self.itshfbc_path  = os.path.join(path,'itshfbc')
          self.prefs_dir     = os.path.join(path,'voacap_prefs'+os.sep)

        self.prefs_path    = self.prefs_dir + 'voacapgui.prefs'
        self.ssn_path      = self.prefs_dir + 'sunspot.predict'

        # Check if the prefs directory exists, create one if if it doesn't
        # (This is probably not required as the installer will probbaly end up
        # creating and populating this directory.

        if not os.path.isdir(self.prefs_dir):
          os.makedirs(self.prefs_dir) 

        #ant_list = []

        self.params = paramsObj()

        self.firstCornerX = 0
        self.firstCornerY = 0

        self.area_rect = VOAAreaRect()

        self.model_list = ('CCIR', 'URSI88')
        self.path_list = (_('Short'), _('Long'))

        # These need to be lists later on to support multiple antennas    
        self.tx_antenna_path = ''
        self.rx_antenna_path = ''

        self.main_window_size = (560, 410)
        self.site_chooser_map_size = area_chooser_map_size = (384,192)
        self.antenna_chooser_size = (500,400)

        self.area_templates_file = None
        
       
        self.max_vg_files_warn = False
        self.max_frequencies_warn = False
        self.max_vg_files = 25 #This was originally set to 12 in earlier versions of voacapl.

#        self.gridsizespinbutton.set_value(125)
#        self.areayearspinbutton.set_value(today.year)
#        self.monthspinbutton.set_value(today.month)
#        self.freqspinbutton.set_value(14.1)
        
        self.ssn_repo = SSNFetch(save_location = self.ssn_path)
        try:
            self.ssn_repo.update_ssn_file() #Force an update
        except:
            pass

        _min, _max = self.ssn_repo.get_data_range()
        self.read_user_prefs()
                    
    def read_user_prefs(self) :
        config = ConfigParser(VOADefaultDictionary())
        config.read(self.prefs_path)
        #set some defaults here for the system variables
        try:
            self.params.foe    = (float(config.get('DEFAULT','foe')))
            self.params.fof1   = (float(config.get('DEFAULT','fof1')))                        
            self.params.fof2   = (float(config.get('DEFAULT','fof2')))                        
            self.params.foes   = (float(config.get('DEFAULT','foes')))
            self.params.model  = (int(config.get('DEFAULT', 'model')))
            self.params.path   = (int(config.get('DEFAULT', 'path')))            
    
            self.params.mm_noise = (float(config.get('DEFAULT','mm_noise')))
            self.params.min_toa  = (float(config.get('DEFAULT','min_toa')))
            self.params.reliability  = (float(config.get('DEFAULT','required_reliability')))
            self.params.snr      = (float(config.get('DEFAULT','required_snr')))
            self.params.mpath    = (float(config.get('DEFAULT','mpath')))
            self.params.delay    = (float(config.get('DEFAULT','delay')))    
            
            self.params.tx_bearing = (float(config.get('DEFAULT', 'tx_bearing')))
            self.params.tx_power   = (float(config.get('DEFAULT', 'tx_power')))
            self.params.rx_bearing = (float(config.get('DEFAULT', 'rx_bearing')))
                            
            self.params.tx_site    = (config.get('tx site','name'))
            self.params.tx_lat     = (float(config.get('tx site','lat')))
            self.params.tx_lon     = (float(config.get('tx site','lon')))
            self.params.tx_antenna = (config.get('tx site', 'antenna' )) 
            self.params.tx_antenna_path, sep, suffix = (config.get('tx site', 'antenna' )).partition(' :')
            self.params.tx_bearing = (float(config.get('tx site', 'bearing')))
            self.params.tx_power   = (float(config.get('tx site', 'power')))
            self.params.rx_site    = (config.get('rx site','name'))
            self.params.rx_lat     = (float(config.get('rx site','lat')))
            self.params.rx_lon     = (float(config.get('rx site','lon')))
            self.params.rx_antenna = (config.get('rx site', 'antenna' ))
            self.params.rx_antenna_path, sep, suffix = (config.get('rx site', 'antenna' )).partition(' :')
            self.params.rx_bearing = (float(config.get('rx site', 'bearing')))    

            self.params.site_chooser_map_size = (config.getint('site chooser','map_width'), 
                                          config.getint('site chooser','map_height'))
            self.params.area_chooser_map_size = (config.getint('area chooser','map_width'), 
                                          config.getint('area chooser','map_height'))
            self.params.antenna_chooser_size = (config.getint('antenna chooser','width'), 
                                          config.getint('antenna chooser','height'))
            self.params.gridsizes  = (config.getint('area', 'gridsize'))
            self.params.areayear   = (config.getint('area','year'))
            self.params.month      = (config.getint('area','month'))
            self.params.utc        = (config.getint('area','utc'))
            self.params.freq       = (config.getfloat('area', 'frequency'))
            self.params.area_templates_file = config.get('area', 'templates_file')
            self.params.area_rect=VOAAreaRect(config.getfloat('area','sw_lat'), 
                                        config.getfloat('area','sw_lon'),
                                        config.getfloat('area','ne_lat'),
                                        config.getfloat('area','ne_lon'))
            self.params.area_label = (self.params.area_rect.get_formatted_string())
        except Exception, X:
            print 'Error reading the user prefs: %s - %s' % (Exception, X)
            
    def update_parameters(self,params):
#      '''Function to update model parameters using the params dictionary from the web page.'''
      self.params.shortName = params['shortName']
      self.params.foe    = float(params['foe'])
      self.params.fof1   = float(params['fof1'])
      self.params.fof2   = float(params['fof2'])
      self.params.foes   = float(params['foes'])
      self.params.model  = int(float(params['model']))
      self.params.path   = int(float(params['path']))

      self.params.mm_noise     = float(params['mm_noise'])
      self.params.min_toa      = float(params['min_toa'])
      self.params.reliability  = float(params['required_reliability'])
      self.params.snr          = float(params['required_snr'])
      self.params.mpath        = float(params['mpath'])
      self.params.delay        = float(params['delay'])
      
      self.params.tx_site      = params['tx_name']
      self.params.tx_lat       = float(params['tx_lat'])
      self.params.tx_lon       = float(params['tx_lon'])
      self.params.tx_antenna   = params['tx_antenna']
  #    self.params.tx_antenna_path, sep, suffix = 
      self.params.tx_bearing   = float(params['tx_bearing'])
      self.params.tx_power     = float(params['tx_power'])
  #    self.params.rx_site      = 
  #    self.params.rx_lat       = 
  #    self.params.rx_lon       = 
  #    self.params.rx_antenna   = 
  #    self.params.rx_antenna_path, sep, suffix =
  #    self.params.rx_bearing   = 

  #    self.params.site_chooser_map_size = (config.getint('site chooser','map_width'), 
  #                                  confiself.getint('site chooser','map_height'))
  #    self.params.area_chooser_map_size = (config.getint('area chooser','map_width'), 
  #                                  confiself.getint('area chooser','map_height'))
  #    self.params.antenna_chooser_size = (config.getint('antenna chooser','width'), 
  #                                  confiself.getint('antenna chooser','height'))
      self.params.gridsizes  = int(float(params['gridsize']))
      self.params.year       = int(float(params['year']))
      self.params.areayear   = int(float(params['year']))
      self.params.month      = int(float(params['month']))
      self.params.utc        = int(float(params['utc']))
      self.params.freq       = float(params['frequency'])
      self.params.area_templates_file = params['templates_file']
      self.params.area_rect=VOAAreaRect(float(params['sw_lat']),
                                     float(params['sw_lon']),
                                     float(params['ne_lat']),
                                     float(params['ne_lon']))
  #    self.params.area_label = (self.params.area_rect.get_formatted_string())

#    def save_user_prefs(self):
#
#        config = ConfigParser()
#        # voaSiteChooser map size
#        config.add_section('site chooser')
#        config.set('site chooser', 'map_width', self.site_chooser_map_size[0])
#        config.set('site chooser', 'map_height', self.site_chooser_map_size[1])
#        # voaAreaChooser map size
#        config.add_section('area chooser')
#        config.set('area chooser', 'map_width', self.area_chooser_map_size[0])
#        config.set('area chooser', 'map_height', self.area_chooser_map_size[1])
#        # voaAreaChooser map size
#        if self.antenna_chooser_size:
#            config.add_section('antenna chooser')
#            config.set('antenna chooser', 'width', self.antenna_chooser_size[0])
#            config.set('antenna chooser', 'height', self.antenna_chooser_size[1])
#        # Tx Site Parameters
#        config.add_section('tx site')
#        config.set('tx site', 'name', self.tx_site_entry.get_text())
#        config.set('tx site', 'lat', self.tx_lat_spinbutton.get_value())
#        config.set('tx site', 'lon', self.tx_lon_spinbutton.get_value())
#        config.set('tx site', 'antenna', self.tx_antenna_entry.get_text())    
#        config.set('tx site', 'bearing', self.tx_bearing_spinbutton.get_value())
#        config.set('tx site', 'power', self.tx_power_spinbutton.get_value())
#        # Rx Site Parameters
#        config.add_section('rx site')
#        config.set('rx site', 'name', self.rx_site_entry.get_text())
#        config.set('rx site', 'lat', self.rx_lat_spinbutton.get_value())
#        config.set('rx site', 'lon', self.rx_lon_spinbutton.get_value())
#        config.set('rx site', 'antenna', self.rx_antenna_entry.get_text())    
#        config.set('rx site', 'bearing', self.rx_bearing_spinbutton.get_value())   
#        # Ionospheric Parameters
#        config.set('DEFAULT', 'foe', self.foe_spinbutton.get_value())   
#        config.set('DEFAULT', 'fof1', self.fof1_spinbutton.get_value())
#        config.set('DEFAULT', 'fof2', self.fof2_spinbutton.get_value())    
#        config.set('DEFAULT', 'foes', self.foes_spinbutton.get_value())    
#        config.set('DEFAULT', 'model', self.model_combo.get_active())
#        config.set('DEFAULT', 'path', self.path_combo.get_active())                
#        # System parameters
#        config.set('DEFAULT','mm_noise', self.mm_noise_spinbutton.get_value())    
#        config.set('DEFAULT','min_toa', self.min_toa_spinbutton.get_value())
#        config.set('DEFAULT','required_reliability', self.reliability_spinbutton.get_value())
#        config.set('DEFAULT','required_snr', self.snr_spinbutton.get_value())                                    
#        config.set('DEFAULT','mpath', self.mpath_spinbutton.get_value())    
#        config.set('DEFAULT','delay', self.delay_spinbutton.get_value())
#        # area parameters
#        config.add_section('area')
#        config.set('area','gridsize', self.gridsizespinbutton.get_value_as_int())
#        config.set('area','year', self.areayearspinbutton.get_value_as_int())
#        config.set('area','month', self.monthspinbutton.get_value_as_int())
#        config.set('area','utc', self.utcspinbutton.get_value_as_int())
#        config.set('area','frequency', self.freqspinbutton.get_value())
#        config.set('area','sw_lat', self.area_rect.sw_lat)
#        config.set('area','sw_lon', self.area_rect.sw_lon)
#        config.set('area','ne_lat', self.area_rect.ne_lat)
#        config.set('area','ne_lon', self.area_rect.ne_lon)
#        config.set('area','templates_file', self.area_templates_file if self.area_templates_file else '')
#        
#        with open(self.prefs_path, 'w') as configfile:
#            config.write(configfile)

    # This function is called everytime a run submenu is activated
    # It enables/disables further submenus until input data is valid
    # todo use the status bar to indicate the reason for any failure            
#gettext here
#This function is used to force an update

    def update_ssn_table(self, widget):     
        self.ssn_repo.update_ssn_file() #Force an update
        self.ssn_file_data_label.set_text(self.ssn_repo.get_file_data())
        #self.write_ssns(self.ssn_repo.get_ssn_list())
       
        
#        [ model.append( [i, label]) for i, label in [
#                 (0, _("Select method to run")),
#                (30, _("Method 30 (Smoothed LP/SP Model)")),
#                (25, _("Method 25 (All Modes SP Model)")),
#                (22, _("Method 22 (Forced SP Model)")),
#                (21, _("Method 21 (Forced LP Model)")),
#                (20, _("Method 20 (Complete System Performance)")),
#                (15, _("Method 15 (Tx. &amp; Rx. Antenna Pattern)")),
#                (14, _("Method 14 (Rx. Antenna Pattern)")),
#                (13, _("Method 13 (Tx. Antenna Pattern)")),
#                 (9, _("Method 9 (HPF-MUF-FOT Text Graph)"))
#                 ]]

#####################SSN Tab functions follow
#        ssn_thumb = VOASSNThumb(self.ssn_repo)
    def run_prediction(self, type='area'):
        voacapl_args = ''
#        if button == self.arearunbt:
        if type=='area':
            voacapl_args = self.itshfbc_path
            ###################################################################
            fName = self.params.shortName+"-pyArea.voa"
#            vf = VOAFile(os.path.join(os.path.expanduser("~"),'itshfbc','areadata','pyArea.voa'))
#            vf = VOAFile(os.path.join(os.path.expanduser("~"),'itshfbc','areadata',fName))
            vf = VOAFile(os.path.join(self.itshfbc_path,'areadata',fName))
#            vf.set_gridsize(self.gridsizespinbutton.get_value())
            vf.set_gridsize(self.params.gridsizes)
            vf.set_location(vf.TX_SITE,
                            self.params.tx_site,
                            self.params.tx_lon,
                            self.params.tx_lat) 
            vf.P_CENTRE = vf.TX_SITE

            vf.set_xnoise(abs(self.params.mm_noise))
            vf.set_amind(self.params.min_toa)
            vf.set_xlufp(self.params.reliability)
            vf.set_rsn(self.params.snr)
            vf.set_pmp(self.params.mpath)
            vf.set_dmpx(self.params.delay)

            vf.set_psc1(self.params.foe)
            vf.set_psc2(self.params.fof1)
            vf.set_psc3(self.params.fof2)
            vf.set_psc4(self.params.foes)

            vf.set_area(self.params.area_rect)

            # Antennas, gain, tx power, bearing
            #def set_rx_antenna(self, data_file, gain=0.0, bearing=0.0):
            #rel_dir, file, description = self.ant_list[self.rx_ant_combobox.get_active()]
            vf.set_rx_antenna(self.params.rx_antenna_path.ljust(21), 0.0, 
                self.params.rx_bearing)

            #def set_tx_antenna(self, data_file, design_freq=0.0, bearing=0.0, power=0.125):
            #rel_dir, file, description = self.ant_list[self.tx_ant_combobox.get_active()]
            vf.set_tx_antenna(self.params.tx_antenna_path.ljust(21), 0.0, 
                self.params.tx_bearing, 
                self.params.tx_power/1000.0)

            vf.clear_plot_data()
            # treeview params            
            model = self.params.model


            year    = self.params.year
            month_i = self.params.month
            utc     = self.params.utc
            freq    = self.params.freq
            # ssn entries are named as months (jan_ssn_entry) so to be sure 
            # we're getting the correct one, we need to map them
            ssn = self.ssn_repo.get_ssn(month_i, year)
            vf.add_plot((freq, utc, month_i, ssn))
            vf.write_file()
            #let the user know we did not run all their data
 
            print "executing vocapl..."
#            os.system('voacapl ~/itshfbc area calc pyArea.voa')
#            print  os.path.join(os.path.expanduser("~"), 'itshfbc')
#            ret = os.spawnlp(os.P_WAIT, 'voacapl', 'voacapl', os.path.join(os.path.expanduser("~"), 'itshfbc'), "area", "calc",  "pyArea.voa")
#            ret = os.spawnlp(os.P_WAIT, 'voacapl', 'voacapl', self.itshfbc_path, "area", "calc",  fName)
            cmd = 'voacapl '+self.itshfbc_path+' area calc '+fName
            ret = subprocess.check_call(cmd.split())
#            subprocess.check_call(cmd.split(), stdout=fLog, stderr=fLog)
#            with open('/var/www/k2bsa/error.txt','w') as error_obj:
#                error_obj.write('Ret: '+str(ret)+'\n')
#                error_obj.write('Cmd: '+cmd+'\n')
#                error_obj.write(self.itshfbc_path+'\n')
#                error_obj.write(fName+'\n')
#                error_obj.write('\n'.join(sys.path))
#            ret = os.spawnlp(os.P_WAIT, 'voacapl', 'voacapl','itshfbc', "area", "calc",  fName)

#            if ret: 
#                e = "voacapl returned %s. Can't continue." % ret
#                return -1
            print "done voacapl"

#            s = os.path.join(os.path.expanduser("~"), 'itshfbc','areadata','pyArea.voa')
            s = os.path.join(os.path.expanduser("~"), 'itshfbc','areadata',fName)
#            s = os.path.join('itshfbc','areadata',fName)

        #P2P Predictions follow
        if type=='p2p':
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
