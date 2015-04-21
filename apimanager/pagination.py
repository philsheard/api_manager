# -*- coding: utf-8 -*-

import logging
from . import utils

# From the Pandas docs:
'''formatters:
default None, a dictionary (by column) of functions each of which takes a
single argument and returns a formatted string.
'''


def end_date(response, target_path, stop_val):  # check_method=">="
    '''Find an end date within a response using the target path and stop val.

    :type response: dict (from response json)
    :type target_path: tuple[str/int] (used to navigate a dict tree)
    :type stop_val: str/datetime (will be converted if str)
    :rtype: str (containing a URL) or False.

    '''
    next_url = False
    logging.debug("End goal: {}".format(stop_val))
    try:
        stopper = reduce(lambda x, y: x[y],
                         target_path, response)
    except:
        raise Exception("Couldn't match the stopper location")
    logging.debug("Stopper: {}".format(stopper))
    stopper_dt = utils.datetime_formatter(stopper)
    if type(stop_val) in [str, unicode]:
        stop_val_dt = utils.datetime_formatter(stop_val)
    else:
        stop_val_dt = stop_val
    logging.debug("Converted stopper: {}".format(stopper_dt))
    if stopper_dt > stop_val_dt:
        try:
            pagination_scheme = ('paging', 'next')
            next_url = reduce(lambda x, y: x[y], pagination_scheme, response)
            logging.info("Paging check positive. Passing next URL.")
        except:
            raise Exception("Path to next URL wasn't right")
    else:
        next_url = False
    return next_url
