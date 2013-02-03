#!/usr/bin/python
# -*- coding: utf-8 -*-

def index():
	"""Error page. It only shows an error message"""

	error = request.vars['msg']

	return locals()