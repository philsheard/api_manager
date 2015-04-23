import numpy as np
import json
import logging
import pandas as pd
import datetime
import pytz


def error_checker(response):
    _return_value = "ERROR"  # Default option
    _response_dict = json.loads(response.content)
    r_code = response.status_code
    if r_code is 200 and _response_dict.get("data", None) is True:
        logging.debug("Response looks fine. Setting positive progress.")
        _return_value = "VALID"
    elif r_code is 200 and _response_dict.get("data", None) is False:
        logging.debug("Valid response but no data. Typically end of records.")
        _return_value = "VALID_EMPTY"
    elif r_code is 400 and _response_dict["body"]["error"]["code"] is 613:
        # Rate limit error - recommend waiting
        _return_value = "RATELIMIT"
    elif _response_dict.get("error", None):
        # Unspecified error
        raise Exception('Error. If repeatable, add to detected errors.')
    else:
        # Wildcard error capture
        raise Exception('Unknown error. Investigate.')

    return _return_value


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
