# -*- coding: utf-8 -*-

"""Index models.
"""
import sqlalchemy as sa

from omoide import constants
from omoide.database import common

__alL__ = [
    'IndexTags',
    'IndexMetas',
]


class IndexTags(common.Base):
    """Index for tags info.

    Used to perform fast search on tags. Note that we're not limiting tag
    column with existing tags and uuid column with existing uuids.
    Gets loaded at the application start and never queried after.
    """
    __tablename__ = 'index_tags'

    # primary and foreign keys
    id = sa.Column(sa.Integer,
                   primary_key=True, unique=True, autoincrement=True)
    # fields
    tag = sa.Column(sa.String(length=constants.MAX_LEN),
                    nullable=False, unique=False, index=True)
    uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                     nullable=False, unique=False)


class IndexMetas(common.Base):
    """Index for metas.

    Fast access to the basic meta information.
    Gets loaded at the application start and never queried after.
    """
    __tablename__ = 'index_metas'

    # primary and foreign keys
    meta_uuid = sa.Column(sa.String(length=constants.UUID_LEN),
                          sa.ForeignKey('metas.uuid'),
                          primary_key=True, nullable=False,
                          unique=True, index=True)
    # fields
    number = sa.Column(sa.Integer, nullable=False)
    path_to_thumbnail = sa.Column(sa.Text, nullable=False)
