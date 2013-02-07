#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Samuel Marks <samuelmarks@gmail.com>
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

import datetime
from gluon import current
from bson.objectid import ObjectId

def add_seconds_to_date(date, seconds):
    return date + datetime.timedelta(0, seconds)

class OAuthStorage(object):
    """Storage interface in order to use the OAuth2 server. It's just an
    interface and you should extend it to your database engine.
    """

    SALT = 'TlG}LJV[nplC5^jZn+Z]TCal`)2[^(_h'
    # ^ Don't forget to change your SALT! ^

    @staticmethod 
    def generate_hash_512(length = 32, salt = True):
        """Generates a SHA512 random hash. It takes two arguments:
        * length (default: 32)
        * salt (default: True). You should change the salt used for the hash 
        """
        
        import os
        import hashlib
        import base64

        encode_str = base64.urlsafe_b64encode(os.urandom(length))
        m = hashlib.sha512()

        if salt:
            encode_str = self.SALT + encode_str
            
        m.update(encode_str)
        return m.hexdigest()

    @staticmethod
    def generate_hash_sha1(length = 32, salt = False):
        """Generates a SHA512 random hash. It takes two arguments:
        * length (default: 32)
        * salt (default: False). You should change the salt used for the hash 
        """
        
        import os
        import hashlib
        import base64

        encode_str = base64.urlsafe_b64encode(os.urandom(length))
        m = hashlib.sha1()

        if salt:
            encode_str = self.SALT + encode_str

        m.update(encode_str)
        return m.hexdigest()
        
    #defaults provided in child classes
    def __init__(self, **kwargs):
        """The Storage constructor takes 3 arguments:
        * The database server
        * The database server port
        * The database name
        """
        
        self.server  = kwargs.get('server', None)
        self.port    = kwargs.get('port', None)
        self.db_name = kwargs.get('db_name', None)

