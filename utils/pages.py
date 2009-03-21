#!/usr/bin/python

# we want to record how long this takes to run
import time
start_time = time.time()

import sys
import os
import getpass
import feedparser

from yahoo.search.term import TermExtraction

# insert application path as we need access to the models
app_path = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), '../'
)
sys.path.insert(0, app_path)

import settings

# assuming appengine isn't already on your path you'll need to add it
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db

# if we don't have a host then exit
if len(sys.argv) < 2:
    print "Usage: %s [host]" % sys.argv[0]
    exit(1)

def auth_func():
    "Callable which asks for a username and password"
    return raw_input('Username:'), getpass.getpass('Password:')

app_id = "hackerposts"
host = sys.argv[1]

# we need to configure the datastore before we import the models
remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
from models import Page

item = Page.all().filter('internal_url =', '/about/')[0]
item.delete()

item = Page(
    title="About",
    content="""
    <p>This software behind this site is a work in progress. As such it doesn't really have a name yet
    and the current design is very much just a placeholder.</p> 
    <p>The eventual plan is something like a cross
    between a planet style agregator and an online magazine for a specific context;
    say an event or community.</p>
    <p>This site is currently seeded with the blog feeds of some of
    the top 100 posters on <a href="news.ycombinator.com/">Hacker News</a> taken from their bios.
    This seemed to provide an interesting data set with which to experiment but if you want to be 
    remove then just let me know. If you want to know more please email 
    <a href="mailto:gareth@morethanseven.net">Gareth</a>.</p>
    """,
    internal_url="/about/",
)
item.put()
print "created page item"