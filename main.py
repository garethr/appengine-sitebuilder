#!/usr/bin/env python

import os
from datetime import timedelta, date
from calendar import isleap, monthrange

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from models import NewsItem, Tag

class Index(webapp.RequestHandler):
    def get(self):
        tags = ['tag1',]
        
        item = NewsItem(
            title="title with spaces to check ? slugify",
            content="content4",
            external_url="http://example.com",
            tags=tags,
        )
        item.put()
        items = NewsItem.all()
        items.order('-publish_date')
        context = {
            "items": items,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        output = template.render(path, context)
        self.response.out.write(output)
        
class DateList(webapp.RequestHandler):
    def get(self, year, month=None, day=None):
        
        if not month:
            # we're dealing with a year only
            # check how many days in this year
            if isleap(int(year)):
                days = 366
            else:
                days = 365
            lower_limit = date(int(year), 1, 1)
            upper_limit = lower_limit + timedelta(days)
        elif not day:
            # we have a month and year            
            lower_limit = date(int(year), int(month), 1)
            upper_limit = lower_limit + timedelta(monthrange(int(year), int(month))[1])
        else:
            # we have everything
            lower_limit = date(int(year), int(month), int(day))
            upper_limit = lower_limit + timedelta(1)
        
        items = NewsItem.all()
        items.filter('publish_date >', lower_limit)
        items.filter('publish_date <', upper_limit)        
        items.order('-publish_date')
        
        context = {
            "items": items,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'list.html')
        # render the template with the provided context
        output = template.render(path, context)
        self.response.out.write(output)

class TagList(webapp.RequestHandler):
    def get(self, tag):
        items = NewsItem.all()
        items.order('-publish_date')
        items.filter('tags = ', tag)
        context = {
            "items": items,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'list.html')
        # render the template with the provided context
        output = template.render(path, context)
        self.response.out.write(output)

class Tags(webapp.RequestHandler):
    def get(self):
        tags = Tag.all()
        context = {
            "tags": tags,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'tags.html')
        # render the template with the provided context
        output = template.render(path, context)
        self.response.out.write(output)
        
class Item(webapp.RequestHandler):
    def get(self, year, month, day, slug):
        item = NewsItem.gql("WHERE slug=:1", slug)[0]
        context = {
            "item": item,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'item.html')
        # render the template with the provided context
        output = template.render(path, context)
        self.response.out.write(output)
                        
# wire up the views
application = webapp.WSGIApplication([
    ('/', Index),
    ('/([0-9]{4})/([0-9]{2})/([0-9]{2})/([A-Za-z0-9-]+)/?$', Item),
    ('/([0-9]{4})/([0-9]{2})/([0-9]{2})/?$', DateList),
    ('/([0-9]{4})/([0-9]{2})/?$', DateList),
    ('/([0-9]{4})/?$', DateList),
    ('/tags/?$', Tags),
    ('/tags/([A-Za-z0-9-]+)/?$', TagList),

], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()