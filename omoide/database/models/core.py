# -*- coding: utf-8 -*-

"""Core models.
"""
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from omoide import constants
from omoide.database import common

__alL__ = [
    'Theme',
    'Group',
    'Meta',
]


class Theme(common.BaseModel):
    """Theme model."""
    __tablename__ = 'themes'

    # primary and foreign keys
    uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                     primary_key=True, nullable=False, index=True)
    # fields
    route = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)
    label = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)

    # relations
    groups = relationship('Group', back_populates='theme',
                          order_by='Group.label')
    tags = relationship('TagTheme', back_populates='theme',
                        order_by='TagTheme.value')


class Group(common.BaseModel):
    """Group model."""
    __tablename__ = 'groups'

    # primary and foreign keys
    # unique group identifier, starts with g_
    uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                     primary_key=True, nullable=False, index=True)
    # unique theme identifier, starts with t_
    theme_uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                           sa.ForeignKey('themes.uuid'),
                           nullable=False, unique=False, index=True)
    # fields
    # resource location
    route = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)
    # human-readable label for entity
    label = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)

    # information about origin
    # metarecord values are more important than these
    # date of registration in form '2021-01-01'
    registered_on = sa.Column(sa.String(length=constants.DATE_LEN),
                              nullable=False)
    # uuid of user or ''
    registered_by = sa.Column(sa.String(length=constants.MAX_LEN),
                              nullable=False)
    # name of the author
    author = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)
    # link to author's page or account
    author_url = sa.Column(sa.Text, nullable=False)
    # link to the page where this content was seen
    origin_url = sa.Column(sa.Text, nullable=False)
    # optional description of the entity
    comment = sa.Column(sa.Text, nullable=False)

    # string with arbitrary names, that represent some logical structure
    # supposed to be used in ordering, like 'plants,flowers,daisy'
    hierarchy = sa.Column(sa.Text, nullable=False)

    # relations
    theme = relationship('Theme', back_populates='groups')
    metas = relationship('Meta', back_populates='group',
                         order_by='Meta.ordering')
    tags = relationship('TagGroup', back_populates='group',
                        order_by='TagGroup.value')


class Meta(common.BaseModel):
    """Metarecord of a single item in the storage.

    Minimal unit of storage. Stores all info about one specific file.
    """
    __tablename__ = 'metas'

    # primary and foreign keys
    # unique meta identifier, starts with m_
    uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                     primary_key=True, nullable=False)
    # unique group identifier, starts with g_
    group_uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                           sa.ForeignKey('groups.uuid'),
                           nullable=False, unique=False)
    # fields
    # path to actual files, relative to theme directory
    path_to_content = sa.Column(sa.Text, nullable=False)
    path_to_preview = sa.Column(sa.Text, nullable=False)
    path_to_thumbnail = sa.Column(sa.Text, nullable=False)

    # original file parameters, can indirectly help in sorting
    # like 'somefile', without extension and dot
    original_filename = sa.Column(sa.Text, nullable=False)
    # like 'jpg', without dot
    original_extension = sa.Column(sa.String(length=constants.MAX_LEN),
                                   nullable=False)
    # specific content information
    # in pixels for images, 0 for everything else
    width = sa.Column(sa.Integer, nullable=False)
    # in pixels for images, 0 for everything else
    height = sa.Column(sa.Integer, nullable=False)
    # in megapixels for images, 0 for everything else
    resolution = sa.Column(sa.Float, nullable=False)
    # in bytes for any file
    size = sa.Column(sa.Integer, nullable=False)
    # string like 'image', 'video', etc.
    type = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)

    # used in group handling, some arbitrary number, that helps in sorting
    ordering = sa.Column(sa.Integer, nullable=False)

    # information about origin
    # metarecord values are more important than these
    # date of registration in form '2021-01-01'
    registered_on = sa.Column(sa.String(length=constants.DATE_LEN),
                              nullable=False, server_default='')
    # uuid of user or ''
    registered_by = sa.Column(sa.String(length=constants.MAX_LEN),
                              nullable=False)
    # name of the author
    author = sa.Column(sa.String(length=constants.MAX_LEN), nullable=False)
    # link to author's page or account
    author_url = sa.Column(sa.Text, nullable=False)
    # link to the page where this content was seen
    origin_url = sa.Column(sa.Text, nullable=False)
    # optional description of the entity
    comment = sa.Column(sa.Text, nullable=False)

    # identification info
    # encoded signature string
    signature = sa.Column(sa.Text, nullable=False)
    # human-readable type, like 'md5'
    signature_type = sa.Column(sa.Text, nullable=False)

    # string with arbitrary names, that represent some logical structure
    # supposed to be used in ordering, like 'plants,flowers,daisy'
    hierarchy = sa.Column(sa.Text, nullable=False)

    # relations
    group = relationship('Group', back_populates='metas')
    tags = relationship('TagMeta', back_populates='meta',
                        order_by='TagMeta.value')
