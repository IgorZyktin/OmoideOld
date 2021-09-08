# -*- coding: utf-8 -*-

"""Collection of classes used on initial parsing stage.

This module describes actual requirements that imposed on source files.
We're using intentionally simplified syntax there, so these entities
are not like actual database models.
"""
from typing import List, Collection, NoReturn, Optional

from pydantic import BaseModel, Field, validator

from omoide import constants

__all__ = [
    'Source',
    'Theme',
    'Group',
    'Extended',
    'Meta',
    'Synonym',
]


def get_prefix(field_name: str, string: str) -> str:
    """Extract prefix from full variable name."""
    if string.startswith(constants.VARIABLE_SIGN):
        raise ValueError(
            f'Field {field_name} is not supposed to '
            f'contain variable at this moment, got {string!r}'
        )
    return string[0]


def assert_unique(field_name: str, collection: Collection[str]
                  ) -> Optional[NoReturn]:
    """Raise if items are not unique."""
    if len(collection) != len(set(collection)):
        raise ValueError(
            f'Field {field_name} must have unique items, got {collection}'
        )


def assert_has_prefix(field_name: str, string: str,
                      expected_prefix: str) -> Optional[NoReturn]:
    """Raise if prefix is incorrect."""
    prefix = get_prefix(field_name, string)

    if prefix != expected_prefix:
        raise ValueError(
            f'Field {field_name} is supposed to '
            f'have prefix {expected_prefix}, got {string!r}'
        )


def assert_equal(var1: str, var2: str) -> Optional[NoReturn]:
    """Raise if values differ."""
    if var1 != var2:
        raise ValueError(
            f'Values are different {var1!r} != {var2!r}'
        )


# noinspection PyMethodParameters
class UniqueTagsMixin:
    """Mixin that checks uniqueness."""

    # pylint: disable=no-self-use
    @validator('tags')
    def must_be_unique(cls, value):
        """Raise if items are not unique."""
        assert_unique('tags', value)
        return value


# noinspection PyMethodParameters
class UniqueValuesMixin:
    """Mixin that checks uniqueness."""

    @validator('values')
    def must_be_unique(cls, value):
        """Raise if items are not unique."""
        assert_unique('values', value)
        return value


# noinspection PyMethodParameters
class UniqueFilenamesMixin:
    """Mixin that checks uniqueness."""

    @validator('filenames')
    def must_be_unique(cls, value):
        """Raise if items are not unique."""
        assert_unique('filenames', value)
        return value


class Synonym(BaseModel, UniqueValuesMixin):
    """User defined Synonym."""
    uuid: str
    label: str
    values: List[str] = Field(default_factory=list)


# noinspection PyMethodParameters
class Theme(BaseModel, UniqueTagsMixin):
    """User defined Theme."""
    uuid: str
    route: str
    label: str
    synonyms: List[Synonym] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    @validator('uuid')
    def must_be_theme(cls, value):
        """Raise if UUID is incorrect."""
        assert_has_prefix('uuid', value, constants.PREFIX_THEME)
        return value


# noinspection PyMethodParameters
class _BaseEntity(BaseModel, UniqueTagsMixin):
    """Base class for Group and Meta."""
    registered_on: str = Field(default='')
    registered_by: str = Field(default='')
    author: str = Field(default='')
    author_url: str = Field(default='')
    origin_url: str = Field(default='')
    comment: str = Field(default='')
    hierarchy: str = Field(default='')
    tags: List[str] = Field(default_factory=list)


class Extended(_BaseEntity, UniqueFilenamesMixin):
    """Additional fields for specific part of group."""
    filenames: List[str]


# noinspection PyMethodParameters
class Group(_BaseEntity):
    """User defined Theme."""
    uuid: str
    theme_uuid: str
    route: str
    label: str
    extended: List[Extended] = Field(default_factory=list)

    @validator('theme_uuid')
    def must_be_theme(cls, value):
        """Raise if UUID is incorrect."""
        assert_has_prefix('theme_uuid', value, constants.PREFIX_THEME)
        return value

    @validator('uuid')
    def must_be_group(cls, value):
        """Raise if UUID is incorrect."""
        assert_has_prefix('uuid', value, constants.PREFIX_GROUP)
        return value


# noinspection PyMethodParameters
class Meta(_BaseEntity, UniqueFilenamesMixin):
    """User defined Meta."""
    theme_uuid: str
    group_uuid: str
    filenames: List[str]

    @validator('theme_uuid')
    def must_be_theme(cls, value):
        """Raise if UUID is incorrect."""
        assert_has_prefix('theme_uuid', value, constants.PREFIX_THEME)
        return value

    @validator('group_uuid')
    def must_be_group(cls, value):
        """Raise if UUID is incorrect."""
        assert_has_prefix('group_uuid', value, constants.PREFIX_GROUP)
        return value


class Source(BaseModel):
    """All source entries combined."""
    themes: List[Theme] = Field(default_factory=list)
    groups: List[Group] = Field(default_factory=list)
    metas: List[Meta] = Field(default_factory=list)
    synonyms: List[Synonym] = Field(default_factory=list)
