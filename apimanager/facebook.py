# -*- coding: utf-8 -*-

from .core import RequestManager
import pandas as pd
from . import utils
from . import pagination


pagination_scheme = ('paging', 'next')


def create_manager():
    '''Facebook API interfaces'''
    manager = RequestManager()
    return manager


def feed(ids, access_token, date_end=None,):
    # url_base = "https://graph.facebook.com/v2.2/{}/feed"
    # _api_type = "stream"
    # params = {"access_token": access_token}
    # manager = RequestManager(ids=ids, url_base=url_base,
    #                          access_token=access_token, api_type=_api_type,
    #                          date_end=date_end, pagination=pagination,
    #                          params=params)
    # return manager

    _api_domain = "https://graph.facebook.com"
    _api_endpoint = "/v2.2/{}/feed"
    url_template = "{}{}".format(_api_domain, _api_endpoint)

    # Build basic URLs
    _formatted_urls = (url_template.format(_id) for _id in ids)

    # Move on to paramaters
    _base_params = [{"access_token": access_token}]

    # Handle Pagination
    pagination_dict = {
                       'target_path': ('data', -1, "created_time"),
                       'stop_val': pd.to_datetime(date_end),
                       }

    # Create the RequestManager instance
    manager = RequestManager()
    # Now pass the paramaters and base URLs to fill the hopper.
    manager.from_product(_formatted_urls, _base_params)

    # Pagination
    # @TODO - the idea was to use a pagination func that takes the response
    # as an argument - however, it's a separate function and can't know about
    # it yet. One option is to pass the function and paramaters separately
    # and then compile the function when the thing gets run. Could use
    # 'partial' or something. Idea was to use `.map()` to apply the function.
    manager.set_pagination(func=pagination.end_date, params=pagination_dict)

    return manager


def insights_fans(ids, access_token, date_start=None, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/insights/page_fans"
    _api_type = "batch"
    params = {"access_token": access_token,
              "period": "day"}
    manager = RequestManager(ids=ids, url_base=url_base,
                             date_start=date_start, date_end=date_end,
                             access_token=access_token, api_type=_api_type,
                             pagination=False, params=params)
    return manager


def insights_impressions_unique(ids, access_token, date_start,
                                date_end, period="day", freq=180):
    if period not in {"day", "week", "days_28"}:
        raise ValueError("Period must be 'day','week' or 'days_28'")

    _api_domain = "https://graph.facebook.com"
    _api_endpoint = "/v2.2/{}/insights/page_impressions_unique"
    url_template = "{}{}".format(_api_domain, _api_endpoint)

    # Build basic URLs
    _formatted_urls = (url_template.format(_id) for _id in ids)

    # Move on to paramaters
    _base_params = [{"access_token": access_token,
                    "period": period}, ]

    # Build date periods
    _date_windows = utils.api_call_time_windows(date_start, date_end,
                                                freq=freq)
    _date_params = [{'since': x[0], 'until': x[1]} for x in _date_windows]

    # Create the RequestManager instance
    manager = RequestManager()
    # Now pass the paramaters and base URLs to fill the hopper.
    manager.from_product(_formatted_urls, _base_params, _date_params)
    # @TODO - add paging logic in here.

    return manager


def promotable_posts(ids, access_token, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/promotable_posts"
    _api_type = "stream"
    pagination = {'pagination_scheme': pagination_scheme,
                  'path': ('data', -1, "created_time"),
                  'end_goal': pd.to_datetime(date_end),
                  'formatter': pd.to_datetime}
    params = {"access_token": access_token}
    manager = RequestManager(ids=ids, url_base=url_base,
                             access_token=access_token,
                             api_type=_api_type, date_end=date_end,
                             pagination=pagination, params=params)
    return manager


def interactions(ids, access_token):
    url_base = "https://graph.facebook.com/v2.2/{}/"
    _api_type = "single"
    params = {"access_token": access_token,
              "fields": "shares,likes.summary(true),comments.summary(true)"}

    manager = RequestManager(ids=ids, url_base=url_base,
                             access_token=access_token, api_type=_api_type,
                             pagination=False, params=params)
    return manager


def insights_post_unique_impressions(ids, access_token):
    url_base = \
        "https://graph.facebook.com/v2.2/{}/insights/post_impressions_unique"
    _api_type = "single"
    params = {"access_token": access_token}
    manager = RequestManager(ids=ids, url_base=url_base,
                             access_token=access_token, api_type=_api_type,
                             pagination=False, params=params)
    return manager
