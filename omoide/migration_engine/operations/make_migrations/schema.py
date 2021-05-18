# -*- coding: utf-8 -*-

"""Supporting code needed for SQL commands.
"""
from typing import List

import sqlalchemy as sa

from omoide.database import models
from omoide.migration_engine import classes

FIELDS_TO_DROP = {
    models.Meta: {'theme_uuid'}
}


def drop_temporary_params(something: dict, model_type) -> dict:
    """Remove fields used on initial stages."""
    return {
        key: value for
        key, value in something.items()
        if key not in FIELDS_TO_DROP.get(model_type, set())
    }


def as_sql(objects: List[dict], model_type) -> List[classes.SQL]:
    """Instantiate migration commands for realms."""
    sql = []

    for each in objects:
        each = drop_temporary_params(each, model_type)
        stmt = sa.insert(model_type).values(**each)
        sql.append(classes.SQL(stmt))

    return sql


def instantiate_commands(content: dict):
    """Create all needed SQL instructions."""

    def _get(key: str) -> List[dict]:
        return content.get(key, [])

    sql: List[classes.SQL] = []

    sql.extend(as_sql(_get('themes'), models.Theme))
    sql.extend(as_sql(_get('groups'), models.Group))
    sql.extend(as_sql(_get('metas'), models.Meta))

    sql.extend(as_sql(_get('tags_themes'), models.TagTheme))
    sql.extend(as_sql(_get('tags_groups'), models.TagGroup))
    sql.extend(as_sql(_get('tags_metas'), models.TagMeta))

    sql.extend(as_sql(_get('synonyms'), models.Synonym))
    sql.extend(as_sql(_get('synonyms_values'), models.SynonymValue))

    return sql
