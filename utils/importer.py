#!/usr/bin/python

"Import script to import content from a list of feeds"

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

handle = open("feeds", "r") 
feeds = handle.readlines()
handle.close() 

# number of new items added
counter = 0

# loop over all the feeds
for feed in feeds:
    print "importing from %s" % feed
    feed_obj = feedparser.parse(feed)
    # then loop over each entry
    for entry in feed_obj['entries']:
        title = entry.title
        link = entry.links[0].href  
        # use content if available, otherwise get the summary  
        try:
            content = entry.content[0].value
        except AttributeError:
            content = entry.summary
            
        # create the object in the datastore only if one with the 
        # same external link doesn't already exist
        
        if Page.all().filter('external_url =', link).count() == 0:
            print "  creating %s" % entry.title

            try:
                # use the Yahoo term extraction API to get tags for the content
                srch = TermExtraction(app_id=settings.TERM_EXTRACTION_APP_ID)
                srch.context = content

                tags = []
                for tag in srch.parse_results():
                    tags.append(tag)

                # create out new Page object
                item = Page(
                    title=title,
                    content=content,
                    external_url=link,
                    tags=tags,
                )
                item.put()
                # increment counter
                counter += 1
            except:
                print "   problem importing %s" % entry.title
        else:
            print "  duplicate %s" % entry.title
            
run_time = time.time() - start_time
print 'imported %s items from %d feeds in %f seconds' % (counter, len(feeds), run_time)