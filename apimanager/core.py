# -*- coding: utf-8 -*-

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""

class RequestManager(object):

	def __init__(self, pages, url_base, until=None):
		
		# Check whether pages variable is a list, or a single page
		if isinstance(pages,list):
			self._batch = True
		elif isinstance(pages,str):
			self._batch = False
		else:
			raise Exception("Missing page posts")

		# Set the URL base provided in setup for this RequestManager instance
		self.url_base = url_base

		if until:
			self.until = until

	def stream():
		pass