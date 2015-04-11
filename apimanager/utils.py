import numpy as np
import json
import logging
import pandas as pd
import datetime# import datetime.fromtimestamp as fromtimestamp


def split_series_into_batches(series):
    array_segment = np.array(series)
    number_of_segments = array_segment.shape[0]/25
    batched_arrays = np.array_split(array_segment, number_of_segments)
    return batched_arrays

def extract_data_from_single_batch_response(response,as_type='dict'):
    # @TODO - MAKE THIS FLEXIBLE TO TAKE DYNAMIC FIELDS
    import pandas as pd
    current_response = json.loads(response["body"])
    results = dict()
    try:
        results = {"id": current_response["id"],}
    except:
        print current_response
    if "comments" in current_response:
        results["comments"] = int(current_response["comments"]["summary"]["total_count"])
    else:
        results["comments"] = 0
    if "likes" in current_response:
        results["likes"] = int(current_response["likes"]["summary"]["total_count"])
    else:
        results["likes"] = 0
    if "shares" in current_response:
        results["shares"] = int(current_response["shares"]["count"])
    else:
        results["shares"] = 0

    if as_type == "series":
        return pd.Series(results)
    else:
        return results

def error_checker(response):
    _return_value = "ERROR" # Default option 
    _response_dict = json.loads(response.content)
    if response.status_code == 200 and _response_dict.get("data",None) is True:
        logging.debug("Response looks fine. Setting positive progress.")
        _return_value = "VALID"
    elif response.status_code == 200 and _response_dict.get("data",None) is False:
        logging.debug("Valid response but no data. Typically end of records.")
        _return_value = "VALID_EMPTY"
    elif response.status_code == 400 and _response_dict["body"]["error"]["code"] == 613:
        # Rate limit error - recommend waiting
        _return_value = "RATELIMIT"
    elif _response_dict.get("error",None):
        # There was an error in the API from FB. This should be caught by the
        # status code check for 200, but it's a backstop just in case.
        raise Exception('There was an error. Could be innocent, like a rate limit error.')
    else:
       raise Exception('Some sort of unknown error took place. Investigate.')

    return _return_value

def api_call_time_windows(start, end, freq=90):
    _latest_date = pd.to_datetime(end)
    _earliest_date = pd.to_datetime(start)
    # TODO - need to change 'start' and 'end', it conflicts here/
    range_with_intervals = pd.date_range(start=_earliest_date, end=_latest_date, freq=(freq * pd.datetools.day))
    converted_to_list = range_with_intervals.to_pydatetime().tolist()
    if converted_to_list[-1] < _earliest_date:
        converted_to_list.append(_earliest_date.to_pydatetime())
    dates_as_integer = pd.Series(converted_to_list).astype(int) // 10**9
    return zip(dates_as_integer[:-1],dates_as_integer[1:])

#     _start_timestamp, _end_timestamp = pd.to_datetime((_start,_end))
#     print _start_timestamp, _end_timestamp
#     time_periods = pd.date_range(start=_start_timestamp,
#                                     end=_endend_timestamp,
#                                     freq=_freq,
# # @TODO - this method needs to be timezone-aware in future.
# #                                     tz="UTC",
# #                                      tz=None,
# #                                      normalize=True,
#                                      )
#         # _all_timestamps = pd.Series([start_timestamp,] + list(pd.to_datetime(time_periods.values,))+ [end_timestamp,])
#         # _all_timestamps.sort(inplace=True)
#         # _all_timestamps = _all_timestamps.unique()
#         # _all_timestamps = _all_timestamps.astype(int) // 10**9
#         # return zip(_all_timestamps[:-1],_all_timestamps[1:])
#     return time_periods

def datetime_formatter(value):
    if type(value) == unicode and len(value) == 10 and ":" not in value:
        logging.debug('Detected as Instagram unix timestamp.')
        _converted = float(value)
        _converted = pd.to_datetime(_converted,unit="s")
    elif type(value) == unicode and len(value) == 24 and ":" in value:
        logging.debug('Detected as Facebook timestamp.')
        _converted = pd.to_datetime(value)
    else:
        raise Exception("Unknown dateformat.")
    return _converted
