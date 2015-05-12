# -*- coding: utf-8 -*-

from .core import RequestManager
import pandas as pd
import datetime

pagination_scheme = ('pagination','next_url')

def users_search(ids, client_id,):
    _url_base = str("https://api.instagram.com/v1/users/search?q={}&client_id=" + client_id)
    _api_type = "single"
    pagination = False
    # params = {"client_id": client_id,}
    params = ""
    manager = RequestManager(ids=ids, url_base=_url_base, 
        access_token=client_id, api_type=_api_type, 
        # date_start=date_start, date_end=date_end,
        hopper_params=False, pagination=pagination,
        params=params)
    return manager

def user_media(ids, client_id, date_start=None, date_end=None,):
    _url_base = str("https://api.instagram.com/v1/users/{}/media/recent/?client_id=" + client_id)
    _api_type = "stream"
    pagination = {'pagination_scheme': pagination_scheme,
                  'path': ('data',-1,"created_time"),
                  'end_goal': pd.to_datetime(date_end),
                  'formatter': (datetime.datetime.fromtimestamp, "s")}
    # params = {"client_id": client_id,}
    params = ""
    manager = RequestManager(ids=ids, url_base=_url_base, 
    	access_token=client_id, api_type=_api_type, 
    	date_start=date_start, date_end=date_end,hopper_params=False,
        pagination=pagination, params=params)
    return manager

def tag_media(ids, client_id, date_start=None, date_end=None,):
    # _url_base = str("https://api.instagram.com/v1/tags/{}/media/recent?client_id=" + client_id)
    # _api_type = "stream"
    # pagination = {'pagination_scheme': pagination_scheme,
    #               'path': ('data',-1,"created_time"),
    #               'end_goal': pd.to_datetime(date_end),
    #               'formatter': (datetime.datetime.fromtimestamp, "s")}
    # # params = {"client_id": client_id,}
    # params = ""
    # manager = RequestManager(ids=ids, url_base=_url_base, 
    #     access_token=client_id, api_type=_api_type, 
    #     date_start=date_start, date_end=date_end,hopper_params=False,
    #     pagination=pagination, params=params)
    # return manager

    api_endpoint = "/v1/tags/{}/media/recent"
    api_domain = "https://api.instagram.com"
    url_template = "{}{}".format(api_domain, api_endpoint)
    formatted_urls = (url_template.format(_id) for _id in ids)

    params = {"client_id": client_id, }
    manager = RequestManager()
    manager.from_product(formatted_urls, params)
    return manager
