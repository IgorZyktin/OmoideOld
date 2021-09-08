# -*- coding: utf-8 -*-
"""Fast lookup tables.

Gets loaded on start of the application and
helps limiting amount of database requests.
"""
from typing import List

from sqlalchemy.orm import Session

from omoide import infra
from omoide.database import models

_META_THEMES_CACHE = {}
_META_GROUPS_CACHE = {}
_SYNONYMS = None


def build_indexes(session: Session, stdout: infra.STDOut) -> int:
    """Create fast lookup tables."""
    new_values = 0
    new_values += build_index_tags(session, stdout)
    new_values += build_index_meta(session, stdout)
    return new_values


def lazy_get_theme(meta: models.Meta) -> models.Theme:
    """Lazy return Theme or go to database for it."""
    value = _META_THEMES_CACHE.get(meta.uuid)

    if value is None:
        value = meta.group.theme
        _META_THEMES_CACHE[meta.uuid] = value

    return value


def lazy_get_group(meta: models.Meta) -> models.Group:
    """Lazy return Group or go to database for it."""
    value = _META_GROUPS_CACHE.get(meta.uuid)

    if value is None:
        value = meta.group
        _META_GROUPS_CACHE[meta.uuid] = value

    return value


def lazy_get_synonyms(session) -> List[models.Synonym]:
    """Lazy return Group or go to database for it."""
    global _SYNONYMS

    if _SYNONYMS is None:
        _SYNONYMS = session.query(models.Synonym).all()

    return _SYNONYMS


def build_index_tags(session: Session, stdout: infra.STDOut) -> int:
    """Create indexes for tags."""
    stdout.print('\tBuilding index for tags')
    new_values = 0

    for meta in session.query(models.Meta).all():
        theme = lazy_get_theme(meta)
        group = lazy_get_group(meta)

        all_tags = {
            *(x.value for x in theme.tags),
            *(x.value for x in group.tags),
            *(x.value for x in meta.tags),
            theme.uuid,
            group.uuid,
            meta.uuid,
        }

        for synonym in lazy_get_synonyms(session):
            values = {x.value for x in synonym.values}
            for value in values:
                if value in all_tags:
                    all_tags.update(values)
                    break

        new_values += len(all_tags)

        for tag in all_tags:
            value = models.IndexTags(tag=tag, uuid=meta.uuid)
            session.add(value)

    session.commit()

    return new_values


def build_index_meta(session: Session, stdout: infra.STDOut) -> int:
    """Create simplified table for thumbnail information."""
    stdout.print('\tBuilding index for metas')

    all_metas = list(session.query(models.Meta).all())
    new_values = len(all_metas)

    all_metas.sort(key=lambda meta: (meta.hierarchy, meta.ordering))

    for i, each_meta in enumerate(all_metas):
        value = models.IndexMetas(
            meta_uuid=each_meta.uuid,
            number=i,
            path_to_thumbnail=each_meta.path_to_thumbnail,
        )
        session.add(value)

    session.commit()

    return new_values
