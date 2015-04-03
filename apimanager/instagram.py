# -*- coding: utf-8 -*-

from .core import RequestManager

def users_search(ids, client_id,):
    _url_base = str("https://api.instagram.com/v1/users/search?q={}&client_id=" + client_id)
    _api_type = "single"
    manager = RequestManager(ids=ids, url_base=_url_base, 
        access_token=client_id, api_type=_api_type, 
        # date_start=date_start, date_end=date_end,
        hopper_params=False)
    return manager

def user_media(ids, client_id, date_start=None, date_end=None,):
    _url_base = str("https://api.instagram.com/v1/users/{}/media/recent/?client_id=" + client_id)
    _api_type = "stream"
    manager = RequestManager(ids=ids, url_base=_url_base, 
    	access_token=client_id, api_type=_api_type, 
    	date_start=date_start, date_end=date_end,hopper_params=False)
    return manager

def tag_media(ids, client_id, date_start=None, date_end=None,):
    _url_base = str("https://api.instagram.com/v1/tags/{}/media/recent?client_id=" + client_id)
    _api_type = "stream"
    manager = RequestManager(ids=ids, url_base=_url_base, 
        access_token=client_id, api_type=_api_type, 
        date_start=date_start, date_end=date_end,hopper_params=False)
    return manager

