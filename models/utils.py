#!/usr/bin/python
# -*- coding: utf-8 -*-

import dateutil.parser, datetime
from bson.objectid import ObjectId
from gluon.custom_import import track_changes
from oauth import OAuth2
from oauth.storage import web2pyStorage as storage  # change to MongoStorage if you aren't using DAL
from oauth.exceptions import *
track_changes(True)

CODES = {'ok': 200}
MESSAGES = {'ok': 'success'}

def validate_access_token(f):
    """
    Function decorator which validates an access token.
    """

    from oauth.storage import web2pyStorage as storage  # change to MongoStorage if you aren't using DAL
    storage = storage()
    storage.connect()
    oauth = OAuth2(storage)
    
    response.headers['Content-Type'] = json_headers()
    response.view = json_service()

    header = request.env['http_authorization']
    token = oauth.validate_access_params(request.get_vars, request.post_vars,
                                         header)
                                    
    return f  # what does f have?
              
def parse_to_date(default, arg):
    try:
        if default:
            return dateutil.parser.parse(default) if not arg else dateutil.parser.parse(arg)
        else:
            return None if not arg else dateutil.parser.parse(arg)
    except ValueError:
        return default
 
def json_service():
    return 'generic.json'
        
def json_headers():
    return 'application/json; charset=utf-8'

def encode_model(obj, recursive=False):
    if obj is None:
        return obj

    import bson
    import datetime

    if isinstance(obj, (int, float, basestring)):
        out = obj
    elif isinstance(obj, list):
        out = [encode_model(item) for item in obj]
    elif isinstance(obj, dict):
        out = dict([(k, encode_model(v)) for (k, v) in obj.items()])
    elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
        out = str(obj)
    elif isinstance(obj, bson.objectid.ObjectId):
        out = {'ObjectId': str(obj)}
    else:
        raise NameError("Could not JSON-encode type '%s': %s" % (type(obj), str(obj)))

    return out
