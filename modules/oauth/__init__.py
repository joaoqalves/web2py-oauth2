#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 João Alves <joaoqalves@gmail.com> and Tiago Pereira
# <tiagomiguelmoreirapereira@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pymongo
import datetime
from exceptions import *
import storage as oauthstorage

"""OAuth 2.0 draft 20 server in Python (for web2py framework), based on the PHP
OAuth2 Server <https://github.com/quizlet/oauth2-php>. It has the bearer token
system with MongoDB only. Feel free to extend the Storage class to the
Database Absraction Layer of web2py.
"""

class OAuth2(object):
    DEFAULT  = {'access_token_lifetime': 3600,
                'refresh_token_lifetime': 1209600,
                'auth_code_lifetime': 30,
                'realm': 'Service',
                'token_type': 'bearer',
                'enforce_redirect': False,
                'enforce_state': False,
                'supported_scopes': []}

    CONFIG_ACCESS_LIFETIME = 'access_token_lifetime'
    CONFIG_REFRESH_LIFETIME = 'refresh_token_lifetime'
    CONFIG_CODE_LIFETIME = 'auth_code_lifetime'
    CONFIG_SUPPORTED_SCOPES = 'supported_scopes'
    CONFIG_TOKEN_TYPE = 'token_type'
    CONFIG_WWW_REALM = 'realm'
    CONFIG_ENFORCE_INPUT_REDIRECT = 'enforce_redirect'
    CONFIG_ENFORCE_STATE = 'enforce_state'

    TOKEN_PARAM_NAME = 'access_token'
    TOKEN_BEARER_HEADER_NAME = 'Bearer'
    WWW_FORM_ENCODE = 'application/x-www-form-urlencoded'
    POST_METHOD = 'POST'
    GET_METHOD = 'GET'

    RESPONSE_TYPE_AUTH_CODE = 'code'
    RESPONSE_TYPE_AUTH_TOKEN = 'token'

    ACCESS_TYPE_ONLINE = 'online'
    ACCESS_TYPE_OFFLINE = 'offline'

    GRANT_TYPE = {'auth_code': 'authorization_code',
                  'implicit': 'token',
                  'user_credentials': 'password',
                  'client_credentials': 'client_credentials',
                  'refresh_token': 'refresh_token',
                  'extensions': 'extensions'}

    TOKEN_TYPE = {'bearer': 'bearer', 'mac': 'mac'}

    HTTP_RESPONSE = {'found': '302 Found', 
                     'bad_request': '400 Bad Request',
                     'unauthorized': '401 Unauthorized',
                     'forbidden': '403 Forbidden',
                     'unavailable': '503 Service Unavailable'}

    HTTP_AUTHORIZATION = 'http_authorization'
    HTTP_CONTENT_TYPE = 'http_content_type'
    HTTP_REQUEST_METHOD = 'request_method'

    ERROR = {'invalid_request': 'invalid_request',
             'invalid_client': 'invalid_client',
             'unauthorized_client': 'unauthorized_client',
             'redirect_uri_mismatch': 'redirect_uri_mismatch',
             'access_denied': 'access_denied',
             'unsupported_response_type': 'unsupported_response_type',
             'invalid_scope': 'invalid_scope',
             'invalid_grant': 'invalid_grant',
             'unsupported_grant_type': 'unsupported_grant_type',
             'insufficient_scope': 'invalid_scope',
             'invalid_code': 'invalide_code',
             'invalid_refresh': 'invalid_refresh',
             'expired_refresh': 'expired_refresh'}
    # ^Bit of overkill here with the object attributes, eh?!
             
    def __init__(self, storage, confs = None):
        """Constructor of the class. It takes 2 arguments:
        * The storage (database) instance where the data should be saved
        * A configuration dictionary like the default one:
            DEFAULT  = {'access_token_lifetime': 3600,
                'refresh_token_lifetime': 1209600,
                'auth_code_lifetime': 30,
                'realm': 'Service',
                'enforce_redirect': False,
                'enforce_state': False,
                'supported_scopes': []}
        """

        if not confs:
            confs = self.DEFAULT
        else:
            confs = dict(self.DEFAULT.items() + confs.items())

        self.config = {self.CONFIG_ACCESS_LIFETIME: confs[self.CONFIG_ACCESS_LIFETIME],
                       self.CONFIG_REFRESH_LIFETIME: confs[self.CONFIG_REFRESH_LIFETIME],
                       self.CONFIG_CODE_LIFETIME: confs[self.CONFIG_CODE_LIFETIME],
                       self.CONFIG_WWW_REALM: confs[self.CONFIG_WWW_REALM],
                       self.CONFIG_TOKEN_TYPE: confs[self.CONFIG_TOKEN_TYPE],
                       self.CONFIG_ENFORCE_INPUT_REDIRECT: confs[self.CONFIG_ENFORCE_INPUT_REDIRECT],
                       self.CONFIG_ENFORCE_STATE: confs[self.CONFIG_ENFORCE_STATE],
                       self.CONFIG_SUPPORTED_SCOPES: confs[self.CONFIG_SUPPORTED_SCOPES]}

        self.storage = storage

    def grant_access_token(self, input_data):
        """Checks if the parameters given are correct and if they match with
        the data stored on the database. After that, generates the access and
        refresh tokens. It takes one argument:
        * A dictionary (GET or POST) with the parameters. Example:
        code = abcd -> input_data['code'] == 'abcd'
        """

        # Checks the "code" parameter
        code = input_data['code']
        client_id = input_data['client_id']
        if not code:
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['invalid_code'],
                                        'Missing parameter. "code" is required.')
                                        
                    
        if not self.storage.exists_code(code):
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['invalid_code'],
                                        'Invalid "code".')
                                        
        # Checks the "client_id" parameter
        if not client_id:
            raise OAuth2ServerExeption(self.HTTP_RESPONSE['bad_request'],
                                       self.ERROR['invalid_client'],
                                       'Missing parameter. "client_id" is required.')
                                       
        if not self.storage.exists_client(client_id):
            raise OAuth2ServerExeption(self.HTTP_RESPONSE['bad_request'],
                                       self.ERROR['invalid_client'],
                                       'Invalid "client_id" parameter.')
                                       
                                       
        # Valid code?!
        if not self.storage.valid_code(client_id, code):
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['invalid_code'],
                                        'The "code" provided has expired')

                                       
                                       
        # Checks the "grant_type" parameter
        if not input_data['grant_type']:
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['invalid_grant'],
                                        'Missing parameter. "grant_type" is required.')


        # Checks client application credentials
        client = self.storage.get_client_credentials(client_id)
        client_secret = input_data['client_secret']
        if not client_secret or client_secret != client['client_secret']:
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['invalid_client'],
                                        'Invalid "client_secret" parameter.')

        redirect_uri = input_data['redirect_uri']
        print redirect_uri, client['redirect_uri']
        if not redirect_uri or redirect_uri != client['redirect_uri']:
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['redirect_uri_mismatch'],
                                        'Invalid or mismatch redirect URI.')

        # Generates the access and tokens
        user_id = self.storage.get_user_id(client_id, code)
        if input_data['grant_type'] == self.GRANT_TYPE['auth_code']:
            access_token, refresh_token, expires_in = self.storage.add_access_token(client_id, 
                user_id, self.config[self.CONFIG_ACCESS_LIFETIME], None,
                self.config[self.CONFIG_REFRESH_LIFETIME])
                
        elif input_data['grant_type'] == self.GRANT_TYPE['refresh_token']:
            if not input_data['refresh_token']:
                 raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                             self.ERROR['invalid_refresh'],
                                             'Missing parameter. "refresh_token" is required')
            
            refresh_token = self.storage.get_refresh_token(input_data['refresh_token'])
            
            if not refresh_token:
                raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                            self.ERROR['invalid_refresh'],
                                            'Invalid "refresh_token".')
                                            
            if self.storage.expired_refresh_token(refresh_token):
                raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                            self.ERROR['expired_refresh'],
                                            'This "refresh_token" has expired.')
                                            
            access_token, refresh_token, expires_in = self.storage.refresh_access_token(client_id,
                                                client['client_secret'],
                                                refresh_token)
        else: # TODO: Support other grant_types
            raise OAuth2ServerException(self.HTTP_RESPONSE['bad_request'],
                                        self.ERROR['unsupported_grant'],
                                        'The grant type given is not supported.')
        
        # Removes the temporary code from the database
        self.storage.remove_code(code)

        return access_token, refresh_token, expires_in


    def validate_authorize_params(self, input_data):
        """Validates the authorize parameters given (usually) by GET"""

        client_id = input_data['client_id']
        response_type = input_data['response_type']
        state = input_data['state']
        scope = input_data['scope']
        redirect_uri = input_data['redirect_uri']
        token_type = self.config[self.CONFIG_TOKEN_TYPE]
        realm = self.config[self.CONFIG_WWW_REALM]
        stored_client = self.storage.get_client_credentials(client_id)
        
        # Checks if the they were passed any parameters
        if not input_data:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['bad_request'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_request'],
                                              'Necessary parameters haven\'t been passed in.',
                                              scope)
        
        # Checks redirect_uri parameter
        if not redirect_uri or not stored_client['redirect_uri'] or redirect_uri != stored_client['redirect_uri']:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['unauthorized_client'],
                                              token_type,
                                              realm,
                                              self.ERROR['redirect_uri_mismatch'],
                                              'Redirect URI does not match.',
                                              scope)

        # Checks client_id parameter
        if not client_id:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['unauthorized_client'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_client'],
                                              'Missing parameters. "client_id" is required.',
                                              scope)
        
        # Checks the stored client details
        if not stored_client:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['unauthorized_client'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_client'],
                                              'Invalid "client_id".',
                                              scope)
                                              
        
        # Checks the response type parameter
        if not response_type:
            raise OAuth2RedirectException(redirect_uri,
                                          self.ERROR['invalid_request'],
                                          'Missing parameters. "response_type" is required.')

        #TODO: Support other response types
        if response_type != self.RESPONSE_TYPE_AUTH_CODE:
            raise OAuth2RedirectException(redirect_uri,
                                          self.ERROR['unsupported_response_type'],
                                          'Response type not supported.')

        # Checks the scope parameter
        if scope and not self.check_scope(scope, self.config[self.CONFIG_SUPPORTED_SCOPES]):
            raise OAuth2RedirectException(redirect_uri,
                                          self.ERROR['invalid_scope'],
                                          'An unsupported scope was requested.')

        # Checks the state parameter
        if not state and self.config[self.CONFIG_ENFORCE_STATE]:
            raise OAuth2RedirectException(redirect_uri,
                                          self.ERROR['invalid_request'],
                                          'The state parameter is required.')

        return input_data
        
    def validate_access_params(self, get_data, post_data, header):
    
        token_type = self.config[self.CONFIG_TOKEN_TYPE]
        realm = self.config[self.CONFIG_WWW_REALM]
        methods = 0
        token = ''
        
        if header:
            bearer, token = header.split(' ')
        
            if not bearer or not token:
                raise OAuth2AuthenticateException(self.HTTP_RESPONSE['bad_request'],
                                                  token_type,
                                                  realm,
                                                  self.ERROR['invalid_request'],
                                                  'Malformed auth header')
                                                  
            if bearer != self.TOKEN_BEARER_HEADER_NAME:
                raise OAuth2AuthenticateException(self.HTTP_RESPONSE['bad_request'],
                                                  token_type,
                                                  realm,
                                                  self.ERROR['invalid_request'],
                                                  'Only "Bearer" token type is allowed')
        
            methods += 1

        try:
            if get_data[self.TOKEN_PARAM_NAME]:
                token = get_data[self.TOKEN_PARAM_NAME]
                methods += 1
        except:
            pass # Do we want a `pass` here?
        
        try:
            if post_data[self.TOKEN_PARAM_NAME]:
                token = post_data[self.TOKEN_PARAM_NAME]
                methods += 1
        except:
            pass # Do we want a `pass` here?
            
        if methods > 1:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['bad_request'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_request'],
                                              'Only one method may be used to authenticate at a time (Auth header, GET or POST).')
        elif not methods:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['bad_request'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_request'],
                                              'The access token was not found.')

        token = self.storage.get_access_token(token)

        if not token:
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['unauthorized'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_grant'],
                                              'Invalid access token.')
            
        elif self.storage.expired_access_token(token):
            raise OAuth2AuthenticateException(self.HTTP_RESPONSE['unauthorized'],
                                              token_type,
                                              realm,
                                              self.ERROR['invalid_grant'],
                                              'The access token provided has expired.')
                                              
        return token['access_token']

