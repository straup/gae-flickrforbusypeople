#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp

import ffbp.App
import ffbp.Auth
import ffbp.API

if __name__ == '__main__':

  handlers = [
    ('/', ffbp.App.Main),
    ('/settings', ffbp.App.Settings),    
    ('/signout', ffbp.Auth.Signout),
    ('/signin', ffbp.Auth.Signin),    
    ('/auth', ffbp.Auth.TokenDance),
    ('/api', ffbp.API.Dispatch),      
    ]

  application = webapp.WSGIApplication(handlers, debug=True)
  wsgiref.handlers.CGIHandler().run(application)