#'cause DALStorage looks weird :P
class web2pyStorage(OAuthStorage):
    """Adapter for the DAL (Database Abstraction Layer) created for the web2py framework.
       - Usable with a variety of databases (including GAE, MongoDB and PostgreSQL)
       - Can be imported into other frameworks (official 'support' for Flask, pyramid &etc....
         see: https://github.com/mdipierro/gluino for further info)
    """

    tables_created = False

    def create_tables(self):
        if self.tables_created:
            return
        
        from gluon.tools import Field
        from gluon.validators import IS_URL

        # Note that (by default): an 'id' primary key is associated with every table.        
        self.db.define_table('clients',
            Field('client_id'), # pid
            Field('client_secret'),
            Field('redirect_uri', requires=IS_URL(allowed_schemes=['http','https'])),
            Field('client_name')
        )

        self.db.define_table('codes',
            Field('code_id'), # pid
            Field('client_id', 'reference clients'),
            Field('user_id'),
            Field('expires_access', 'datetime'),
            Field('expires_refresh', 'datetime'),
            Field('the_scope'), # 'scope' is a reserved SQL keyword
            Field('access_token')
        )
        
        self.db.define_table('tokens',
            Field('refresh_token'), # pid
            Field('client_id'),
            Field('user_id'),
            Field('expires_access'),
            Field('expires_refresh'),
            Field('the_scope'),
            Field('access_token')
        )

        self.tables_created = True


    def connect(self):
        # Syntax: "dbtype://username:password@host:port/dbname"
        # The /dbname syntax doesn't seem to work with SQLite...
        
        from gluon.tools import DAL
        print 'self.db_name =', self.db_name

        if self.server == self.port == self.db_name == None:
            self.server = 'sqlite://oauth.sqlite'
        
        conn = self.server if not self.port else self.server + self.port

        self.db = DAL(conn, pool_size=1, check_reserved=['all'])

    def add_client(self, client_name, redirect_uri):
        """Adds a client application to the database, with its client name and
        redirect URI. It returns the generated client_id and client_secret
        """
        
        try:
            self.db.clients
        except AttributeError:
            self.create_tables()
        
        client_id = self.generate_hash_sha1()
        client_secret = self.generate_hash_sha1()
        
        self.db.clients.insert(**{'client_id': client_id,
                                  'client_secret': client_secret,
                                  'redirect_uri': redirect_uri,
                                  'client_name': client_name})

        return client_id, client_secret

    def get_client_credentials(self, client_id):
        """Gets the client credentials by the client application ID given."""
        
        try:
            return self.db.clients(client_id)
        except AttributeError:
            self.create_tables()
            return None

    def exists_client(self, client_id):
        """Checks if a client exists, given its client_id"""
        
        return self.get_client_credentials(client_id) != None

    def add_code(self, client_id, user_id, lifetime):
        """Adds a temporary authorization code to the database. It takes 3
        arguments:
        * The client application ID
        * The user ID who wants to authenticate
        * The lifetime of the temporary code
        It returns the generated code
        """

        expires = add_seconds_to_date(datetime.datetime.now(), lifetime)

        # do -> while FTW
        code = self.generate_hash_sha1()
        while self.get_refresh_token(code):
            code = self.generate_hash_sha1()

        self.db.codes(self.db.codes.code_id==code).update(**{'client_id': client_id,
                                                            'user_id': user_id,
                                                            'expires': expires})

        return code

    def valid_code(self, client_id, code):
        """Validates if a code is (still) a valid one. It takes two arguments:
        * The client application ID
        * The temporary code given by the application
        It returns True if the code is valid. Otherwise, False
        """
        
        try:
            data = self.db.codes(self.db.codes.code_id==code).select(self.db.expires_access).first()
        except AttributeError:
            self.create_tables()
            return False

        if data:
            return datetime.datetime.now() < data.expires_access

        return False

    def exists_code(self, code):
        """Checks if a given code exists on the database or not"""

        try:
            self.db.codes(self.db.codes.code_id==code).select().first() != None
        except AttributeError:
            self.create_tables()
            return False

    def remove_code(self, code):
        """Removes a temporary code from the database"""
        
        self.db.codes(self.db.codes.code_id==code).select().first().delete()

    def get_user_id(self, client_id, code):
        """Gets the user ID, given a client application ID and a temporary
        authentication code
        """
        try:
            return self.db.codes(self.db.codes.code_id==code).select(self.db.codes.user_id).first()
        except AttributeError:
            self.create_tables()
            return None

    def expired_access_token(self, token):
        """Checks if the access token remains valid or if it has expired"""
        
        return token['expires_access'] < datetime.datetime.now()

    def expired_refresh_token(self, token):
        """Checks if the refresh token remains valid or if it has expired"""
        
        return token['expires_refresh'] < datetime.datetime.now()

    def add_access_token(self, client_id, user_id, access_lifetime,
                         refresh_token = None, refresh_lifetime = None,
                         expires_refresh = None, the_scope = None):
        """Generates an access token and adds it to the database. If the refresh
        token does not exist, it will create one. The method takes 6 arguments:
        * The client application ID
        * The user ID
        * The access token lifetime
        * [OPTIONAL] The refresh token
        * [OPTIONAL] The refresh token lifetime
        * [OPTIONAL] The the_scope of the access
        """
        
        now = datetime.datetime.now()

        # do -> while FTW
        access_token = self.generate_hash_512()
        while self.get_access_token(access_token):
            access_token = self.generate_hash_512()

        expires_access = add_seconds_to_date(now, access_lifetime)

        # It guarantees uniqueness. Better way?
        if not refresh_token:
            # do -> while FTW
            refresh_token = self.generate_hash_512()
            while self.get_refresh_token(refresh_token):
                refresh_token = self.generate_hash_512()

            expires_refresh = add_seconds_to_date(now, refresh_lifetime)

        self.db.tokens.update_or_insert(**{'refresh_token': referesh_token,
                                           'client_id': client_id,
                                           'user_id': user_id,
                                           'expires_access': expires_access,
                                           'expires_refresh': expires_refresh,
                                           'the_scope': the_scope,
                                           'access_token': access_token})

        return access_token, refresh_token, expires_access

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        """Updates an access token, given the refresh token.
        The method takes 3 arguments:
        * The client application ID
        * The client application secret ID
        * The refresh token
        """

        now = datetime.datetime.now()
        credentials = self.get_client_credentials(client_id)
        old_token = self.db.tokens.update_or_insert({'refresh_token': refresh_token,
                                                     'client_id': client_id})

        if old_token and expired_refresh_token(old_token, now) and credentials['client_secret'] == client_secret:
            return self.add_access_token(client_id,
                                         old_token['user_id'],
                                         self.config[self.CONFIG_ACCESS_LIFETIME],
                                         old_token['refresh_token'],
                                         self.config[self.CONFIG_REFRESH_LIFETIME],
                                         old_token['expires_refresh'],
                                         old_token['the_scope'])
        return (False,)*3
        
    def get_access_token(self, access_token):
        """Returns the token data, if the access token exists"""

        try:
            return self.db(self.db.tokens.access_token==access_token).select().first()
        except AttributeError:
            self.create_tables()
            return None

    def get_refresh_token(self, refresh_token):
        """Returns the token data, if the refresh token exists"""
    
        try:
            return self.db.tokens(self.db.tokens.refresh_token==refresh_token).select().first() # 'code' == 'refresh_token', right? [pid that is]
        except AttributeError:
            self.create_tables()
            return None


