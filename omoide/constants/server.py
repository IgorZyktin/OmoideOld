# -*- coding: utf-8 -*-

"""Constant values.
"""
import os as _os

DEFAULT_SERVER_HOST = '0.0.0.0'
DEFAULT_SERVER_PORT = 8080

# files and folders
TEMPLATES_FOLDER_NAME = 'templates'
STATIC_FOLDER_NAME = 'static'
INJECTION_FILE_NAME = 'injection.txt'

DEFAULT_TEMPLATES_FOLDER = _os.path.join('.', TEMPLATES_FOLDER_NAME)
DEFAULT_STATIC_FOLDER = _os.path.join('.', STATIC_FOLDER_NAME)

ITEMS_PER_PAGE = 100

MAX_TEXT_INPUT_SIZE = 4096
