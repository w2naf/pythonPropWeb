#!/usr/bin/env python
#From http://flask.pocoo.org/docs/tutorial/setup/#tutorial-setup
#all the imports
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
import pymongo
from bson.objectid import ObjectId

import datetime
import os
import sys

#Confuguration
DEBUG = True
SECRET_KEY = 'HJJDnaoiwer&*(@#%@sdanbiuas@HEIu'
USERNAME = 'admin'
PASSWORD = 'default'

import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

app = Flask(__name__)
app.config.from_object(__name__)

sys.path.append(os.path.join(app.root_path,'pyprop'))
import voaAreaPlotWeb

root_path = app.root_path
templates_file    = os.path.join(root_path,'voacap_prefs','area_templ.ex')
viewControl_fName = os.path.join(root_path,'itshfbc','areadata','pyArea')

mongo         = pymongo.MongoClient()
db            = mongo.voacap
views_coll    = db.entries
stations_coll = db.stations

app.config.from_envvar('FLASKR_SETTINGS',silent=True)


@app.route('/')
def show_entries():
  stations = [x for x in stations_coll.find()]

  stations_sorted = sorted(stations, key=lambda k: float(k['frequency'])) 
  stations_sorted = stations_sorted[::-1]

  return render_template('index.html',stations=stations_sorted)

@app.route('/config')
def config():
  if not session.get('logged_in'):
    return redirect(url_for('login'))
  stations  = [x for x in stations_coll.find()]
  stations_sorted = sorted(stations, key=lambda k: float(k['frequency'])) 
  stations  = stations_sorted[::-1]
  entries   = [x for x in views_coll.find()]
  return render_template('config.html',entries=entries,stations=stations)

# Login/Session Control ########################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('config'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# Station Controls #############################################################
@app.route('/add_station',methods=['GET','POST'])
@app.route('/upsert_station',methods=['GET','POST'])
def upsert_station():
  if not session.get('logged_in'):
    abort(401)
  params = {}
  params['stationName'] = '20 Meters'
  params['shortName']   = '20m'
  params['foe']         = '1.0'
  params['fof1']        = '1.0'
  params['fof2']        = '1.0'
  params['foes']        = '0.0'
  params['model']       = '0'
  params['path']        = '0'
  params['mm_noise']    = '-145.0'
  params['min_toa']     = '3.0'
  params['required_reliability']  = '90.0'
  params['required_snr']  = '47.0'
  params['mpath']       = '3.0'
  params['delay']       = '0.1'
  params['tx_name']     = 'K2BSA_Summit'
  params['tx_lat']      = '37.9'
  params['tx_lon']      = '-81.1'
  params['tx_antenna']  = 'default/isotrope : ISOTROPE'
  params['tx_bearing']  = '0.0'
  params['tx_power']    = '100.0'
  params['gridsize']    = '125'
  params['year']        = '2013'
  params['month']       = '7'
  params['utc']         = '0.0'
  params['frequency']   = '14.290'
  params['sw_lat']      = '-90.0'
  params['sw_lon']      = '-180.0'
  params['ne_lat']      = '90.0'
  params['ne_lon']      = '180.0'
  params['templates_file'] = templates_file
#  params['rx_name'] = 'Test'
#  params['rx_lat'] = 'Test'
#  params['rx_lon'] = 'Test'
#  params['rx_antenna'] = 'Test'
#  params['rx_bearing'] = 'Test'

  models = []
  models.append({'text':'CCIR','value':'0','selected':False})
  models.append({'text':'URSI88','value':'1','selected':False})

  paths = []
  paths.append({'text':'Short','value':'0','selected':False})
  paths.append({'text':'Long','value':'1','selected':False})

  views = [{'value':x['viewName'],'selected':''} for x in views_coll.find()]

  if request.form.has_key('ObjectId'):
    _oid    = request.form['ObjectId']
    oid     = ObjectId(_oid)
    params  = stations_coll.find_one({"_id":oid})
    edit    = True

    #Select view from drop down list
    if params.has_key('viewName'):
      for view in views:
        if view['value']==params['viewName']:
          view['selected'] = True

    if params.has_key('model'):
      for model in models:
        if model['value']==params['model']:
          model['selected'] = True

    if params.has_key('path'):
      for path in paths:
        if path['value']==params['path']:
          path['selected'] = True
  else:
    _oid    = None
    edit    = False

#  import ipdb; ipdb.set_trace()
  return render_template('station_form.html',params=params,edit=edit,_oid=_oid,views=views,models=models,paths=paths)

