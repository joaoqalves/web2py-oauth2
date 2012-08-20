#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    """
    It adds a new client app to the database. You need to provide a name for the
    app and a valid callback URI. It will return the client_id and client_secret
    generated.
    """
    
    mongo = MongoStorage()
    mongo.connect()
    oauth = OAuth2(mongo)
    
    success = False
    if request.post_vars:
        client_name, client_uri = request.post_vars['client_name'], request.post_vars['client_uri']
        client_id, client_secret = oauth.storage.add_client(client_name, client_uri)
        success = True

    return locals()
