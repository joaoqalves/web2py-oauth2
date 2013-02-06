#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
    """
    This method has two functionalities:
    1. Asks the user if he permits that a 3rd party app access his data
    2. Receives the user's answer and redirect the user to the 3rd party
       correspondant URI
    In case of error, it redirects to the 'error' controller. 
    Of course, you can modify this behavior. For instance, you may want return
    a JSON or HTTP error instead.
    
    The request MUST be like this:
    http://[your_server]{:port}/[your_application]/auth?
    client_id=[your_client_id]&
    redirect_uri=[your_callback_uri]&
    response_type=code&
    access_type=online
    NOTE: You can pass a "the_scope" parameter, but you need to configure it at the
    OAuth2 object constructor.
    """
    
    from oauth.storage import web2pyStorage as storage # change to MongoStorage if you aren't using DAL
    storage = storage()
    storage.connect()
    oauth = OAuth2(storage)
    
    # Validates GET parameters
    params = dict()
    success = False
    try:
        params = oauth.validate_authorize_params(request.get_vars)
    except Exception as ex:
        redirect(URL(c='error', vars=dict(msg=(ex.msg or ex))))

    #POST request. Yes/No answer
    print 'dir(request) =', str(request)
    if request.post_vars:
        success = True
        
        # Access given by the user?
        if request.post_vars['accept'] == 'Yes':
            user_id ='501faa19a34feb05890005c9' # Change it. Get it from your DB
            code = oauth.storage.add_code(request.post_vars['client_id'], 
                                          user_id,
                                          oauth.config[oauth.CONFIG_CODE_LIFETIME])
            redirect(request.get_vars['redirect_uri']+'?code='+code)
        else:
            redirect(request.get_vars['redirect_uri']+'#error=access_denied')

    # Builds the response URL
    url = ''
    try:
        client_id = params['client_id']
        redirect_uri = params['redirect_uri']
        the_scope = params['the_scope']
        response_type = params['response_type']
        access_type = params['access_type']

        url = '?' + 'client_id=' + client_id \
                  + '&redirect_uri=' + redirect_uri + '&response_type=' \
                  + response_type + '&access_type=' + access_type
        print 'url =', url
    except Exception as ex:
        redirect(URL(c='error', vars=dict(msg=(ex.msg or ex)))

    return locals()

