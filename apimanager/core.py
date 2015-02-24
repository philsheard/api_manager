# -*- coding: utf-8 -*-

import pandas as pd
import requests
import json
import datetime
import logging

import numpy as np

import sys

from .utils import split_series_into_batches, batch_id_requests, extract_data_from_single_batch_response

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

    def run(self):
        master_response_list = list()
        for single_id in self.id_list:
            string_url = str(self.url_base)
            prepared_url = string_url.format(page_id=single_id, access_token=self.access_token)
            created_datetime = datetime.datetime.now()

            while created_datetime > pd.to_datetime(self.date_end):
                response = requests.get(prepared_url)

                # This is where error checking / code checking should take place

                response_dict = json.loads(response.content)
                if response.status_code != 200:
                    logging.warning('Response was not a 200 code. Investigate.') # will print a message to the console
                    print response.status_code
                    print response.content
                    raise Exception("Response exception.")
                elif response_dict.get("data",None):
                    # Check whether the response has "data" records
                    master_response_list = master_response_list + response_dict["data"]
                    created_datetime = pd.to_datetime(response_dict["data"][-1:][0]["created_time"])
                    prepared_url = json.loads(response.content)["paging"]["next"]
                    logging.info("Successful response: {id} - {created_datetime} oldest".format(
                        id=single_id, created_datetime=created_datetime))
                elif response_dict.get("error",None):
                    print response_dict
                    raise Exception("Unknown API error. See response to debug")
                else:
                    # Provide a condition for the loop to end gracefully
                    created_datetime = pd.to_datetime(self.date_end)
                    print response_dict
                    logging.warning('Some sort of error took place. Investigate.') # will print a message to the console
            else:
                logging.info("Loop finished for {id}".format(id=single_id))
        return master_response_list

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
                    print "."
                    OK_to_proceed = True
                elif last_response["code"] == 400:
                    if json.loads(last_response["body"])["error"]["code"] == 613:
                        delay_time = 120
                        print "\nAPI limit exceeded. Waiting for %s seconds" % (delay_time)
                        print "==="
                        time.sleep(delay_time)
                    else:
                        print "\nUNKNOWN!!"
                        print last_response#[:250]
                        raise Exception("Unknown error code.")
                else:
                    print "\nUNKNOWN!!"
                    print last_response#[:250]
                    raise Exception("Unknown error code.")
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
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
