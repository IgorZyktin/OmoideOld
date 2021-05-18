# -*- coding: utf-8 -*-

"""Collection of classes used after initial parsing is complete.
"""
from typing import List

from pydantic import BaseModel, Field

__all__ = [
    'Theme',
    'Group',
    'Meta',
    'TagTheme',
    'TagGroup',
    'TagMeta',
    'Synonym',
    'SynonymValue',
    'Unit',
]


class BaseUnitElement(BaseModel):
    """Base class for all parsed elements."""
    revision: str
    last_update: str


class Theme(BaseUnitElement):
    """User defined Theme."""
    uuid: str
    route: str
    label: str


class _BaseEntity(BaseUnitElement):
    """Base class for Group and Meta."""
    registered_on: str = Field(default='')
    registered_by: str = Field(default='')
    author: str = Field(default='')
    author_url: str = Field(default='')
    origin_url: str = Field(default='')
    comment: str = Field(default='')
    hierarchy: str = Field(default='')


class Group(_BaseEntity):
    """User defined Theme."""
    uuid: str
    theme_uuid: str
    route: str
    label: str


class Meta(_BaseEntity):
    """User defined Meta."""
    uuid: str
    theme_uuid: str
    group_uuid: str

    path_to_content: str = Field(default='')
    path_to_preview: str = Field(default='')
    path_to_thumbnail: str = Field(default='')
    original_filename: str = Field(default='')
    original_extension: str = Field(default='')
    width: int = Field(default=0)
    height: int = Field(default=0)
    resolution: float = Field(default=0.0)
    size: int = Field(default=0)
    type: str = Field(default='')
    ordering: int = Field(default=0)
    signature: str = Field(default='')
    signature_type: str = Field(default='')


class TagTheme(BaseUnitElement):
    """Tag model."""
    theme_uuid: str
    value: str


class TagGroup(BaseUnitElement):
    """Tag model."""
    group_uuid: str
    value: str


class TagMeta(BaseUnitElement):
    """Tag model."""
    meta_uuid: str
    value: str


class Synonym(BaseUnitElement):
    """User defined Synonym."""
    uuid: str
    label: str


class SynonymValue(BaseUnitElement):
    """User defined Synonym."""
    synonym_uuid: str
    value: str


class Unit(BaseModel):
    """All parsed entries combined."""
    themes: List[Theme] = Field(default_factory=list)
    groups: List[Group] = Field(default_factory=list)
    metas: List[Meta] = Field(default_factory=list)

    tags_themes: List[TagTheme] = Field(default_factory=list)
    tags_groups: List[TagGroup] = Field(default_factory=list)
    tags_metas: List[TagMeta] = Field(default_factory=list)

    synonyms: List[Synonym] = Field(default_factory=list)
    synonyms_values: List[SynonymValue] = Field(default_factory=list)