class MongoStorage(OAuthStorage):
    """A MongoDB adapter for the Storage super-class.
       - It uses pymongo and a cache abstraction wrapper from gluon (web2py) """

    import pymongo
    
    def connect(self):
        """Connects to the database with the credentials provided in the
        constructor
        """
        
        if self.server == self.port == self.db_name == None:
            server='localhost'; port=27017; db_name='oauth'

        self.conn = pymongo.Connection(self.server, self.port)
        self.db = current.cache.ram('mongodb', lambda: self.conn[self.db_name], None)
        #^ CHANGE ME if you do not use web2py


    def add_client(self, client_name, redirect_uri):
        """Adds a client application to the database, with its client name and
        redirect URI. It returns the generated client_id and client_secret
        """
        
        client_id = MongoStorage.generate_hash_sha1()
        client_secret = MongoStorage.generate_hash_sha1()

        self.db.clients.save({'_id': client_id,
                              'client_secret': client_secret,
                              'redirect_uri': redirect_uri,
                              'client_name': client_name})

        return client_id, client_secret
        
    def exists_client(self, client_id):
        """Checks if a client exists, given its client_id"""
        
        return self.db.clients.find({'_id': client_id}) != None

    def get_client_credentials(self, client_id):
        """Gets the client credentials by the client application ID given."""
        
        return self.db.clients.find_one({'_id': client_id})

    def add_code(self, client_id, user_id, lifetime):
        """Adds a temporary authorization code to the database. It takes 3
        arguments:
        * The client application ID
        * The user ID who wants to authenticate
        * The lifetime of the temporary code
        It returns the generated code
        """
        
        user_id = ObjectId(user_id)
        expires = add_seconds_to_date(datetime.datetime.now(), lifetime)

        # do -> while FTW
        code = OAuthStorage.generate_hash_sha1()
        while self.get_refresh_token(code):
            code = OAuthStorage.generate_hash_sha1()

        self.db.codes.save({'_id': code,
                            'client_id': client_id,
                            'user_id': user_id, 
                            'expires': expires})

        return code

    def valid_code(self, client_id, code):
        """Validates if a code is (still) a valid one. It takes two arguments:
        * The client application ID
        * The temporary code given by the application
        It returns True if the code is valid. Otherwise, False
        """
        
        data = self.db.codes.find_one({'_id': code,
                                       'client_id': client_id})
        if data:
            return datetime.datetime.now() < data['expires']

        return False

    def exists_code(self, code):
        """Checks if a given code exists on the database or not"""
        
        return self.db.codes.find_one({'_id': code}) != None

    def remove_code(self, code):
        """Removes a temporary code from the database"""

        self.db.codes.remove({'_id': code})

    def get_user_id(self, client_id, code):
        """Gets the user ID, given a client application ID and a temporary
        authentication code
        """
        
        return self.db.codes.find_one({'_id': code, 'client_id': client_id}
                                      )['user_id']

    def expired_access_token(self, token):
        """Checks if the access token remains valid or if it has expired"""
        
        return token['expires_access'] < datetime.datetime.now()

    def expired_refresh_token(self, token):
        """Checks if the refresh token remains valid or if it has expired"""
        
        return token['expires_refresh'] < datetime.datetime.now()

    def add_access_token(self, client_id, user_id, access_lifetime,
                         refresh_token = None, refresh_lifetime = None,
                         expires_refresh = None, the_scope = None):
        """Generates an access token and adds it to the database. If the refresh
        token does not exist, it will create one. The method takes 6 arguments:
        * The client application ID
        * The user ID
        * The access token lifetime
        * [OPTIONAL] The refresh token
        * [OPTIONAL] The refresh token lifetime
        * [OPTIONAL] The the_scope of the access
        """
        
        now = datetime.datetime.now()

        # do -> while FTW
        access_token = MongoStorage.generate_hash_512()
        while self.get_access_token(access_token):
            access_token = MongoStorage.generate_hash_512()

        expires_access = add_seconds_to_date(now, access_lifetime)

        # It guarantees uniqueness. Better way?
        if not refresh_token:
            # do -> while FTW
            refresh_token = MongoStorage.generate_hash_512()
            while self.get_refresh_token(refresh_token):
                refresh_token = MongoStorage.generate_hash_512()
            
            expires_refresh = add_seconds_to_date(now, refresh_lifetime)

        self.db.tokens.save({'_id': refresh_token,
                             'client_id': client_id,
                             'user_id': user_id,
                             'expires_access': expires_access,
                             'expires_refresh': expires_refresh,
                             'the_scope': the_scope,
                             'access_token': access_token})

        return access_token, refresh_token, expires_access

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        """Updates an access token, given the refresh token.
        The method takes 3 arguments:
        * The client application ID
        * The client application secret ID
        * The refresh token
        """

        now = datetime.datetime.now()
        credentials = get_client_credentials(client_id)
        old_token = self.db.tokens.find_one({'_id': refresh_token,
                                             'client_id': client_id})

        if old_token and expired_refresh_token(old_token, now) and credentials['client_secret'] == client_secret:
            return self.add_access_token(client_id,
                                         old_token['user_id'],
                                         self.config[self.CONFIG_ACCESS_LIFETIME],
                                         old_token['refresh_token'],
                                         self.config[self.CONFIG_REFRESH_LIFETIME],
                                         old_token['expires_refresh'],
                                         old_token['the_scope'])
        return (False,)*3
        
    def get_access_token(self, access_token):
        """Returns the token data, if the access token exists"""
        return self.db.tokens.find_one({'access_token': access_token})
        
    def get_refresh_token(self, refresh_token):
        """Returns the token data, if the refresh token exists"""
    
        return self.db.tokens.find_one({'_id': refresh_token})
