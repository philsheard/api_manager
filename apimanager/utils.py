import datetime
import numpy as np
import json

def split_series_into_batches(series):
    array_segment = np.array(series)
    number_of_segments = array_segment.shape[0]/25
    batched_arrays = np.array_split(array_segment, number_of_segments)
    return batched_arrays

def batch_id_requests(data):
    list_of_batch_requests = list()
    for i in data:
        list_of_batch_requests.append({"method":"GET","relative_url":i + "/?fields=shares,likes.summary(true),comments.summary(true)"})
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