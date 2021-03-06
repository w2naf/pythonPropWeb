#! /usr/bin/env python
#
# File: voaDatFile.py
# Version: 300409
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
# A class to encapsulate the data file used for voacap point-to-point
# prediction
# A typical file is shown below;
#

# COMMENT    This file is a sample input file
# LINEMAX      55       number of lines-per-page
# COEFFS    CCIR
# TIME          1   24    1    1
# MONTH      2009 3.00
# SUNSPOT      6.
# LABEL     RIYADH (AR RIYAD)   WARSAW (WARSZAWA)   
# CIRCUIT   24.63N    46.71E    52.25N    21.00E  S     0
# SYSTEM       1. 145. 1.00  90. 45.0 3.00 0.10
# FPROB      1.00 1.00 1.00 0.00
# ANTENNA       1    1   02   30     0.000[default/swwhip.voa   ]  0.0    0.1500
# ANTENNA       2    2   02   30     0.000[default/swwhip.voa   ]  0.0    0.0000
# FREQUENCY  2.40 3.30 4.90 6.00 7.20 9.7011.8013.7015.3017.7021.60
# METHOD       30    0
# EXECUTE
# QUIT


#from __future__ import with_statement
import calendar
import datetime
import os.path
import string
import sys
import textwrap

#from voaLocation import *
from hamlocation import *

DEBUG = False

