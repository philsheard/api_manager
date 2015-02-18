# -*- coding: utf-8 -*-

#import pandas as pd
import requests

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""

class RequestManager(object):

	def __init__(self, ids, url_base, access_token, date_start=None, date_end=None):
		

		if isinstance(ids,str):
			self.id_list = [ids,]
			self.batch = False
		elif isinstance(ids,list):
			self.id_list = ids
			self.batch = True
		else:
			raise TypeError("IDs are not a valid list or string.")

		# Set the URL base provided in setup for this RequestManager instance
		self.url_base = url_base

		if date_start:
			self.date_start = date_start

		if date_end:
			self.date_end = date_end

		self.access_token = access_token

	def start(self):
		for single_id in self.id_list:
			string_url = str(self.url_base)
			prepared_url = string_url.format(page_id=single_id, access_token=self.access_token)
			response = requests.get(prepared_url)
		return response#.text#["data"]#[-1]

	# def stream(self):
	# 	pass

	# def collect(self):
	# 	pass