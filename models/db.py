# -*- coding: utf-8 -*-

from gluon.tools import Service  # decorators
import re
import difflib
from unicodedata import normalize
from gluon.tools import DAL
from gluon.tools import URL
from gluon.tools import Auth
from gluon.tools import Mail
import pymongo
from gluon.http import redirect
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId

service = Service()

# Database
def make_connection_mongo(server = 'dev.tymr.com', db_name = 'tymr'):
    server = 'localhost'
    port = 27017
    conn = pymongo.Connection(server, port)
    mongo = conn[db_name]
    return mongo

try:
    mongo = cache.ram('mongodb', make_connection_mongo, None)
except:
    redirect(URL(a='tymr', c='default', f='error'))
    
def resultset_meta(page_number, page_size, cursor):
    """Create the metadata for any resultset. The parameters are:
    page_number - the page number of the results
    page_size - the page size of each page of results
    cursor - the resultset cursor
    
    """
    records = cursor.count()
    page_records = cursor.count(True)
    pages = cursor.count() / page_size
    pages += (1 if cursor.count() % page_size > 0 else 0)
    return {'page_number':page_number, 'page_size':page_size,'pages':pages,
            'page_records':page_records, 'records':records}

def find_event_by_id(event_id):
    
    event = mongo.events.find_one({'_id': event_id})
    
    if event == None:
        raise Exception('There is no event with the id ' + str(event_id))
        
    return event

def search_event(location, area, start_date, end_date, page_number, page_size):

    mongo.events.ensure_index([('date.place.geo', pymongo.GEO2D)])
    if start_date is None:
        cursor = mongo.events.find({'date.end':{'$lte':end_date},
                                    'date.place.geo':{'$within':
                                        {'$centerSphere': [location, area],
                                         '$uniqueDocs': True}}})
    else:
        cursor = mongo.events.find({'date.start':{'$gte':start_date},
                                    'date.end':{'$lte':end_date},
                                    'date.place.geo':{'$within':
                                                        {'$centerSphere':
                                                         [location, area],
                                                         '$uniqueDocs': True}}})
                                                         
    cursor = cursor.skip(page_number*page_size).limit(page_size)                
    return cursor.sort('date.end', pymongo.ASCENDING)

# Return an error dictionary in JSON
def error(error_type, msg):
    return dict(error=dict({'id':ERRORS[error_type], 'msg': msg}))

