# -*- coding: utf-8 -*-
"""Helper type for relocation/conversion.
"""
from dataclasses import dataclass

__all__ = [
    'Relocation',
]


@dataclass
class Relocation:
    """Helper type for each output file relocation/conversion."""
    uuid: str
    width: int
    height: int
    folder_from: str
    folder_to: str
    operation_type: str
    source_filename: str
    target_filename: str
