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
        self._pagination = {}
        self._pagination["func"] = kwargs["func"]
        self._pagination["params"] = kwargs["params"]
        self.pagination_func = partial(self._pagination["func"],
                                       **self._pagination["params"])

    def run(self):
        '''Make a series of requests from the hopper and handle pagination.'''
        # @TODO:
        # - Ability to return in different formats (raw, pandas, dict, etc)

        response_list = list()
        while self.hopper:
            logging.debug("Entering an iteration of the loop")

            request_made = datetime.datetime.utcnow()
            request_made = request_made.replace(tzinfo=pytz.utc)
            logging.debug("Request sent timestamp: {}".format(request_made))

            _current_request = self.hopper.pop()
            response = requests.get(_current_request)

            # json_response = json.loads(response.content)
            # json_response["request_made"] = request_made

            result, output = utils.process_response(response,
                                                    request_made)
            if result == "OK":
                response_list.extend(output)
            elif result == "RETRY":
                self.hopper.append(response.url)

            if getattr(self, "_pagination", None):
                response_dict = json.loads(response.content)
                next_url_check = self.pagination_func(response_dict)
                logging.debug("Next url: {}".format(next_url_check))
                if next_url_check:
                    self.hopper.append(next_url_check)

        self.result = response_list
        return response_list
