# -*- coding: utf-8 -*-

"""Helper models.
"""
import sqlalchemy as sa

from omoide import constants
from omoide.database import common

__alL__ = [
    'Helper',
]


class Helper(common.Base):
    """Helper model."""
    __tablename__ = 'helpers'

    # primary and foreign keys
    key = sa.Column(sa.String(length=constants.MAX_LEN),
                    primary_key=True, nullable=False, index=True)
    # fields
    value = sa.Column(sa.Text, nullable=False)
