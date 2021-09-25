# -*- coding: utf-8 -*-

"""Media constants.
"""
PREVIEW_WIDTH = 1024
PREVIEW_HEIGHT = 1024
PREVIEW_SIZE = (PREVIEW_WIDTH, PREVIEW_HEIGHT)

THUMBNAIL_WIDTH = 384
THUMBNAIL_HEIGHT = 384
THUMBNAIL_SIZE = (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)

COMPRESS_TO = [
    PREVIEW_SIZE,
    THUMBNAIL_SIZE,
]

SAVE_PARAMETERS = {
    'jpg': {
        'quality': 80,
        'progressive': True,
        'optimize': True,
    }
}
