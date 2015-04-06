# -*- coding: utf-8 -*-

from .core import RequestManager
import pandas as pd


def create_manager():
    '''Facebook API interfaces'''
    manager = RequestManager()
    return manager

def feed(ids, access_token, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/feed"
    _api_type = "stream"
    pagination = {'pagination_scheme': pagination_scheme,
                  'path': ('data',-1,"created_time"),
                  'end_goal': pd.to_datetime(date_end),
                  'formatter': pd.to_datetime}
    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
        api_type=_api_type, date_end=date_end, pagination=pagination)
    return manager

def insights_fans(ids, access_token, date_start=None, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/insights/page_fans"
    _api_type = "batch"
    manager = RequestManager(ids=ids, url_base=url_base,
        date_start=date_start, date_end=date_end,
        access_token=access_token, api_type=_api_type,
        pagination=False)
    return manager

def promotable_posts(ids, access_token, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/promotable_posts"
    _api_type = "stream"
    pagination = {'pagination_scheme': pagination_scheme,
              'path': ('data',-1,"created_time"),
              'end_goal': pd.to_datetime(date_end),
              'formatter': pd.to_datetime}
    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
        api_type=_api_type, date_end=date_end, pagination=pagination)
    return manager

def interactions(ids, access_token):
    url_base = "https://graph.facebook.com/v2.2/{}/?fields=shares,likes.summary(true),comments.summary(true)"
    _api_type = "single"
    manager = RequestManager(ids=ids, url_base=url_base, 
        access_token=access_token, api_type=_api_type,
        pagination=False)
    return manager
