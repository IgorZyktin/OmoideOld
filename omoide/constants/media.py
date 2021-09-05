# -*- coding: utf-8 -*-

"""Constant values.
"""
# media parameters
PREVIEW_SIZE = (1024, 1024)
THUMBNAIL_SIZE = (384, 384)
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
