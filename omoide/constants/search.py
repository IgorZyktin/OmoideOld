# -*- coding: utf-8 -*-

"""Constant values.
"""
# search engine
import re

ALL_THEMES = 'all_themes'
NO_GROUP = 'no_group'
UNKNOWN = 'unknown'

# identity
PREFIX_THEME = 't'
PREFIX_GROUP = 'g'
PREFIX_META = 'm'
PREFIX_SYNONYM = 's'

ALL_PREFIXES = ''.join([PREFIX_THEME,
                        PREFIX_GROUP,
                        PREFIX_META,
                        PREFIX_SYNONYM])
ALL_PREFIXES_SET = set(ALL_PREFIXES)

VARIABLE_SIGN = '$'
VARIABLE_SEARCH_WINDOW = 40
UUID_MAKE_VARIABLE_PATTERN = r'var\(\'(\w+)\',\s+\'(\w+)\'\)'
UUID_VARIABLE_PATTERN = r'\$\w+'

KW_AND = '+'
KW_OR = '|'
KW_NOT = '-'

OPERATORS = {KW_AND, KW_OR, KW_NOT}

STRICT_THEME_UUID_PATTERN = re.compile(
    '^t_[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$'
)

THEMES_SEPARATION = re.compile(r',|%2C')
