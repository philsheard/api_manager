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

from .utils import split_series_into_batches, batch_id_requests, extract_data_from_single_batch_response, error_checker

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

        self.url_base = None
        if url_base:
            self.url_base = url_base
        else:
            self.url_base = "Wowser."
        
        if date_start:
            self.date_start = date_start

        if date_end:
            self.date_end = date_end

        self.access_token = access_token

    def run_test(self):
        _arg_list = None
        _id_arg_list = [(_id_list_item,None) for _id_list_item in self.id_list]
        print _id_arg_list
        _batch_requests = json.dumps(batch_id_requests(_id_arg_list, self.url_base,))
        _response_list = list()

        _continue = True

        ps_counter = 0
        logging.debug("Initial setup completed")
        while _continue == True and ps_counter < 2:
            ps_counter = ps_counter + 1
            args = {'access_token':self.access_token,
                'batch':_batch_requests,
                'include_headers':'false',}
            request_baseurl = "https://graph.facebook.com/"
            response = requests.post(request_baseurl, params=args)
            json_response = json.loads(response.content)
            _arg_list = list()

            _id_arg_list = list()


            for count, item in enumerate(json_response):
                _r_code = item["code"]
                _r_body = json.loads(item["body"])

                if _r_code == 200:
                    logging.info("Status code {code}".format(code=_r_code))

                    if "paging" in _r_body:
                        _paging = _r_body["paging"]


            ### NEED TO ADD:
            ### - CHECK FOR END DATES
            ### - HANDLING FOR OAUTH


                        if _paging.get("next",False):
                            logging.debug("Paging 'next' exists")
                            _query_str = urlparse.urlparse(_paging["next"]).query
                            _query_args = urlparse.parse_qsl(_query_str)
                            _new_args = dict()

                            for key, value in _query_args:
                                _new_args[key] = value

                            if "access_token" in _new_args:
                                del(_new_args["access_token"])
                            _id_arg_list.append((self.id_list[count], urllib.urlencode(_new_args)))
                        else:
                            print "No next"
                    else:
                        _continue = False
                elif _r_code == 400:
                    raise Exception("Error")
                else:
                    logging.debug(_r_code, _r_body)
            print _id_arg_list
            _batch_requests = json.dumps(batch_id_requests(_id_arg_list, self.url_base,))
            #   REMOVING THIS TEMPORARILY, SO THAT WE CAN RESPOND ONLY WITH THE
            #   VALID BODY. MIGHT NEED TO BECOME MORE SOPHISITICATED IN TIME.
            #   _response_list.append(response)
            print ps_counter

### WORKS FOR STREAMS, BUT NOT FOR SINGLE LAYER REQUESTS. INVESTIGATE FURTHER.
### PROBLEM IN THIS SECTION IS THAT THE RESPONSES ARE VARIED (LISTS VS DICTS)
### AND SO THERE NEEDS TO BE A COMMON WAY TO RETURN THE VALUES

            print _r_body
            if "data" in _r_body:
                _latest_responses = _r_body["data"]
            else:
                _latest_responses = _r_body
            _response_list = _response_list + _latest_responses



        return _response_list


    def run(self):
        _master_response_list = list()
        for _single_id in self.id_list:
            _string_url = str(self.url_base)
            _prepared_url = _string_url.format(page_id=_single_id, access_token=self.access_token)
            _created_datetime = datetime.datetime.now() # Start from now
            while _created_datetime > pd.to_datetime(self.date_end):
                response = requests.get(_prepared_url)
                logging.debug("Response successful")
                _response_check = error_checker(response)
                if _response_check == "VALID":
                    _response_dict = json.loads(response.content)
                    _master_response_list = _master_response_list + _response_dict["data"]
                    _created_datetime = pd.to_datetime(_response_dict["data"][-1:][0]["created_time"])
                    _prepared_url = json.loads(response.content)["paging"]["next"]
                    logging.info("Successful response: {id} - {created_datetime} oldest".format(
                        id=_single_id, created_datetime=_created_datetime))
                elif _response_check == "VALID_EMPTY":
                    _created_datetime = pd.to_datetime(self.date_end)
                elif _response_check == "RATELIMIT":
                    _wait_seconds = 120
                    logging.info("Rate limit reached. Waiting for {seconds} seconds".format(seconds=_wait_seconds))
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
            final_output = output_series.apply(lambda x: extract_data_from_single_batch_response(x,as_type="series"))
        elif return_format == "raw":
            final_output = response_tidy
        else:
            raise Exception("Unknown return_format supplied.")
        return final_output

    # def stream(self):
    #     pass

    # def collect(self):
    #     pass
