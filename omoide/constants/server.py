# -*- coding: utf-8 -*-

"""Constant values.
"""
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 8080

# files and folders
INJECTION_FILE_NAME = 'injection.txt'

DEFAULT_TEMPLATES_PATH = ('omoide', 'app_server', 'templates')
DEFAULT_STATIC_PATH = ('omoide', 'app_server', 'static')

ITEMS_PER_PAGE = 100
PAGES_IN_BLOCK = 10
MAX_TEXT_INPUT_SIZE = 4096

ALLOWED_SYMBOLS = frozenset(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '+-| _,.'
    'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
)
