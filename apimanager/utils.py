import datetime
import numpy as np
import json
import logging
import pandas as pd

def split_series_into_batches(series):
    array_segment = np.array(series)
    number_of_segments = array_segment.shape[0]/25
    batched_arrays = np.array_split(array_segment, number_of_segments)
    return batched_arrays

def xstr(s):
    if s is None:
        return ''
    return "?" + str(s)


def batch_id_requests(id_arg_list, url_base,):
    list_of_batch_requests = list()
    # if not optional_args:
    #     optional_args = list()
    #     for i in range(len(data)):
    #         optional_args.append("")
    for _single_id, _opt_args in id_arg_list:
        list_of_batch_requests.append({"method":"GET","relative_url":str(_single_id + url_base + xstr(_opt_args))})
    return list_of_batch_requests

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
    # This is just the single-stream version. Need to merge into the batch version,
    # which is slightly more advanced (it handled OAuth errors better and will
    # hang back when needed).

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
        # Provide a condition for the loop to end gracefully
#        _created_datetime = pd.to_datetime(self.date_end)
        print response.content
        raise Exception('Unknown error - might need to assess whether it has run out of data.')
#        logging.warning('Some sort of unknown error took place. Investigate.') # will print a message to the console

    return _return_value
