# -*- coding: utf-8 -*-

import pdb

from .core import RequestManager
import pandas as pd
# from . import utils
# from . import pagination
import utils
import pagination

pagination_scheme = ('paging', 'next')


def create_manager():
    '''Facebook API interfaces'''
    manager = RequestManager()
    return manager

# TEMPLATES - Make the common call types reusable.
# Insights, single calls, streams, etc.


def _fb_stream_model(ids, access_token, api_endpoint, date_end=None):
    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)

    # Build basic URLs
    formatted_urls = (url_template.format(_id) for _id in ids)

    # Move on to paramaters
    base_params = [{"access_token": access_token}]

    # Handle Pagination
    pagination_dict = {
                       'target_path': ('data', -1, "created_time"),
                       'stop_val': pd.to_datetime(date_end),
                       }

    # Create the RequestManager instance
    manager = RequestManager()
    # Now pass the paramaters and base URLs to fill the hopper.
    manager.from_product(formatted_urls, base_params)

    # Pagination
    manager.set_pagination(func=pagination.end_date, params=pagination_dict)

    return manager


def _fb_in_batch_model(ids, access_token, api_endpoint,
                       date_range=None, freq=None, period="day"):
    if period not in {"day", "week", "days_28", "lifetime"}:
        raise ValueError("Period must be 'day','week', 'days_28' or 'lifetime'")

    pdb.set_trace()

    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    # Build basic URLs
    formatted_urls = (url_template.format(_id) for _id in ids)

    # Move on to paramaters
    base_params = [{"access_token": access_token,
                    "period": period}, ]

    # Build date periods
    if date_range:
        _date_windows = utils.api_call_time_windows(date_range=date_range, freq=freq)
        _date_params = [{'since': x[0], 'until': x[1]} for x in _date_windows]
    else:
        _date_params = None

    # Create the RequestManager instance
    manager = RequestManager()
    # Now pass the paramaters and base URLs to fill the hopper.
    if _date_params:
        manager.from_product(formatted_urls, base_params, _date_params)
    else:
        manager.from_product(formatted_urls, base_params)
    # @TODO - add paging logic in here.

    return manager


# API specific methods - Make the common call types reusable.
# Insights, single calls, streams, etc.

def feed(ids, access_token, date_end=None):
    api_endpoint = "/v2.2/{}/feed"
    manager = _fb_stream_model(ids=ids, access_token=access_token, 
                               api_endpoint=api_endpoint, 
                               date_end=date_end)
    return manager


def promotable_posts(ids, access_token, date_end):
    api_endpoint = "/v2.2/{}/promotable_posts"
    manager = _fb_stream_model(ids=ids, access_token=access_token, 
                               api_endpoint=api_endpoint, 
                               date_end=date_end)
    return manager

def insights_all(ids, access_token, date_range, period="day", freq=90):
    # pdb.set_trace()

    api_endpoint = "/v2.2/{}/insights/"
    manager = _fb_in_batch_model(ids=ids, access_token=access_token, api_endpoint=api_endpoint,
                                 date_range=date_range, period=period, freq=freq)
    return manager


def insights_fans(ids, access_token, period="lifetime"):
    api_endpoint = "/v2.2/{}/insights/page_fans"
    manager = _fb_in_batch_model(ids=ids, access_token=access_token, api_endpoint=api_endpoint, period=period)
    return manager

def insights_page_fan_adds_unique(ids, access_token, date_range, period="day", freq=90):
    api_endpoint = "/v2.2/{}/insights/page_fan_adds_unique"
    manager = _fb_in_batch_model(ids=ids, access_token=access_token, api_endpoint=api_endpoint,
                                 date_range=date_range, freq=freq, period=period)
    return manager


def insights_impressions_unique(ids, access_token, date_start,
                                date_end, period="day", freq=90):
    api_endpoint = "/v2.2/{}/insights/page_impressions_unique"
    manager = _fb_in_batch_model(ids, access_token, api_endpoint,
                                 date_start, date_end, period, freq)
    return manager


def interactions(ids, access_token):
    api_endpoint = "/v2.2/{}/"
    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    formatted_urls = (url_template.format(_id) for _id in ids)

    params = {"access_token": access_token,
              "fields": "shares,likes.summary(true),comments.summary(true)"}
    manager = RequestManager()
    manager.from_product(formatted_urls, params)
    return manager


def insights_post_all(ids, access_token):
    api_endpoint = "/v2.2/{}/insights"
    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    formatted_urls = (url_template.format(_id) for _id in ids)

    params = {"access_token": access_token}

    manager = RequestManager()
    manager.from_product(formatted_urls, params)
    return manager

def insights_post_unique_impressions(ids, access_token):
    api_endpoint = "/v2.2/{}/insights/post_impressions_unique"
    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    formatted_urls = (url_template.format(_id) for _id in ids)

    params = {"access_token": access_token}

    manager = RequestManager()
    manager.from_product(formatted_urls, params)
    return manager

def insights_post_unique_engaged_users(ids, access_token):
    api_endpoint = "/v2.2/{}/insights/post_engaged_users"
    api_domain = "https://graph.facebook.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    formatted_urls = (url_template.format(_id) for _id in ids)

    params = {"access_token": access_token}

    manager = RequestManager()
    manager.from_product(formatted_urls, params)
    return manager
