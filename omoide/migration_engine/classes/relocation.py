# -*- coding: utf-8 -*-
"""Helper type for relocation/conversion.
"""
from typing import List, Dict

from pydantic import BaseModel, Field

__all__ = [
    'Relocation',
    'OneGroup',
    'OneFile',
    'OneConversion',
]


class OneConversion(BaseModel):
    """Helper type for each output file relocation/conversion."""
    width: int
    height: int
    folder_to: str
    operation_type: str


class OneFile(BaseModel):
    """Helper type for each output file relocation/conversion."""
    uuid: str
    source_filename: str
    target_filename: str
    conversions: List[OneConversion] = Field(default_factory=list)


class OneGroup(BaseModel):
    """Helper type for each output file relocation/conversion."""
    folder_from: str
    files: Dict[str, OneFile] = Field(default_factory=dict)


class Relocation(BaseModel):
    """Helper type that describes relocation of a single leaf."""
    groups: Dict[str, OneGroup] = Field(default_factory=dict)
