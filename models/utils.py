#!/usr/bin/python
# -*- coding: utf-8 -*-

import dateutil.parser, datetime
from bson.objectid import ObjectId
from gluon.custom_import import track_changes
from oauth import OAuth2
from oauth.storage import MongoStorage
from oauth.exceptions import *
track_changes(True)

CODES = {'ok': 200}
MESSAGES = {'ok': 'success'}

def validate_access_token(f):
    """
    Function decorator which validates an access token.
    """
    
    mongo = MongoStorage()
    mongo.connect()
    oauth = OAuth2(mongo)
    
    response.headers['Content-Type'] = json_headers()
    response.view = json_service()

    try:
        header = request.env['http_authorization']
        token = oauth.validate_access_params(request.get_vars, request.post_vars,
                                             header)
                                        
        return f
    except OAuth2AuthenticateException as auth_ex:
        error_code, error_msg = auth_ex.http_response.split(' ')
        return lambda: meta_data(error_code, error_msg)
    except OAuth2RedirectException as redir_ex:
        return lambda: meta_data(redir_ex.error, redir_ex.msg)

def meta_data(code, msg, information = {}):
        return dict({'code':code, 'msg':msg}.items() + information.items())
              
def parse_to_date(default, arg):
        try:
                if default is not None:
                        return dateutil.parser.parse(default) if arg is None else dateutil.parser.parse(arg)
                else:
                        return None if arg is None else dateutil.parser.parse(arg)
        except ValueError:
                return default
 
def json_service():
        return 'generic.json'
        
def json_headers():
        return 'application/json; charset=utf-8'

def encode_model(obj, recursive=False):
    import bson
    import datetime
    if obj is None:
            return obj
    elif isinstance(obj, int):
            out = obj
    elif isinstance(obj, float):
            out = obj
    elif isinstance(obj, (list)):
            out = [encode_model(item) for item in obj]
    elif isinstance(obj, (str, unicode)):
            out = obj
    elif isinstance(obj, (dict)):
            out = dict([(k, encode_model(v)) for (k, v) in obj.items()])
    elif isinstance(obj, datetime.datetime):
            out = str(obj)
    elif isinstance(obj, datetime.timedelta):
            out = str(obj)
    elif isinstance(obj, bson.objectid.ObjectId):
            out = {'ObjectId': str(obj)}
    else:
            raise NameError("Could not JSON-encode type '%s': %s" % (type(obj), str(obj)))
    return out
