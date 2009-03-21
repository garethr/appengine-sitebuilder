from urlparse import urlparse

from google.appengine.ext import webapp

def get_domain(value):
    try:
        parts = urlparse(value)
        val = parts[1]
        # as we're getting feeds we get some data from feedburner
        # which hides the url. 
        if val == "feedproxy.google.com":
            path = parts[2].split("/")
            val = path[2]
    except:
        val = value
        
    return val

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()
register.filter(get_domain)
