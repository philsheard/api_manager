# -*- coding: utf-8 -*-

from .core import RequestManager

def create_manager():
	'''Facebook API interfaces'''

	manager = RequestManager()

	return manager

def page_posts(pages):

	url_base = "https://graph.facebook.com/"

	manager = RequestManager(pages, url_base)

	return manager

	pass
