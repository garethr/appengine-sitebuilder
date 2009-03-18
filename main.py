#!/usr/bin/env python

import os
from datetime import timedelta, date
from calendar import isleap, monthrange
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from models import Page, Tag, Content
import settings
from middleware import SimpleMiddleware

class BaseRequest(webapp.RequestHandler):
    def _extra_context(self, context):        
        extras = {
            "today": date.today(),
            "yesterday": date.today() - timedelta(1),
            "this_month": date.today(),
            "last_month": date.today() - timedelta(monthrange(date.today().year, date.today().month)[1]),
        }
        path = self.request.path        
        content = Content.all().filter('path =', path)
        content_extras = {}
        for item in content:
            content_extras[item.ident] = item.value
                
        context.update(extras)
        context.update(content_extras)
        return context
        
    def render(self, template_file, context={}):
        path = os.path.join(os.path.dirname(__file__), 'templates',
            template_file)
        # render the template with the provided context
        output = template.render(path, self._extra_context(context))
        self.response.out.write(output)        
    
class Index(BaseRequest):
    def get(self):

        """
        tags = ['tag 1','tag 4']
        item = Page(
            title="title4",
            content="content and more",
            external_url="http://example.com",
            tags=tags,
        )
        item.put()
        """
        """
        item = Page(
            title="about",
            content="content",
            internal_url="/about/",
            tags=tags,
        )
        item.put()
        """
        """
        content = Content(
            path="/",
            ident="title",
            value="something interesting",
        )
        content.put()
        """


        items = Page.all().order('-publish_date').fetch(20)
        context = {
            "items": items,
            "title": "Home",
        }
        # calculate the template path
        self.render("index.html", context)
        
class DateList(BaseRequest):
    def get(self, year, month=None, day=None):
        
        # we want a canonical url with the trailing slash
        # so if it's missing we need to throw a 301, adding the slash in 
        # the process
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return
        
        if not month:
            # we're dealing with a year only
            # check how many days in this year
            if isleap(int(year)):
                days = 366
            else:
                days = 365
            lower_limit = date(int(year), 1, 1)
            upper_limit = lower_limit + timedelta(days)
            title = year
        elif not day:
            # we have a month and year            
            lower_limit = date(int(year), int(month), 1)
            upper_limit = lower_limit + timedelta(monthrange(int(year), int(month))[1])
            title = "%s %s" % (lower_limit.strftime("%B"), year)
        else:
            # we have everything
            lower_limit = date(int(year), int(month), int(day))
            upper_limit = lower_limit + timedelta(1)
            title = "%s %s %s" % (lower_limit.strftime("%d"), lower_limit.strftime("%B"), year)
        
        items = Page.all()
        items.filter('publish_date >', lower_limit)
        items.filter('publish_date <', upper_limit)        
        items.order('-publish_date')
        
        context = {
            "items": items,
            "title": "News from %s" % title
        }
        self.render("list.html", context)

class TagList(BaseRequest):
    def get(self, tag):
        
        # we want a canonical url with the trailing slash
        # so if it's missing we need to throw a 301, adding the slash in 
        # the process
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return
        
        items = Page.all()
        items.order('-publish_date')
        items.filter('tags = ', tag.replace("-", " "))
        context = {
            "items": items,
            "title": "Content tagged %s" % tag,
        }
        self.render("list.html", context)

class Tags(BaseRequest):
    def get(self):
        
        # we want a canonical url with the trailing slash
        # so if it's missing we need to throw a 301, adding the slash in 
        # the process
        if self.request.path[-1] != "/":
            self.redirect("%s/" % self.request.path, True)
            return
        
        tags = Tag.all()
        tags.order('-date')
        context = {
            "tags": tags,
            "title": "Latest tags",
        }
        self.render("tags.html", context)
        
class Item(BaseRequest):
    def get(self, slug):

        # we want a canonical url with the trailing slash
        # so if it's missing we need to throw a 301, adding the slash in 
        # the process
        if slug[-1] != "/":
            self.redirect("%s/" % slug, True)
            return

        try:
            item = Page.gql("WHERE internal_url=:1", slug)[0]
        except IndexError:
            self.error(404)
            self.render("404.html", {"title": "Page not found"})
            return
        
        # get a list of related items based on taggings
        # remember to filter out the article we're on
        related = []
        for tag in item.tags:
             related += (Tag.all().filter('name =', tag).filter('title !=', item.title))
            
        # we also need to deduplicate the list as sometimes items
        # will share tags
        seen = [] 
        deduped = []
        for related_item in related:
            if not related_item.url in seen:
                deduped.append(related_item)
                seen.append(related_item.url)
        
        context = {
            "item": item,
            "related": deduped,
            "title": item.title,
        }
        self.render("item.html", context)
   
class Search(BaseRequest):
    def get(self):
   
        query = self.request.get("q")
        
        if not query:
            items = []
            title = ""
        else:
            items = Page.all().search(query).order("-publish_date")
            title = " for %s" % query
                        
        context = {
            "items": items,
            "query": self.request.get("q"),
            "title": "Search%s" % title
        }
        self.render("search.html", context)
                     
class NotFoundPageHandler(BaseRequest):
    def get(self):
        self.error(404)
        self.render("404.html", {"title": "Page not found"})

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))
                        
def main():
    "Run the application"
    # wire up the views
    ROUTES = [
        ('/', Index),
        ('/([0-9]{4})/([0-9]{2})/([0-9]{2})/?$', DateList),
        ('/([0-9]{4})/([0-9]{2})/?$', DateList),
        ('/([0-9]{4})/?$', DateList),
        ('/tags/?$', Tags),
        ('/tags/([A-Za-z0-9-]+)/?$', TagList),
        ('/search/?$', Search),
        ('([A-Za-z0-9-/]+)', Item),
        ('/.*', NotFoundPageHandler),
    ]
    application = webapp.WSGIApplication(ROUTES, debug=settings.DEBUG)
    # add simple middleware
    application = SimpleMiddleware(application)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()