class VOADatFile:
    comment  = 'COMMENT    File generated by pythonProp package.\n'
    coeffs   = 'CCIR'
    linemax  = 'LINEMAX      55\n'
    month    = 'MONTH'
    sunspot  = 'SUNSPOT'
    frprob   = 'FPROB'
    method   = 'METHOD'
    label    = 'LABEL'
    power    = 0.0
    antenna  = ['ANTENNA', 'ANTENNA']

    frequency_list = ()
    
    ssn_list = ()
    
    SHORT_PATH    = 0
    LONG_PATH    = 1
    
    TX_ANTENNA    = 0
    RX_ANTENNA     = 1
    
    CIRCUIT_FORMAT = 0
    GRAPHICAL_FORMAT = 1


    def __init__(self, fn):
        self.filename = fn
        

    # COMMENT 
    # 1-10    COMMENT command
    # 11-80    User comment
    def set_title(self, title_list):
        self.title = title_list
        

    def get_comment_card(self, comment_list):
        comment_str  = ''
        for comment in comment_list:
            tw_str = textwrap.fill(comment, width=69).split('\n')
            for line in tw_str:
                #line = +line
                comment_str = comment_str + 'COMMENT   ' + line + '\n'
        return comment_str
        
    def set_linemax(self, max):
        self.linemax = 'LINEMAX   '+str(max).rjust(5)+'\n'
    
    # MONTH
    # 1-10 MONTH command
    # 11-15 year
    # 16-20 month
    # MONTH      2009 3.00 4.00 5.00

    # SUNSPOT
    # 1-10 SUNSPOT command
    # 11-15 12 month mean sunspot value
    
    # ssn_list is a list of tuples (day, month, year, ssn)
    def set_ssn(self, ssn_list):
        self.ssn_list = ssn_list

        
    def get_month_ssn_cards(self, ssn_list=None ): 
        month     = 'MONTH     '
        sunspot     = 'SUNSPOT   '
        if ssn_list:
            if (len(ssn_list) > 12):
                ssn_list = ssn_list[0:11]
            for item in ssn_list:
                _day, _month, _year, _ssn = item
                if ((_day < 0) or (_day>30)): break
                if ((_month < 1) or (_month>12)): break
                the_month = str(_month) + '.' + str(_day)
                the_ssn = "%.1f" % float(_ssn)
                month = month + str(_year).rjust(5) + the_month.rjust(5)
                sunspot = sunspot + the_ssn.rjust(5)
        month = month + '\n'
        sunspot = sunspot + '\n'
        return month + sunspot

    def set_coeffs(self, coeffs):
        self.coeffs = coeffs.strip()
        
    def get_coeffs(self):
        return self.coeffs

    def get_coeffs_card(self):        
        return 'COEFFS    '+self.coeffs+'\n'
        
    # SYSTEM
    # 1-10 SYSTEM command
    # 11-15 Tx. PoSYSTEM       1. 145. 1.00  90. 45.0 3.00 0.10wer (kW)
    # 16-20 XNOISE
    # 21-25 AMIND
    # 26-30 XLUFP
    # 31-35 RSN
    # 36-4PMP
    # 41-45 DMPX
    # SYSTEM       1. 145. 1.00  90. 45.0 3.00 0.10
    # FORMAT(10X,F5.2,F5.0,F5.2,F5.0,3F5.2)
    # SYSTEM       1. 145. 3.00  90. 45.0 3.00 0.10
    def set_system(self, pwr, xnoise, amind, xlufp, rsn, pmp, dmpx):
        self.system = 'SYSTEM    '
        self.system = self.system + self.get_formatted_power(pwr,5)
        self.system = self.system + ("%.0f" % float(xnoise)).rjust(5)
        self.system = self.system + ("%.2f" % float(amind)).rjust(5)
        self.system = self.system + ("%.0f" % float(xlufp)).rjust(5)
        self.system = self.system + ("%.2f" % float(rsn)).rjust(5)
        self.system = self.system + ("%.2f" % float(pmp)).rjust(5)
        self.system = self.system + ("%.2f" % float(dmpx)).rjust(5) + '\n'
    
    # Accepts a power (in kW) and returns a formatted string
    # The number of decimal places is dependant upon the input power    
    def get_formatted_power(self, power, width):
        pow_str = ("%f" % float(power))[0:width]
        return pow_str.strip().rjust(width)
        
    # FPROB
    # 1-10 FPROB command
    # 11-15 PSC(1) Multiplier for foE > 0
    # 16-20 PSC(2) Multiplier for foF1
    # 21-25 PSC(3) Multiplier for foF2 > 0
    # 26-30 PSC(4) Multiplier for foEs
    # FPROB      1.00 1.00 1.00 0.00
    # FORMAT(10X,4A10)
    def set_fprob(self, psc1='1.0', psc2='1.0', psc3='1.0', psc4='0.0'):
        self.fprob = 'FPROB     '
        self.fprob = self.fprob + ("%.2f" % float(psc1)).rjust(5)
        self.fprob = self.fprob + ("%.2f" % float(psc2)).rjust(5)
        self.fprob = self.fprob + ("%.2f" % float(psc3)).rjust(5)
        self.fprob = self.fprob + ("%.2f" % float(psc4)).rjust(5) + '\n'
        
    # LABEL
    # 1-10 LABEL command
    # 11-30 ITran
    # 31-50 IRcvr
    # FORMAT(10X,4A10)
    #
    # CIRCUIT
    # 1-10 CIRCUIT command
    # 11-15    TLATD        F5.2    Latitude of Tx
    # 16        ITLAT        A1        N=North, S=South
    # 20-25    TLONGD    F5.2    Longitude of Tx
    # 26        ITLONG    A1        E=East, W=West
    # 31-25    RLATD        F5.2    Latitude of Receiver
    # 36        IRLAT        A1        N=North, S=South
    # 41-45    RLONGD    F5.2    Longitude of Rx
    # 46        IRLONG    A1        E=East, W=West
    # 51-55    NPSL        I5        0=Short, 1=Long
    # FORMAT(10X,F5.2,A1,3(F9.2,A1),4X,I5)
    def set_sites(self, tx_site, rx_site, path = SHORT_PATH):
        self.label = 'LABEL     ' + \
            self.format_site_label(tx_site.get_name()) + \
            self.format_site_label(rx_site.get_name()) + '\n'

        self.circuit = 'CIRCUIT   ' + ("%.2f" % abs(tx_site.get_latitude())).rjust(5)
        self.circuit = self.circuit + ('N' if tx_site.get_latitude() >= 0 else 'S')
        self.circuit = self.circuit + ("%.2f" % abs(tx_site.get_longitude())).rjust(9)
        self.circuit = self.circuit + ('E' if tx_site.get_longitude() >= 0 else 'W')
        self.circuit = self.circuit + ("%.2f" % abs(rx_site.get_latitude())).rjust(9)
        self.circuit = self.circuit + ('N' if rx_site.get_latitude() >= 0 else 'S')
        self.circuit = self.circuit + ("%.2f" % abs(rx_site.get_longitude())).rjust(9)
        self.circuit = self.circuit + ('E' if rx_site.get_longitude() >= 0 else 'W')
        self.circuit = self.circuit + ('  S ' if path == self.SHORT_PATH else '  L ')
        self.circuit = self.circuit + str(path).rjust(5) + '\n'
        
        
    # Returns a right justified string, limited to 20 chars in length
    def format_site_label(self, some_text):
        if len(some_text) > 20:
            some_text = some_text[0:19]
        return some_text.rjust(20)
        
        
    def set_antenna(self, tx_rx, data_file, bearing=0.0, power=0.0):
    # ANTENNA       2    2   02   30     0.000[default/swwhip.voa   ]  0.0    0.0000
        data_file = data_file.ljust(21)        
        self.antenna[tx_rx] = 'ANTENNA   '+\
                            str(tx_rx+1).rjust(5)+\
                            str(tx_rx+1).rjust(5)+\
                            '   02   30'+\
                            ("%.3f" % float(0.0)).rjust(10)+\
                            '['+data_file+']' +\
                            ("%.1f" % float(bearing)).rjust(5)+\
                            self.get_formatted_power(power,10)+'\n'

    # Frequency list is limited to 11 entries.  
    # Frequency precsion is 3     decimal places.
    def set_frequency_list(self, frequency_list):
        frequency_list = frequency_list if len(frequency_list)<=11 else frequency_list[0:11]
        self.frequency_list = []
        for frequency in frequency_list:
            if ((frequency<2.0) or (frequency > 30.0)):break
            self.frequency_list.append(frequency)
        
    def get_frequency_card(self, frequency_list):
        # The '$' sign in the frequency card allows us to use 
        # 3 d.p. in the frequency field
        card = 'FREQUENCY $'
        for frequency in self.frequency_list:
            card = card + ("%.3f" % float(frequency)).rjust(6)
            #card = card + ("%.2f" % float(frequency)).rjust(5)
        return card + '\n'


    def set_method(self, method):
        self.method = method
        
    def get_method_card(self, method):
        return 'METHOD    ' + str(method).strip().rjust(5) + '\n'
        
    def write_file(self, data_file_format):
        f = open(self.filename, 'wt')
        if data_file_format == self.CIRCUIT_FORMAT:
            f.write(self.get_comment_card(self.title))
            f.write(self.linemax)
            f.write(self.get_coeffs_card())
            f.write('TIME          1   24    1    1\n')

            f.write(self.label)
            f.write(self.circuit)
            f.write(self.system)
            f.write(self.fprob)
            f.write(self.antenna[0])
            f.write(self.antenna[1])
            f.write(self.get_frequency_card(self.frequency_list))
            #f.write('FREQUENCY  2.40 3.30 4.90 6.00 7.20 9.7011.8013.7015.3017.7021.60\n')
            f.write(self.get_method_card(self.method))

            for group in self.ssn_list:
                f.write(self.get_month_ssn_cards([group]))
                group_comment = 'GROUP'+str(self.ssn_list.index(group)+1).rjust(3)+':'+\
                                    self.get_group_description(group)
                f.write(self.get_comment_card([group_comment]))
                f.write('EXECUTE\n')

            f.write('QUIT\n')
            f.write('\n')
        elif data_file_format == self.GRAPHICAL_FORMAT:
            f.write(self.get_comment_card(self.title))
            f.write(self.linemax)
            f.write(self.get_coeffs_card())
            f.write('TIME          1   24    1    1\n')
            f.write(self.get_month_ssn_cards())
            f.write(self.label)
            f.write(self.circuit)
            f.write(self.system)
            f.write(self.fprob)
            f.write(self.antenna[0])
            f.write(self.antenna[1])
            for group in self.ssn_list:
                f.write(self.get_month_ssn_cards([group]))
                group_comment = 'GROUP'+str(self.ssn_list.index(group)+1).rjust(3)+':'+\
                                    self.get_group_description(group)
                f.write(self.get_comment_card([group_comment]))
                f.write(self.get_method_card('26'))
                f.write('EXECUTE\n')
                f.write('FREQUENCY  -1\n')
                f.write(self.get_method_card(self.method))
                f.write('EXECUTE\n')                
            f.write('QUIT\n')
            f.write('\n')
        else:
            print "Invalid data file format specified."
        f.close()
        
    def get_group_description(self, group):   
        _day_str = '' if group[0] == 0 else str(group[0]).rjust(3)
        _month_str = calendar.month_abbr[group[1]].rjust(4)
        _year_str = str(group[2]).rjust(5)
        _ssn_str = str(group[3]).rjust(4)+'ssn'
        return _day_str + _month_str + _year_str + _ssn_str