# -*- coding: utf-8 -*-
"""Helper type for relocation/conversion.
"""
from typing import List

from pydantic import BaseModel

__all__ = [
    'Operation',
    'Relocation',
]


class Operation(BaseModel):
    """Helper type for each output file relocation/conversion."""
    width: int
    height: int
    folder_to: str
    operation_type: str


class Relocation(BaseModel):
    """Helper type for a single source file relocation/conversion."""
    uuid: str
    source_filename: str
    target_filename: str
    folder_from: str
    operations: List[Operation]
