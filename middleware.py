from webob import Request

from lib import add_to_end

class SimpleMiddleware(object):
    "Example middleware that appends a message to all 200 html responses"
    
    def __init__(self, app):
        self.app = app
   
    def __call__(self, environ, start_response):       
        # deal with webob request and response objects
        # due to a nicer interface
        req = Request(environ)
        resp = req.get_response(self.app)
        # if it's not text/html or a 200 then we don't care
        if resp.content_type != 'text/html' or resp.status_int != 200:
            return resp(environ, start_response)
        # add a string to the end of the body
        body = add_to_end(resp.body, "")
        # set the body to the new copy
        resp.body = body
        return resp(environ, start_response)