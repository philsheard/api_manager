# -*- coding: utf-8 -*-

from .core import RequestManager

def create_manager():
	'''Facebook API interfaces'''

	manager = RequestManager()

	return manager

def page_posts(ids, access_token, date_start=None, date_end=None,):

	url_base = "https://graph.facebook.com/v2.2/{page_id}/feed?access_token={access_token}"

	# if isinstance(ids,str):
	# 	list_of_ids = [ids,]
	# 	print list_of_ids
	# elif isinstance(ids,list):
	# 	pass # Already a list, move along
	# else:
	# 	raise TypeError("IDs are not a valid list or string.")

	manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
		date_start=date_start, date_end=date_end)

	return manager
