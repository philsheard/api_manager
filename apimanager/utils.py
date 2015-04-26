# -*- coding: utf-8 -*-

import json
import logging
import pandas as pd
import datetime
import pytz
import time


def error_checker(response):
    return_value = "ERROR"  # Default option
    r_code = response.status_code
    response_dict = json.loads(response.content)
    if (r_code is 200 and "data" in response_dict
            and "error" not in response_dict):
        logging.debug("Response looks fine. Setting positive progress.")
        return_value = "VALID_FB_FEED"
    elif (r_code is 200 and "error" not in response_dict
          and all(k in response_dict.keys() for k in ["created_time", ])):
        return_value = "VALID_FB_INTERACTIONS"
    elif (r_code is 200 and response_dict.get("data", None) is False):
        logging.debug("Valid response but no data. Typically end of records.")
        return_value = "VALID_EMPTY"
    elif (r_code is 200 and "error" in response_dict):
        return_value = "ERROR"
    elif r_code is 400 and response_dict["body"]["error"]["code"] is 613:
        return_value = "RATELIMIT"
    elif r_code is 400:
        return_value = "ERROR"
    else:
        print response_dict
        raise Exception('Unknown error. Investigate.')
    logging.debug(return_value)
    return return_value


def process_response(response, request_made):
    response_check = error_checker(response)
    response_dict = json.loads(response.content)
    if response_check == "VALID_FB_FEED":
        individual_results = response_dict["data"]
        output = []
        for counter, i in enumerate(individual_results):
            individual_results[counter]["request_made"] = request_made
            output += individual_results
        result = "OK"
    elif response_check == "VALID_FB_INTERACTIONS":
        individual_results = response_dict
        result = "OK"
        output = individual_results
    elif response_check == "VALID_EMPTY":
        result = "OK"
        output = None
    elif response_check == "RATELIMIT":
        delay_time = 120
        msg = "API limit exceeded. Waiting for {} seconds"
        logging.info(msg.format(delay_time))
        time.sleep(delay_time)
        result = "RETRY"
    elif response_check == "ERROR":
        error_msg = "Error: {msg}".format(msg=response.content)
        raise Exception(error_msg)
    else:
        exception_string = "Unknown error/nCode: {}/n Response:{}"
        raise Exception(exception_string.format(response.status_code,
                                                response.content))
    return (result, output)


def api_call_time_windows(start=None, end=None, freq=90,
                          output_format="unix_ts"):
    # # @TODO - this method needs to be timezone-aware in future.
    _utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if start is None:
        start = _utcnow
    if end is None:
        end = _utcnow - datetime.datetime.timedelta(days=7)

    _earliest_date = pd.to_datetime(start)
    _latest_date = pd.to_datetime(end)
    range_with_intervals = pd.date_range(start=_earliest_date,
                                         end=_latest_date,
                                         freq=(freq * pd.datetools.day))
    converted_to_list = range_with_intervals.to_pydatetime().tolist()

    # Check whether the last date is included.
    # Function uses Pandas for the date range, and its behaviour is to exclude
    # the last date if the frequency provided is greater than the time window.
    if converted_to_list[-1] < _latest_date:
        converted_to_list.append(_latest_date.to_pydatetime())
    # Convert the timestamps into relevant format
    if output_format is "unix_ts":  # Unix timestamp = seconds since the epoch.
        final_date_ranges = pd.Series(converted_to_list).astype(int) // 10**9
    else:
        raise Exception("Unknown format requested")
    return zip(final_date_ranges[:-1], final_date_ranges[1:])


def datetime_formatter(value=None):
    if value:
        print value
        if type(value) == unicode and len(value) == 10 and ":" not in value:
            logging.debug('Detected as Instagram unix timestamp.')
            _converted = float(value)
            _converted = pd.to_datetime(_converted, unit="s")
        elif type(value) == unicode and len(value) == 24 and ":" in value:
            logging.debug('Detected as Facebook timestamp.')
            _converted = pd.to_datetime(value)
        else:
            logging.debug("Value: {}/n\
                           Type: {}/n\
                           Length: {}".format(value, type(value), len(value)))
            raise Exception("Unknown dateformat.")
        return _converted
    else:
        raise Exception("No value provided")
