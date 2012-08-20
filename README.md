web2py-oauth2
=============

An OAuth 2.0 module for web2py framework, based in:

* [OAuth 2.0 draft 20](http://tools.ietf.org/html/draft-ietf-oauth-v2-20)
* [PHP OAuth 2 Server](https://github.com/quizlet/oauth2-php)
* [YouTube API v2.0](https://developers.google.com/youtube/2.0/developers_guide_protocol#Authentication)

Requirements
------------

* Python
* MongoDB
* PyMongo

I have tested with Python 2.7, MongoDB 2.0.7 and pymongo 2.2.1, but I guess
it should work properly with other versions.
NOTE: The OAuthStorage class is extensible, so you can work with DAL if you
implement it.

Using
------------

It's just like any other web2py application. Here are a few steps to test the
module:

* Add a client (`http://your_server[:port]/application/add_client`)
* Change the `client_id`, `client_secret` and `redirect_uri` at 
`controllers/callback.py` for the ones given by the above step
* Browse `http://your_server[:port]/application/auth` with the required parameters
and click "Yes"
* Get the `access_token` and `refresh_token`
* `curl -H "Authorization: Bearer access_token_here" http://your_server[:port]/application/protected_resource`

Contributing
------------

Want to contribute? Great! Just fork this project and/or make a pull request ;)

TODO
------------

* Implement subclasses of OAuthStorage for the web2py's Database Abstraction Layer
* Unit tests
* Improve the code and the comments

Note
------------

By default, the web2py-oauth2 module works with web2py framework and MongoDB but
is easy to adapt it to another frameworks and databases
