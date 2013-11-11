#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
cgitb.enable()

import sys
import os

file_dir = os.path.dirname(__file__)
ret0 = sys.path.insert(0,file_dir)
#voacapl_dir = '/usr/local/bin'
#ret = sys.path.append(voacapl_dir)
#
#with open('/var/www/k2bsa/error2.txt','w') as error_obj:
#    error_obj.write(str(ret0)+'\n')
#    error_obj.write('dir: '+file_dir+'\n')
#    error_obj.write(str(ret)+'\n')
#    error_obj.write('dir: '+voacapl_dir)


from voacap import app as application
