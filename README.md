pythonPropWeb
=============

A Flask-based web app for making HF Radio Propagation Prediction Maps

The plotting code and VOACAP-calling code in this project is a derivative of pythonProp (http://sourceforge.net/projects/pythonprop/).

Any plot will be automatically created in the form of:
http://your.server.com/station/<band-short-name>/YYYYmm/HHMM/

Example:
http://k2bsa.w2naf.com/station/10m/201311/0500/

If that map has not been created yet, it will be created on the fly.  Once a map has already been created, the app will load the cached map off of the server.

Certain directories need to be writable to the web server/app:

itshfbc/ (Some things may be able to be locked down... but I'm not sure which ones yet)
static/output/

The app will not replot anything that has already been plotted.  To reset things, delete static/output, or the specific plot inside of there you want to delete.

Things will fail if the app cannot spawn the voacapl binary at the shell.  For now, I've put this binary in the root of this distribution.

The program should be updating the smoothed sunspot number (SSN) database every time the model is run. This is done in pyprop/vocapnogui.py line 129.
This has not been well tested.