@app.route('/db_upsert_station', methods=['POST'])
def db_upsert_station():
  if not session.get('logged_in'):
    abort(401)
  params = {}
  params['stationName'] = request.form['stationName']
  params['shortName'] = request.form['shortName']
  params['viewName'] = request.form['viewName']
  params['foe'] = request.form['foe']
  params['fof1'] = request.form['fof1']
  params['fof2'] = request.form['fof2']
  params['foes'] = request.form['foes']
  params['model'] = request.form['model']
  params['path'] = request.form['path']
  params['mm_noise'] = request.form['mm_noise']
  params['min_toa'] = request.form['min_toa']
  params['required_reliability'] = request.form['required_reliability']
  params['required_snr'] = request.form['required_snr']
  params['mpath'] = request.form['mpath']
  params['delay'] = request.form['delay']
  params['tx_name'] = request.form['tx_name']
  params['tx_lat'] = request.form['tx_lat']
  params['tx_lon'] = request.form['tx_lon']
  params['tx_antenna'] = request.form['tx_antenna']
  params['tx_bearing'] = request.form['tx_bearing']
  params['tx_power'] = request.form['tx_power']
  params['gridsize'] = request.form['gridsize']
  params['year'] = request.form['year']
  params['month'] = request.form['month']
  params['utc'] = request.form['utc']
  params['frequency'] = request.form['frequency']
  params['sw_lat'] = request.form['sw_lat']
  params['sw_lon'] = request.form['sw_lon']
  params['ne_lat'] = request.form['ne_lat']
  params['ne_lon'] = request.form['ne_lon']
  params['templates_file'] = request.form['templates_file']

  _oid   = request.form['ObjectId']
  if _oid=='':
    entry_id = stations_coll.insert(params)
    flash('New station was successfully added.')
  else:
    oid    = ObjectId(_oid)
    entry_id = stations_coll.update({'_id':oid}, {"$set": params}, upsert=False)
    flash('Station was successfully updated.')
  return redirect(url_for('config'))

@app.route('/db_delete_station', methods=['POST'])
def db_delete_station():
  if not session.get('logged_in'):
    abort(401)
  oid   = ObjectId(request.form['ObjectId'])
  entry = stations_coll.find_and_modify({"_id":oid},remove=True)
  flash('Station Entry Deleted')
  return redirect(url_for('config'))

# View Control #################################################################
@app.route('/add_view',methods=['GET','POST'])
@app.route('/upsert_view',methods=['GET','POST'])
def upsert_view():
  if not session.get('logged_in'):
    abort(401)
  params = {
    'fileName': viewControl_fName,
    'data_type':'2',
    'vg_files':'1',
    'time_zone':'0',
    'color_map':'jet',
    'plot_contours':'False',
    'plot_meridians':'True',
    'plot_parallels':'True',
    'plot_terminator':'True'}

  if request.form.has_key('ObjectId'):
    _oid    = request.form['ObjectId']
    oid     = ObjectId(_oid)
    params  = views_coll.find_one({"_id":oid})
    edit    = True
  else:
    _oid    = None
    edit    = False

  return render_template('view_form.html',params=params,edit=edit,_oid=_oid)

@app.route('/db_upsert_view', methods=['POST'])
def db_upsert_view():
  if not session.get('logged_in'):
    abort(401)
  params = {
    'viewName':request.form['viewName'],
    'fileName':request.form['fileName'],
    'data_type':request.form['data_type'],
    'vg_files':request.form['vg_files'],
    'time_zone':request.form['time_zone'],
    'color_map':request.form['color_map'],
    'plot_contours':request.form['plot_contours'],
    'plot_meridians':request.form['plot_meridians'],
    'plot_parallels':request.form['plot_parallels'],
    'plot_terminator':request.form['plot_terminator']}
  _oid   = request.form['ObjectId']
  if _oid=='':
    entry_id = views_coll.insert(params)
    flash('New view was successfully added.')
  else:
    oid    = ObjectId(_oid)
    entry_id = views_coll.update({'_id':oid}, {"$set": params}, upsert=False)
    flash('View was successfully updated.')
  return redirect(url_for('config'))

@app.route('/db_delete_view', methods=['POST'])
def db_delete_view():
  if not session.get('logged_in'):
    abort(401)
  oid   = ObjectId(request.form['ObjectId'])
  entry = views_coll.find_and_modify({"_id":oid},remove=True)
  flash('View Deleted')
  return redirect(url_for('config'))

