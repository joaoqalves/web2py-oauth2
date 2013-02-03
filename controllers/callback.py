#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2

# Change the values to your application id, secret and redirect_uri
APP = {'CLIENT_ID': '524fa225e2925ea0d9c700bfda40ec4e833c6e01',
       'CLIENT_SECRET': 'acd709c3f403701b875dc224695466ba7ce117ef',
       'REDIRECT_URI': 'http://localhost/oauth2/callback/',
       'TOKEN_URI': 'http://localhost/oauth2/token/'} 

def index():
    """
    This controller is not really part of the OAuth 2.0 server but it acts like
    a OAuth client callback. It receives a "code" parameter given by the "auth"
    controller and it tries to exchange the <code, id, secret, redirect_uri> for
    an access token.
    """
    
    code = request.get_vars['code']
    if code:
      # Prepares the request parameters
      url = APP['TOKEN_URI']
      values = dict(code = code,
                    client_id = APP['CLIENT_ID'],
                    client_secret= APP['CLIENT_SECRET'],
                    redirect_uri = APP['REDIRECT_URI'],
                    grant_type = 'authorization_code')
                      
      data = urllib.urlencode(values)
      req = urllib2.Request(url, data)
      rsp = urllib2.urlopen(req)
        
      # Gets the answer
      content = rsp.read()
      response.headers['Content-Type'] = json_headers()
      response.view = json_service()
      return content
        
    redirect(URL(c='error',vars=dict(msg='No "code" parameter provided')))
