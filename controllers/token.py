#!/usr/bin/python
# -*- coding: utf-8 -*-


def index():
    """
    Exchange a <code, client_id, client_secret, redirect_uri> for an access
    token.
    """

    from oauth.storage import web2pyStorage as storage  # change to MongoStorage if you aren't using DAL
    storage = storage()
    storage.connect()
    oauth = OAuth2(storage)

    response.headers['Content-Type'] = json_headers()
    response.view = json_service()

    token, refresh, expires = oauth.grant_access_token(request.get_vars)
    return meta_data(CODES['ok'],
                     MESSAGES['ok'],
                     dict(access_token=token, token_type='Bearer',
                          expires_in=expires, refresh_token=refresh))
