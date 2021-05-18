# -*- coding: utf-8 -*-

"""Tools that should return same results during migration/relocation/etc.
"""
import random
import string
from datetime import datetime
from typing import Optional

from omoide import constants

__all__ = [
    'get_now',
    'get_revision',
]

_NOW: Optional[str] = None
_REVISION: Optional[str] = None


def get_now() -> str:
    """Get current moment as a string."""
    global _NOW
    if _NOW is None:
        _NOW = str(datetime.now().replace(microsecond=0))
    return _NOW


def set_now(now: str) -> None:
    """Set value."""
    global _NOW
    _NOW = now


def get_revision(length: int = constants.REVISION_LEN) -> str:
    """Generate unique revision number from os random generator."""
    global _REVISION
    if _REVISION is None:
        symbols = string.ascii_lowercase + string.digits
        tokens = [random.choice(symbols) for _ in range(length)]
        _REVISION = ''.join(tokens)
    return _REVISION


def set_revision(revision: str) -> None:
    """Set value."""
    global _REVISION
    _REVISION = revision
