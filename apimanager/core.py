# -*- coding: utf-8 -*-

import pandas as pd
import requests
import json
import datetime

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""

class RequestManager(object):

	def __init__(self, ids, url_base, access_token, date_start=None, date_end=None):
		
		# Check whether ids contains a string or list. If it's a string, create a list of one for consistency
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

	def run(self):
		for single_id in self.id_list:
			string_url = str(self.url_base)
			prepared_url = string_url.format(page_id=single_id, access_token=self.access_token)
			response = requests.get(prepared_url)
			first_response_as_dict = json.loads(response.content)
			created_datetime = pd.to_datetime(first_response_as_dict["data"][-1:][0]["created_time"])
			responses = list(first_response_as_dict["data"])
			while created_datetime > pd.to_datetime(self.date_end):
				next_url = json.loads(response.content)["paging"]["next"]
				response = requests.get(next_url)
				response_loop_as_dict = json.loads(response.content)
				if response_loop_as_dict.get("data",None):
					# Check whether the response has "data" records
					responses = responses + response_loop_as_dict["data"]
					created_datetime = pd.to_datetime(response_loop_as_dict["data"][-1:][0]["created_time"])
				else:
					# Provide a condition for the loop to end gracefully
					created_datetime = pd.to_datetime(self.date_end)
		return responses

	# def stream(self):
	# 	pass

	# def collect(self):
	# 	pass