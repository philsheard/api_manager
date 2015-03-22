# -*- coding: utf-8 -*-

from .core import RequestManager

def create_manager():
    '''Facebook API interfaces'''

    manager = RequestManager()

    return manager

def feed(ids, access_token, date_start=None, date_end=None,):

    url_base = "https://graph.facebook.com/v2.2/{page_id}/feed?access_token={access_token}"

    manager = RequestManager(ids=ids, url_base=url_base, access_token=access_token, 
        date_start=date_start, date_end=date_end)

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
