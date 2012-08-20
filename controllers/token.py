#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    """
    Exchange a <code, client_id, client_secret, redirect_uri> for an access
    token.
    """

    mongo = MongoStorage()
    mongo.connect()
    oauth = OAuth2(mongo)

    response.headers['Content-Type'] = json_headers()
    response.view = json_service()

    try:
        token, refresh, expires = oauth.grant_access_token(request.post_vars)
        return meta_data(CODES['ok'],
                         MESSAGES['ok'],
                         dict(access_token = token, token_type = 'Bearer',
                              expires_in = expires, refresh_token = refresh))
    except OAuth2ServerException as server_ex:
        error_code, error_msg = server_ex.http_response.split(' ')
        return meta_data(error_code, error_msg)
        
