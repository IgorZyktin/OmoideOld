# -*- coding: utf-8 -*-

"""Index server constants.
"""
VERSION = '2021-10-06'
HOST = '127.0.0.1'
PORT = 9000

MESSAGE_INIT = 'Please wait a few minutes for server init after reload'
MESSAGE_RELOADING = ('New content is loading right now and '
                     'will be available in a few minutes')

SELECT_INDEX_METAS = """
SELECT meta_uuid, number, path_to_thumbnail 
FROM index_metas
ORDER BY number;
"""

SELECT_INDEX_TAGS = """
SELECT tag, uuid 
FROM index_tags
ORDER BY id;
"""
