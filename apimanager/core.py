# -*- coding: utf-8 -*-

import requests
import json
import datetime
import logging
import urllib
import pytz
from itertools import product
import utils
from functools import partial

"""
apimanager.core
~~~~~~~~~~~~~~~~~

Core functions to deal with API requests.
"""


class RequestManager(object):

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
        self.hopper = list()

        if urls:
            self._urls = urls
            self.hopper += self._urls
        if pagination:
            self._pagination = pagination
        if hopper_params:
            self._hopper_params = hopper_params

    def from_product(self, base_urls, *param_groups):
        '''Create a batch of URLs from the product of passed iterables.

        :type base_urls: list[str]
        :type param_groups: tuple[list[dict[str]]]
        :rtype: RequestManager instance with URLs added to hopper.

        '''
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

    def set_pagination(self, **kwargs):
        '''Assign pagination variables to RequestManager object.'''
        self.pagination_func = partial(self._pagination["func"],
                                       **self._pagination["params"])
        self._pagination = {}
        self._pagination["func"] = kwargs["func"]
        self._pagination["params"] = kwargs["params"]

    def run(self):
        '''Make a series of requests from the hopper and handle pagination.'''
        # @TODO:
        # - Ability to return in different formats (raw, pandas, dict, etc)
        # - Better handling of OAuth and delays
        # - Start using "error_checker" like we had in
        #   the previous version below

        _response_list = list()
        while self.hopper:
            logging.debug("Entering an iteration of the loop")
            _current_request = self.hopper.pop()
            request_made = datetime.datetime.utcnow()
            request_made = request_made.replace(tzinfo=pytz.utc)
            logging.debug("Request sent timestamp: {}".format(request_made))
            response = requests.get(_current_request)
            json_response = json.loads(response.content)
            json_response["request_made"] = request_made

            if (response.status_code == 200
                    and not json_response.get("error")
                    and "data" in json_response):

                # @TODO - this is very FB specific, so need to adapt later
                _individual_results = json_response["data"]
                for counter, i in enumerate(_individual_results):
                    _individual_results[counter]["request_made"] = request_made
                _response_list += _individual_results

            elif (response.status_code == 200
                  and not json_response.get("error")
                  and all(k in json_response.keys()
                          for k in ["created_time", ])):

                # @TODO - hack to get Facebook likes/comments/shares quickly
                _individual_results = json_response
                _response_list.append(_individual_results)

            elif response.status_code == 200 and json_response.get("error"):
                _error_msg = "Error: {msg}".format(msg=json_response["error"])
                raise Exception(_error_msg)
            # NEED TO WORK TO INTEGRATE THIS CONCEPT
            # elif response.status_code == 400 and json.loads(
            #         json_response["body"])["error"]["code"] == 613:
            #     delay_time = 120
            #     logging.info("API limit exceeded. Waiting for %s seconds" % (
            #         delay_time))
            #     time.sleep(delay_time)
            #     self.hopper.append(response.url)
            #     raise Exception(json.loads(response.content))
            elif response.status_code == 400:
                raise Exception(json.loads(response.content))
            elif response.status_code == 404 and json_response.get("error"):
                raise Exception(json_response["error"])
            else:
                exception_string = "Unknown error/nCode: {}/n Response:{}"
                raise Exception(exception_string.format(response.status_code,
                                                        response.content))

            if self._pagination:
                next_url_check = self.pagination_func(json_response)
                logging.debug("Next url: {}".format(next_url_check))
                if next_url_check:
                    self.hopper.append(next_url_check)

        return _response_list
