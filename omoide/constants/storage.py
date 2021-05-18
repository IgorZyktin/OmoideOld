# -*- coding: utf-8 -*-

"""Constant values.
"""
import os as _os

# files and folders
SOURCES_FOLDER_NAME = 'sources'
STORAGE_FOLDER_NAME = 'storage'
CONTENT_FOLDER_NAME = 'content'
DATABASE_FOLDER_NAME = 'app_database'

MEDIA_CONTENT_FOLDER_NAME = 'content'
MEDIA_PREVIEW_FOLDER_NAME = 'preview'
MEDIA_THUMBNAILS_FOLDER_NAME = 'thumbnails'

DEFAULT_SOURCES_FOLDER = _os.path.join('.', SOURCES_FOLDER_NAME)
DEFAULT_STORAGE_FOLDER = _os.path.join('.', STORAGE_FOLDER_NAME)
DEFAULT_CONTENT_FOLDER = _os.path.join('.', CONTENT_FOLDER_NAME)
DEFAULT_DATABASE_FOLDER = _os.path.join('.', DATABASE_FOLDER_NAME)

SOURCE_FILE_NAME = 'source.json'
UNIT_FILE_NAME = 'unit.json'
CACHE_FILE_NAME = 'cache.json'
MIGRATION_FILE_NAME = 'migration.sql'
RELOCATION_FILE_NAME = 'relocation.json'

ROOT_DB_FILE_NAME = 'root.db'
BRANCH_DB_FILE_NAME = 'branch.db'
LEAF_DB_FILE_NAME = 'migration.db'
STATIC_DB_FILE_NAME = 'database.db'

# media parameters
PREVIEW_SIZE = (1024, 1024)
THUMBNAIL_SIZE = (384, 384)
COMPRESS_TO = [
    PREVIEW_SIZE,
    THUMBNAIL_SIZE,
]

# database constants
MAX_LEN = 255
UUID_LEN = 38
REVISION_LEN = 40
DATE_LEN = 10
TIMESTAMP_LEN = 19
