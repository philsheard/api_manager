# -*- coding: utf-8 -*-

import pandas as pd
import requests
import json
import datetime
import logging
import time
# import re.
import urllib
import pytz
from itertools import product
import utils

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""


class RequestManager(object):

    def _hopper_initial_fill(self):
        # if self._hopper_params:
        #     raw_params = {'access_token': self.access_token,}
        #     params = urllib.urlencode(raw_params)
        # else:
        #     params = ""
        # @TODO - This handling params is hacky and needs to be changed.

        core_params = self._params
        if self.api_type == "stream":
            logging.debug("API type: {}".format(self.api_type))
            url_params = urllib.urlencode(core_params)
            print url_params
            self.hopper += [str(self.url_base.format(_id) + "?" + url_params)
                            for _id in self.id_list]

        elif self.api_type == "single":
            logging.debug("API type: {}".format(self.api_type))
            url_params = urllib.urlencode(core_params)
            self.hopper += [self.url_base.format(_id) + "?" + url_params
                            for _id in self.id_list]

        elif self.api_type == "batch":
            logging.debug("API type: {}".format(self.api_type))

            # response_list = list()
            time_windows = utils.api_call_time_windows(self.date_start,
                                                       self.date_end)
            merged_combo = product(time_windows, self.id_list,)
            for combo in merged_combo:
                additional_params = {"since": combo[0][0],
                                     "until": combo[0][1]}
                combined_params = core_params.copy()
                combined_params.update(additional_params)
                url_params = urllib.urlencode(combined_params)
                page_name = combo[1]
                self.hopper += [self.url_base.format(page_name) + "?" + url_params]
        else:
            raise Exception("Unknown api_type")

        logging.debug("Initial hopper fill complete")

    def manage_paging(self, response):
        _next_url = False
        _end_goal = self._pagination["end_goal"]
        logging.debug("End goal: {}".format(_end_goal))
        _loc_to_check_against_goal = self._pagination["path"]

        try:
            _stopper = reduce(lambda x, y: x[y],
                              _loc_to_check_against_goal, response)
        except:
            raise Exception("Couldn't match the stopper location")

        logging.debug("Stopper: {}".format(_stopper))
        _final_stopper = utils.datetime_formatter(_stopper)
        logging.debug("Converted stopper: {}".format(_final_stopper))
        _next_url_loc = self._pagination["pagination_scheme"]
        if _final_stopper > _end_goal:
            try:
                _next_url = reduce(lambda x, y: x[y], _next_url_loc, response)
                logging.info("Paging check positive. Passing next URL.")
            except:
                raise Exception("Path to next URL wasn't right")
        else:
            _next_url = False
        return _next_url

    def __init__(self, urls=None, hopper_params=True, pagination=None):
        # Check whether ids contains a string or list. 
        # If it's a string, create a list of one for consistency

        # if isinstance(ids, str):
        #     self.id_list = [ids,]
        #     self.batch = False
        # elif isinstance(ids, list):
        #     self.id_list = ids
        #     self.batch = True
        # else:
        #     raise TypeError("IDs are not a valid list or string.")

        # Set the URL base provided in setup for this RequestManager instance

        self.hopper = list()

        if urls:
            self._urls = urls
            self.hopper += self._urls
        if pagination:
            self._pagination = pagination
        if hopper_params:
            self._hopper_params = hopper_params

    def from_product(self, base_urls, *param_groups):
        _combined_params = product(*param_groups)
        list_of_params = []
        for combined_param_product in _combined_params:
            params = {}
            for param_dict in combined_param_product:
                params.update(param_dict)
            list_of_params.append(urllib.urlencode(params))
        components = product(base_urls, list_of_params)
        finalised_urls = ["{0}?{1}".format(_u, _p) for _u, _p in components]
        self.hopper += finalised_urls
        return self

    def run(self):
        # @TODO:
        # - Ability to return in different formats (raw, pandas, dict, etc)
        # - Better handling of OAuth and delays
        # - Start using "error_checker" like we had in
        #   the previous version below

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
            _request_made = datetime.datetime.utcnow()
            _request_made = _request_made.replace(tzinfo=pytz.utc)
            logging.debug("Request sent timestamp: {}".format(_request_made))
            response = requests.get(_current_request)
            _json_response = json.loads(response.content)
            _json_response["request_made"] = _request_made
            if response.status_code == 200 and not _json_response.get("error") and "data" in _json_response:
                # @TODO - this is very FB specific, so need to adapt later
                _individual_results = _json_response["data"]
                for counter, i in enumerate(_individual_results):
                    _individual_results[counter]["_request_made"] = _request_made
                _response_list += _individual_results
            elif response.status_code == 200 and not _json_response.get("error") and all(k in _json_response.keys() for k in ["created_time",]):
                # @TODO - hack to get Facebook likes/comments/shares quickly
                _individual_results = _json_response
                _response_list.append(_individual_results)
            elif response.status_code == 200 and _json_response.get("error"):
                _error_msg = "Error: {msg}".format(msg=_json_response["error"])
                raise Exception(_error_msg)

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
            elif response.status_code == 404 and _json_response.get("error"):
                raise Exception(_json_response["error"])
            else:
                print response.status_code
                raise Exception("Unknown error/nCode: {}/n Response:{}".format(response.status_code,response.content))

            if self._pagination:
                next_url_check = self.manage_paging(_json_response)
                if next_url_check:
                    self.hopper.append(next_url_check)

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
