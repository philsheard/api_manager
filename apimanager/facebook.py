# -*- coding: utf-8 -*-

from .core import RequestManager
import pandas as pd

pagination_scheme = ('paging','next')

def create_manager():
    '''Facebook API interfaces'''

    manager = RequestManager()

    return manager

def feed(ids, access_token, date_start=None, date_end=None,):

    # url_base = "https://graph.facebook.com/v2.2/{}/feed?access_token={}"
    url_base = "https://graph.facebook.com/v2.2/{}/feed"
    pagination = {'pagination_scheme': pagination_scheme,
                  'path': ('data',-1,"created_time"),
                  'end_goal': pd.to_datetime(date_end),
                  'formatter': pd.to_datetime}

    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
        api_type="stream", 
        # date_start=date_start, date_end=date_end,
        pagination=pagination)

    return manager

def feed_test_a(ids, access_token, date_start=None, date_end=None,):
    _url_base = "https://graph.facebook.com/v2.2/{}/feed"
    _api_type = "stream"
    manager = RequestManager(ids=ids, url_base=_url_base, 
    	access_token=access_token, api_type=_api_type, 
    	date_start=date_start, date_end=date_end,)
    return manager

def feed_test_b(ids, access_token, date_start=None, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/?fields=shares,likes.summary(true),comments.summary(true)"
    _api_type = "single"
    manager = RequestManager(ids=ids, url_base=url_base, 
    	access_token=access_token, api_type=_api_type,)
    return manager


def insights_fans(ids, access_token, date_start=None, date_end=None,):
    url_base = "https://graph.facebook.com/v2.2/{}/insights/page_fans"
    _api_type = "batch"

    # pagination = {'pagination_scheme': pagination_scheme,
    #               'path': ('data','values',-1,),
    #               'end_goal': pd.to_datetime('2015-01-01')}

    manager = RequestManager(ids=ids, url_base=url_base,
        date_start=date_start, date_end=date_end,
        access_token=access_token, api_type=_api_type,
        pagination=False)
    return manager

def promotable_posts(ids, access_token, date_start=None, date_end=None,):

    url_base = "https://graph.facebook.com/v2.2/{page_id}/promotable_posts?access_token={access_token}"

    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
        date_start=date_start, date_end=date_end)

    return manager

def interactions(ids, access_token):

    # HMM - THIS DOESN'T HAVE A URL BASE DOES IT?
    url_base = "'method':'GET','relative_url':{id}/?fields=shares,likes.summary(true),comments.summary(true)'"

    # url_base = "This is new"
    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token,)

    return manager

def insights_likes(ids, access_token, date_start=None, date_end=None):

    url_base = "/insights/page_fans"

    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token,)

    return manager
