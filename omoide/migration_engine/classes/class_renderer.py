# -*- coding: utf-8 -*-

"""Object that handles image analyzing and conversion.
"""
import os
from typing import Optional, Callable
# from typing import TypedDict, Optional, Callable

from PIL import Image

__all__ = [
    'Renderer',
    # 'MediaInfo',
]


# class MediaInfo(TypedDict):
#     """Container for media information."""
#     width: int
#     height: int
#     resolution: float
#     size: int
#     type: str
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
    def resize(path_from: str, path_to: str, width: int, height: int) -> None:
        """Resize image."""
        image = Image.open(path_from)
        image.thumbnail((width, height))
        image.save(path_to)
        image.close()
