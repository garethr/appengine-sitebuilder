#!/usr/bin/python
import code
import os
import getpass
import sys

# insert application path
app_path = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), '../'
)
sys.path.insert(0, app_path)

# assuming appengine isn't already on your path you'll need to add it
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db

def auth_func():
    return raw_input('Username:'), getpass.getpass('Password:')

if len(sys.argv) < 2:
    print "Usage: %s [host]" (sys.argv[0]
    exit(1)

app_id = "sitebuilder"

if len(sys.argv) == 2:
    host = sys.argv[1]
else:
    host = '%s.appspot.com' % app_id

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)

code.interact('App Engine interactive console for %s' % (app_id,), None, locals())