# Run Model ####################################################################
@app.route('/run', methods=['POST'])
def run_model(shortName,dt):
  import voacapnogui as voa
  g=voa.VOACAP_GUI(path=root_path)

  params  = stations_coll.find_one({"shortName":shortName})
  if params is None:
    #Model shortName not found.  Exiting with error code 1.
    return 1

  params['utc']   = dt.strftime('%H')
  params['year']  = dt.strftime('%Y')
  params['month'] = dt.strftime('%m')
  
  g.update_parameters(params)
  g.run_prediction(type='area')

  entry = views_coll.find_one({"viewName":params['viewName']})

  fileName          = os.path.join(root_path,'itshfbc','areadata',params['shortName']+'-pyArea')
  outputPath  = os.path.join(root_path,'static','output',params['shortName'])
  try:
    os.makedirs(outputPath)
  except:
    pass

  dt = datetime.datetime(g.params.year,g.params.month,1,g.params.utc)

  _save_file        = os.path.join(outputPath,params['shortName']+dt.strftime('-%Y%m.%H00.png'))
  _data_type  = entry['data_type']
  _vg_files   = [int(entry['vg_files'])]
  _time_zone  = int(entry['time_zone'])
  _color_map  = entry['color_map']
  _plot_contours    = bool(int(entry['plot_contours']))
  _plot_meridians   = bool(int(entry['plot_meridians']))
  _plot_parallels   = bool(int(entry['plot_parallels']))
  _plot_terminator  = bool(int(entry['plot_terminator']))
  _run_quietly      = True
  plot = voaAreaPlotWeb.VOAAreaPlot(fileName,
                  data_type = _data_type,
                  vg_files = _vg_files,
                  time_zone = _time_zone,
                  color_map = _color_map,
                  plot_contours   = _plot_contours,
                  plot_meridians  = _plot_meridians,
                  plot_parallels  = _plot_parallels,
                  plot_terminator = _plot_terminator,
                  run_quietly     = _run_quietly,
                  save_file       = _save_file)

  #Model run successful. Exit with success code 0.
  return 0


# Plotting #####################################################################
@app.route('/station/<shortName>/')
@app.route('/station/<shortName>/<date>/')
@app.route('/station/<shortName>/<date>/<time>/')
@app.route('/plot_map')
def plot_map(shortName=None,date=None,time=None):
  if date==None and time==None:
    dt = datetime.datetime.utcnow()
  else:
    if time == None: time = '0000'
    try:
      if len(date) == 6:
        dt = datetime.datetime.strptime(date+time,'%Y%m%H%M')
      elif len(date) == 8:
        dt = datetime.datetime.strptime(date+time,'%Y%m%d%H%M')
      else:
        abort(404)
    except:
      abort(404)

  params = None
  if shortName != None:
    params  = stations_coll.find_one({"shortName":shortName})

  try:
    outputPath  = os.path.join('static','output',params['shortName'])
    fName = os.path.join(outputPath,params['shortName']+dt.strftime('-%Y%m.%H00.png'))
  except:
    abort(404)

  if not os.path.exists(fName):
    error = run_model(shortName,dt)

  #I need the actual model time as a datetime.datetime object so I can do a little math on it
  #to calculate forwards and backwards in time.
  tmpDt = datetime.datetime(dt.year,dt.month,15,dt.hour)
  nav   = {}
  tmp   = ((dt.hour + 1) % 24)*100
  tmp   = ('%04d' % tmp)
  nav['forwardHr'] = dt.strftime('/%Y%m/')+tmp
  tmp   = ((dt.hour - 1) % 24)*100
  tmp   = ('%04d' % tmp)
  nav['backHr'] = dt.strftime('/%Y%m/')+tmp
  tmp   = (dt.month + 1) % 12
  tmp   = ('%02d' % tmp)
  nav['forwardMonth'] = dt.strftime('/%Y')+tmp+dt.strftime('/%H00')
  tmp   = (dt.month - 1) % 12
  tmp   = ('%02d' % tmp)
  nav['backMonth'] = dt.strftime('/%Y')+tmp+dt.strftime('/%H00')
  tmp   = dt.year + 1
  tmp   = ('%04d' % tmp)
  nav['forwardYear'] = '/'+tmp+dt.strftime('%m/%H00')
  tmp   = dt.year - 1
  tmp   = ('%04d' % tmp)
  nav['backYear'] = '/'+tmp+dt.strftime('%m/%H00')

  dateStr = dt.strftime('%B %Y %H:00 UT') #Used for pretty printing date on station page.
  return render_template('map.html',params=params,fName=fName,dateStr=dateStr,nav=nav)

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5002)
