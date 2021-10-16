# -*- coding: utf-8 -*-

"""Object that handles image analyzing and conversion.
"""
import math
import os
from typing import Optional, Callable, Tuple

from PIL import Image

from omoide import constants

Image.MAX_IMAGE_PIXELS = None

# from typing import TypedDict, Optional, Callable # FIXME

__all__ = [
    'Renderer',
    # 'MediaInfo', # FIXME
]


# FIXME
# class MediaInfo(TypedDict):
#     """Container for media information."""
#     width: int
#     height: int
#     resolution: float
#     size: int
#     type_: str
#     signature: str
#     signature_type: str


def analyze_static_image(path: str):
    """Get parameters of a static image (not gif)."""
    image = Image.open(path)
    width, height = image.size
    image.close()

    media_info = {
        'width': width,
        'height': height,
        'resolution': round(width * height / 1_000_000, 2),
        'size': os.path.getsize(path),
        'type': 'image',
        'signature': '',  # TODO
        'signature_type': '',  # TODO
    }

    return media_info


def analyze_test(path: str):
    """Used for testing, returns dummy info."""
    media_info = {
        'width': 0,
        'height': 0,
        'resolution': 0.0,
        'size': os.path.getsize(path),
        'type': 'image',
        'signature': '',
        'signature_type': '',
    }
    return media_info


def get_analyze_tool(extension: str) -> Optional[Callable[[str], dict]]:
    """Return callable that can analyze this kind of files.
    """
    return {
        'jp2': analyze_static_image,
        'jpg': analyze_static_image,
        'jpeg': analyze_static_image,
        'bmp': analyze_static_image,
        'png': analyze_static_image,
        'test': analyze_test,
    }.get(extension.lower())


class Renderer:
    """Object that handles image analyzing and conversion.
    """

    @staticmethod
    def is_known_media(extension: str) -> bool:
        """Return True if we can handle this file."""
        return get_analyze_tool(extension) is not None

    @staticmethod
    def analyze(path: str, extension: str):
        """Gather media information about the file."""
        tool = get_analyze_tool(extension)

        if tool is None:
            print(f'Unable to analyze this kind of file: {path}')

        info = tool(path)
        return info

    @staticmethod
    def calculate_size(original_width: int, original_height: int,
                       target_width: int, target_height: int
                       ) -> Tuple[int, int]:
        """Get size for preview or thumbnail.

        Unlike pillow, this method revolves around height.
        We have strict target height but can tolerate various
        variants of width.
        """
        if not all([original_width, original_height,
                    target_width, target_height]):
            raise ValueError('Resize is not working with zero sized images')

        dimension = min(target_height, original_height)
        coefficient = dimension / original_height
        resulting_width = math.ceil(coefficient * original_width)
        return resulting_width, dimension

    @staticmethod
    def save_new_size(path_from: str, path_to: str,
                      width: int, height: int) -> None:
        """Save image with given dimensions to a new path."""
        if path_to.endswith('jpg'):
            kwargs = constants.SAVE_PARAMETERS['jpg']
        else:
            kwargs = {}

        image = Image.open(path_from)

        if not path_from.lower().endswith('jpg') and path_to.endswith('jpg'):
            # non jpg downscale produces terrible quality
            image = image.convert('RGB')

        image = image.resize((width, height))
        image.save(path_to, **kwargs)
        image.close()
