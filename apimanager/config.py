# -*- coding: utf-8 -*-

import os, sys

"""
apimanager.config
~~~~~~~~~~~~~~~~~

This module is simply to setup credentials for your API connections. To begin with, a
single set of credentials per platform is allowed.
"""

# @TODO - one day it will need to support multiple users

def load_credentials():
    _config_path = os.path.dirname(__file__) + "/settings/config.json"
    try:
        with open(_config_path, "r") as _config_file:
            _config_file_contents = _config_file.read()
        return _config_file_contents
    except:
        raise Exception("Failed to load config.json file. Is it present?")


credentials = load_credentials()
