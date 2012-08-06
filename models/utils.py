# -*- coding: utf-8 -*-

import dateutil.parser, datetime

TIME_FORMAT         = '%Y-%m-%d %H:%M'
EARTH_RADIUS        = 6378.0 # Kilometers
CODES = {'ok':200, 'no_such_event':400}
MESSAGES = {'ok':'success'}

#FIXME: Change the default values of lat/lon to a user's place
DEFAULT_VALUES = dict(lat=41.150223, lon=-8.609848, radius=1000, page_size=10, page_number=1)

def meta_data(code, msg, information = {}):
        return dict({'code':code, 'msg':msg}.items() + information.items())

def parse_to_int(default, arg):
        try:
                return int(default if arg is None else arg)
        except ValueError:
                return default

def parse_to_float(default, arg):
        try:
                return float(default if arg is None else arg)
        except ValueError:
                return default
                
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
            """
    if isinstance(obj, (bson.Document, bson.EmbeddedDocument)):
            out = dict(obj._data)
            for k,v in out.items():
                    if isinstance(v, ObjectId):
                            if k is None:
                                    out['_id'] = str(v)
                                    del(out[k])
                            else:
                                    # Unlikely that we'll hit this since ObjectId is always NULL key
                                    out[k] = str(v)
                    else:
                            out[k] = encode_model(v)
    elif isinstance(obj, mongoengine.queryset.QuerySet):
            out = encode_model(list(obj))
    elif isinstance(obj, ModuleType):
            out = None
    elif isinstance(obj, groupby):
            out = [ (g,list(l)) for g,l in obj ]
    """
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
