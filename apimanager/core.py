# -*- coding: utf-8 -*-

import pandas as pd
import requests
import json
import datetime
import logging
import time
import re
import urlparse
import urllib
import pytz

import numpy as np

import sys

import utils
# from .utils import format_batch_item
# from .utils import split_series_into_batches
# from .utils import batch_id_requests, extract_data_from_single_batch_response,
# error_checker, response_parser

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""

class RequestManager(object):

    def _hopper_initial_fill(self):
        if self._hopper_params:
            raw_params = {'access_token': self.access_token,}
            params = urllib.urlencode(raw_params)
        else:
            params = ""
        # @TODO - This handling params is hacky and needs to be changed.
        if "?" in self.url_base:
            params = str("&" + params)
        else:
            print False
            params = str("?" + params)

        if self.api_type == "stream":
            print "Params: {}".format(params)
            print "URL Base: {}".format(self.url_base)
            self.hopper += [str(self.url_base.format(_id) + params) 
            for _id in self.id_list]
        elif self.api_type == "single":
            print "single"
            self.hopper += [self.url_base.format(_id) + params 
            for _id in self.id_list]
        elif self.api_type == "batch":
            print "batch"
        else:
            raise Exception("Unknown api_type")

        logging.debug("Initial hopper fill complete")


    def manage_paging(self, response):
        return_url = False

        # FACEBOOK
        if "paging" in response:
            try:
                _latest_item_date = pd.to_datetime(response["data"][-1]["created_time"])
            except:
                _latest_item_date = None

            if _latest_item_date > pd.to_datetime(self.date_end):# and ps_counter < 5: 
                return_url = response["paging"]["next"]

        # INSTAGRAM
        elif "pagination" in response:
            try:
                _latest_item_date = pd.to_datetime(datetime.datetime.fromtimestamp(
                    float(response["data"][-1]["created_time"])))
            except:
                _latest_item_date = None
            if ("next_url" in response["pagination"]):
                if (_latest_item_date) and (_latest_item_date >= pd.to_datetime(self.date_end)):
                    logging.debug("Next URL valid and being added.")
                    return_url = response["pagination"]["next_url"]

        # Unknown API
        else:
            return_url = False
#            raise Exception("Unknown API type.")

        return return_url

    def __init__(self, ids, url_base, access_token, api_type, date_start=None, 
        date_end=None,hopper_params=True):
        
        # Check whether ids contains a string or list. 
        # If it's a string, create a list of one for consistency
        if isinstance(ids,str):
            self.id_list = [ids,]
            self.batch = False
        elif isinstance(ids,list):
            self.id_list = ids
            self.batch = True
        else:
            raise TypeError("IDs are not a valid list or string.")

        # Set the URL base provided in setup for this RequestManager instance

        self.url_base = None
        if isinstance(url_base, str):
            self.url_base = url_base
        else:
            raise TypeError("url_base provided is not a string")
        
        if date_start:
            self.date_start = date_start

        if date_end:
            self.date_end = date_end
        else:
            self.date_end = None

        self.access_token = access_token

        if api_type not in ["stream", "single", "batch",]:
            raise Exception("Invalid API type.")
        else:
            self.api_type = api_type

        self._hopper_params = hopper_params

        self.hopper = list()
        self._hopper_initial_fill()

    def run(self):
        # @TODO:
        # - Ability to return in different formats (raw, pandas, dict, etc)
        # - Better handling of OAuth and delays
        # - Start using "error_checker" like we had in the previous version below

        ''' 
        Handles running of the actual requests to get data. Initial hopper of 
        URLs to request is created at initialisation, based on the API type
        called and the options provided. This method makes the requests and 
        feeds them back. 

        The only complex thing it needs to do is to know when to stop. This is
        mainly based on a date range (especially for feeds) but other reasons
        could be added in future.
        '''
        if self.date_end:
            _date_end = pd.to_datetime(self.date_end)
        else:
            _date_end = datetime.datetime.now()
        _response_list = list()
        while self.hopper:
            logging.debug("Entering an iteration of the loop")
            _current_request = self.hopper.pop()
            # print _current_request

            _request_made = datetime.datetime.utcnow()
            _request_made = _request_made.replace(tzinfo=pytz.utc)
            print _request_made
            response = requests.get(_current_request)
            response.encoding = "latin-1"
            encoded = response.content#.encode("utf-8")
            _json_response = json.loads(encoded)
            _json_response["request_made"] = _request_made
            if response.status_code == 200 and not _json_response.get("error") and "data" in _json_response:
                # @TODO - this is very FB specific, so need to adapt later
                _individual_results = _json_response["data"]
                for counter, i in enumerate(_individual_results):
                    _individual_results[counter]["_request_made"] = _request_made
                _response_list += _individual_results
            elif response.status_code == 200 and not _json_response.get("error") and all(k in _json_response.keys() for k in ["created_time",]):
                # @FIXME - hack to get Facebook likes/comments/shares quickly
                _individual_results = _json_response
                for counter, i in enumerate(_individual_results):
                    _individual_results[counter]["_request_made"] = _request_made
                _response_list.append(_individual_results)
            elif response.status_code == 200 and _json_response.get("error"):
                _error_message = "Error: {msg}".format(msg=_json_item["error"]) 
                raise Exception(_error_message)

            ### NEED TO WORK TO INTEGRATE THIS CONCEPT
            # elif response.status_code == 400 and json.loads(
            #         _json_response["body"])["error"]["code"] == 613:
            #     delay_time = 120
            #     logging.info("API limit exceeded. Waiting for %s seconds" % (
            #         delay_time))
            #     time.sleep(delay_time)
            #     self.hopper.append(response.url)
            #     raise Exception(json.loads(response.content))
            elif response.status_code == 400:
                raise Exception(json.loads(response.content))
            else:
                # print _json_response
                # print response.status_code
                raise Exception("Unknown error")
            # CHECK FOR PAGING
            # Hacky hack to get Instagram working
            paging_check = self.manage_paging(_json_response)
            if paging_check:
                self.hopper.append(paging_check)

        return _response_list


    def old_run(self):
        _master_response_list = list()

        for _single_id in self.id_list:
            _string_url = str(self.url_base)
            _prepared_url = _string_url.format(page_id=_single_id,
                access_token=self.access_token)
            _created_datetime = datetime.now() # Start from now
            while _created_datetime > pd.to_datetime(self.date_end):
                response = requests.get(_prepared_url)
                logging.debug("Response successful")
                _response_check = error_checker(response)
                if _response_check == "VALID":
                    _response_dict = json.loads(response.content)
                    _master_response_list = _master_response_list + _response_dict["data"]
                    _created_datetime = pd.to_datetime(
                        _response_dict["data"][-1:][0]["created_time"])
                    _prepared_url = json.loads(response.content)["paging"]["next"]
                    logging.info("Successful response: {id} - {created_datetime} oldest".format(
                        id=_single_id, created_datetime=_created_datetime))
                elif _response_check == "VALID_EMPTY":
                    _created_datetime = pd.to_datetime(self.date_end)
                elif _response_check == "RATELIMIT":
                    _wait_seconds = 120
                    logging.info("Rate limit reached. Waiting for {seconds} seconds".format(
                        seconds=_wait_seconds))
                    time.wait(_wait_seconds)
                elif _response_check == "ERROR":
                    raise Exception("Unknown error check response.")
                else:
                    raise Exception("Unknown error check response.")
            else:
                logging.info("Loop finished for {id}".format(id=_single_id))
        return _master_response_list
