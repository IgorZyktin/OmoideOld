# -*- coding: utf-8 -*-

"""Common database related things.
"""
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from omoide import constants

__all__ = [
    'metadata',
    'Base',
    'BaseModel',
]

metadata = sa.MetaData()
Base = declarative_base(metadata=metadata)


class BaseModel(Base):
    """Common base for all project models."""
    __abstract__ = True

    # marks
    revision = sa.Column(sa.String(length=constants.REVISION_LEN),
                         nullable=False, index=True)
    last_update = sa.Column(sa.String(length=constants.TIMESTAMP_LEN),
                            nullable=False)
