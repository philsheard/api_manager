# -*- coding: utf-8 -*-

import os, sys, json

"""
apimanager.config
~~~~~~~~~~~~~~~~~

This module is simply to setup credentials for your API connections. To begin with, a
single set of credentials per platform is allowed.
"""

# @TODO - one day it will need to support multiple users

def load_credentials(format="dict"):
    _config_path = os.path.dirname(__file__) + "/settings/config.json"
    try:
        with open(_config_path, "r") as _config_file:
            _config_file_contents = _config_file.read()
    except:
        raise Exception("Failed to load config.json file. Is it present?")

    if format == "dict":
        _formatted_credentials = json.loads(_config_file_contents)
    elif format == "json":
        _formatted_credentials = _config_file_contents
    else:
        _formatted_credentials = json.loads(_config_file_contents)

    return _formatted_credentials


credentials = load_credentials(format="dict")
