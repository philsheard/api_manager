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
        params = {'access_token': self.access_token,}
        if self.api_type == "stream":
            self.hopper += [self.url_base.format(_id) + "?" + urllib.urlencode(params) 
            for _id in self.id_list]
        elif self.api_type == "single":
            print "single"
        elif self.api_type == "batch":
            print "batch"
        else:
            raise Exception("Unknown api_type")

        logging.debug("Initial hopper fill complete")


    def __init__(self, ids, url_base, access_token, api_type, date_start=None, 
        date_end=None,):
        
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

        self.hopper = list()
        self._hopper_initial_fill()

    def run_test(self):

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
        ps_counter = 0

        while self.hopper:
            ps_counter += 1
            logging.debug("Entering an iteration of the loop")
            _current_request = self.hopper.pop()
            # print _current_request
            response = requests.get(_current_request)
            encoded = response.content.encode("utf-8")
            print encoded
            _json_response = json.loads(encoded)

            latest_response = _json_response

            if response.status_code == 200 and not _json_response.get("error"):
                # @TODO - this is very FB specific, so need to adapt later
                _response_list += _json_response["data"]
            elif response.status_code == 200 and _json_response.get("error"):
                _error_message = "Error: {msg}".format(msg=_json_item["error"]) 
                raise Exception(_error_message)
            elif response.status_code == 400:
                raise Exception(json.loads(response.content))
            else:
                print _json_response
                print response.status_code
                raise Exception("Unknown error")

            # CHECK FOR PAGING
            _latest_item_date = pd.to_datetime(_json_response["data"][-1]["created_time"])
            # print _latest_item_date > _date_end
            if _json_response.get("paging") and _latest_item_date > _date_end:# and ps_counter < 5: 
                self.hopper.append(_json_response["paging"]["next"])

        return _response_list, pd.DataFrame(_response_list), latest_response


    def run(self):
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

    def batch_run(self, return_format="raw"):

        list_of_responses = list()
        OK_to_proceed = False

        args = {'access_token':self.access_token,
            'batch':json.dumps(batch_id_requests(self.id_list)),
            'include_headers':'false',}
        request_baseurl = "https://graph.facebook.com/"
        while OK_to_proceed == False:
            response = requests.post(request_baseurl, params=args)
            try:
                last_response = json.loads(response.content.encode("utf-8"))[-1]#["body"]
                if last_response["code"] == 200:
                    logging.debug("Loop passed")
                    OK_to_proceed = True
                elif last_response["code"] == 400:
                    if json.loads(last_response["body"])["error"]["code"] == 613:
                        delay_time = 120
                        logging.info("API limit exceeded. Waiting for %s seconds" % (
                            delay_time))
                        time.sleep(delay_time)
                    else:
                        logging.warn("Unknown error - last response:\n{last_response}".format(
                            last_response=last_response))
                        raise Exception("Unknown error code.")
                else:
                    logging.warn("Unknown error - last response:\n{last_response}".format(
                        last_response=last_response))
                    raise Exception("Unknown error code.")
            except:
                logging.warn("Unknown error - sys error:\n{sys_error}".format(
                    sys_error=sys.exc_info()[0]))
                raise Exception("Unknown error code.")
            # list_of_responses.append(response)
        response_tidy = json.loads(response.content.encode("utf-8"))
        if return_format == "pandas":
            output_series = pd.Series(response_tidy)
            final_output = output_series.apply(lambda x: extract_data_from_single_batch_response(x,
                as_type="series"))
        elif return_format == "raw":
            final_output = response_tidy
        else:
            raise Exception("Unknown return_format supplied.")
        return final_output

    # def stream(self):
    #     pass

    # def collect(self):
    #     pass
