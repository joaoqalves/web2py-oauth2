# -*- coding: utf-8 -*-

class OAuth2Exception(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return repr(self.msg)

class OAuth2:

    old_refresh_token = ""
    
    DEFAULT  = {'access_token_lifetime': 3600,
                'refresh_token_lifetime': 1209600,
                'auth_code_lifetime': 30,
                'www_realm': 'Service',
                'enforce_input_redirect': False,
                'enforce_state': False,
                'supported_scopes': {}}
                     
    CONFIG_ACCESS_LIFETIME = 'access_token_lifetime'
    CONFIG_REFRESH_LIFETIME = 'refresh_token_lifetime'
    CONFIG_AUTH_LIFETIME = 'auth_code_lifetime'
    CONFIG_SUPPORTED_SCOPES = 'supported_scopes'
    CONFIG_TOKEN_TYPE = 'token_type'
    CONFIG_WWW_REALM = 'realm'
    CONFIG_ENFORCE_INPUT_REDIRECT = 'enforce_redirect'
    CONFIG_ENFORCE_STATE = 'enforce_state'
    
    CLIENT_ID_REGEX = '/^[a-z0-9-_]{3,32}$/'
    
    TOKEN_PARAM_NAME = 'access_token'
    TOKEN_BEARER_HEADER_NAME = 'Bearer'
    
    RESPONSE_TYPE_AUTH_CODE = 'code'
    RESPONSE_TYPE_AUTH_TOKEN = 'token'
    
    GRANT_TYPE = {'auth_code': 'authorization_code',
                  'implicit': 'token',
                  'user_credentials': 'password',
                  'client_credentials': 'client_credentials',
                  'refresh_token': 'refresh_token',
                  'extensions': 'extensions'}
                  
    GRANT_TYPE_REGEX = '#^(authorization_code|token|password|client_credentials|refresh_token|http://.*)$#'
    
    TOKEN_TYPE = {'bearer': 'bearer', 'mac': 'mac'}
    
    HTTP_RESPONSE = {'found': '302 Found', 
                     'bad_request': '400 Bad Request',
                     'unauthorized': '401 Unauthorized',
                     'forbidden': '403 Forbidden',
                     'unavailable': '503 Service Unavailable'}
                                    
    ERROR = {'invalid_request': 'invalid_request',
             'invalid_client': 'invalid_client',
             'unauthorized_client': 'unauthorized_client',
             'redirect_uri_mismatch': 'redirect_uri_mismatch',
             'access_denied': 'access_denied',
             'unsupported_response_type': 'unsupported_response_type',
             'invalid_scope': 'invalid_scope',
             'invalid_grant': 'invalid_grant',
             'unsupported_grant_type': 'unsupported_grant_type',
             'insufficient_scope': 'invalid_scope'}
             
    def __init__(self, confs=None):
    
        if confs == None
            confs = DEFAULT
    
        self.config = {CONFIG_ACCESS_LIFETIME: confs[CONFIG_ACCESS_LIFETIME],
                       CONFIG_REFRESH_LIFETIME: confs[CONFIG_REFRESH_LIFETIME],
                       CONFIG_AUTH_LIFETIME: confs[CONFIG_AUTH_LIFETIME],
                       CONFIG_WWW_REALM: confs[CONFIG_WWW_REALM],
                       CONFIG_TOKEN_TYPE: TOKEN_PARAM_NAME,
                       CONFIG_ENFORCE_INPUT_REDIRECT: confs[ENFORCE_INPUT_REDIRECT],
                       CONFIG_ENFORCE_STATE: confs[ENFORCE_STATE],
                       CONFIG_SUPPORTED_SCOPES: confs[SUPPORTED_SCOPES]}
                       
    def verify_access_token(token_param, scope=None):
        token_type = self.config[CONFIG_TOKEN_TYPE]
        realm = self.config[CONFIG_WWW_REALM]
        
        if not token_param:
            raise OAuth2Exception(HTTP_RESPONSE['bad_request'],
                                  token_type, 
                                  realm,
                                  ERROR['invalid_request'],
                                  'The request is missing a required parameter.',
                                  scope)

def index():
    """
    Fixme
    """
    response.headers['Content-Type'] = json_headers()
    response.view = json_service()
    
