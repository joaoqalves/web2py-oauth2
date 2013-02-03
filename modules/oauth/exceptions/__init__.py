'''
   This file is no longer needed... as I now am using the gluon.http.HTTP (web2py) exception class
'''

# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# # Copyright 2012 João Alves <joaoqalves@gmail.com> and Tiago Pereira
# # <tiagomiguelmoreirapereira@gmail.com>

# # Permission is hereby granted, free of charge, to any person obtaining
# # a copy of this software and associated documentation files (the
# # "Software"), to deal in the Software without restriction, including
# # without limitation the rights to use, copy, modify, merge, publish,
# # distribute, sublicense, and/or sell copies of the Software, and to
# # permit persons to whom the Software is furnished to do so, subject to
# # the following conditions:

# # The above copyright notice and this permission notice shall be
# # included in all copies or substantial portions of the Software.

# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# # NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# # LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# # WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# class OAuth2AuthenticateException(Exception):
#     """Send an error header with the given realm and error, if provided.
#     Suitable for bearer token type. It takes 6 arguments:
#     * The HTTP status code message as predefined
#     * The token type
#     * The realm provided
#     * The error code
#     * A human readable error message, with additional information
#     * [OPTIONAL] Required if the "scope" parameter was present in the client
#       authorization request
#     """
    
#     def __init__(self, http_response, token_type,
#                  realm, error, msg, scope=None):
#         self.http_response = http_response
#         self.token_type = token_type
#         self.realm = realm
#         self.error = error
#         self.msg = msg
#         self.scope = scope or 'No scope provided'
    
#     def __str__(self):
#         return "".join([self.http_response, ' | ', self.token_type, ' | ',
#                         self.realm, ' | ', self.error, ' | ', self.msg,
#                         ' | ', self.scope])
#         # Previous [concat.] method was too slow, see my benchmarks: http://stackoverflow.com/a/14610440/587021

# class OAuth2RedirectException(Exception):
#     """Redirect the end-user's user agent with error message. It takes 3 
#     arguments:
#     * An URI where the user should be redirect, after the authentication
#     * The error code
#     * A human readable error message, with additional information
#     * [OPTIONAL] Required if the "state" parameter was present in the client
#       authorization request
#     """
    
#     def __init__(self, redirect_uri, error, msg, state=None):
#         self.redirect_uri = redirect_uri
#         self.error = error
#         self.msg = msg
#         self.state = state or 'No state provided'
    
#     def __str__(self):
#         return "".join([self.redirect_uri, ' | ', self.error, ' | ',
#                         self.msg, ' | ', self.state])
#         # Previous [concat.] method was too slow, see my benchmarks: http://stackoverflow.com/a/14610440/587021
               
# class OAuth2ServerException(Exception):
#     """Server exception. Something is missing and the request could not be
#     performed. It takes 3 arguments:
#     * The HTTP status code message as predefined
#     * The error code
#     * A human readable error message, with additional information about
#     """
    
#     def __init__(self, http_response, error, msg):
#         self.http_response = http_response
#         self.error = error
#         self.msg = msg
    
#     def __str__(self):
#         return "".join([self.http_response, ' | ', self.error, ' | ', self.msg])
