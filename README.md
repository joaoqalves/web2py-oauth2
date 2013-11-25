web2py-oauth2
=============

An OAuth 2.0 module for web2py framework, based in:
* [OAuth 2.0 draft 20](http://tools.ietf.org/html/draft-ietf-oauth-v2-20)
* [PHP OAuth 2 Server](https://github.com/quizlet/oauth2-php)
* [YouTube API v2.0](https://developers.google.com/youtube/2.0/developers_guide_protocol#Authentication)

Requirements
------------

* Python

Using
------------

From `web2py\applications`, clone the app `git clone https://github.com/SamuelMarks/web2py-oauth2.git oauth2`

Then follow these steps to test the module:

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

* Unit tests
* Upgrade from Draft 20 to released OAuth2 standards

NOTE
------------

This code was originally written by [João Alves](http://joaoqalves.net/) and [Tiago Pereira](http://fe.up.pt/~ei08023/curriculum)
and after that was changed by [Samuel Marks](http://github.com/SamuelMarks)

The major changes that Samuel did in the code can be summarised in three points:

1. Reviewed the entire codebase; improving quality, fixing hacks and improving formatting along the way.
2. Rewrote all the relevant exceptions to use gluon.http.HTTP (with correct HTTP error codes + easier to understand specific exception messages)
3. Implemented subclasses of OAuthStorage for web2py's DAL. Now this project is no longer locked-into MongoDB ;]
