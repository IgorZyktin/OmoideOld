# -*- coding: utf-8 -*-
"""Database tools used specifically by the Application.
"""
from collections import defaultdict
from typing import Optional, Dict, Type, Union, Any, Set

import ujson
from sqlalchemy.orm import Session

from omoide import search_engine, constants
from omoide.database import models


def get_meta(session: Session, meta_uuid: str) -> Optional[models.Meta]:
    """Load instance of Meta from db."""
    return session.query(models.Meta) \
        .where(models.Meta.uuid == meta_uuid).first()


def get_index(session: Session) -> search_engine.Index:
    """Load instance of Index from db."""
    metas = list(session.query(models.IndexMetas).order_by('number').all())
    all_metas = [
        search_engine.ShallowMeta(x.meta_uuid, x.number, x.path_to_thumbnail)
        for x in metas
    ]

    by_tags = defaultdict(set)
    for each in session.query(models.IndexTags).all():
        by_tags[each.tag.lower()].add(each.uuid)

    index = search_engine.Index(
        all_metas=all_metas,
        by_tags={
            tag: frozenset(uuids)
            for tag, uuids in by_tags.items()
        },
    )

    return index


def get_statistic(session: Session,
                  active_themes: Optional[Set[str]]
                  ) -> search_engine.Statistics:
    """Load statistics for given targets from db.

    Could get SQL injection here.
    """
    if active_themes is None:
        keys = ['stats__all_themes']
    else:
        keys = [f'stats__{x}' for x in active_themes]

    statistic = search_engine.Statistics()
    for key in keys:
        item = session.query(models.Helper) \
            .where(models.Helper.key == key).first()

        if item is not None:
            local_statistic = search_engine.Statistics.from_dict(
                source=ujson.loads(item.value)
            )
            statistic += local_statistic

    return statistic


_THEME_NAMES_CACHE: Dict[str, str] = {}
_GROUP_NAMES_CACHE: Dict[str, str] = {}
_GRAPH_CACHE: Optional[Dict[str, Any]] = None


def get_theme_name(session: Session, theme_uuid: str) -> str:
    """Return cached or find theme name by uuid."""
    if theme_uuid == constants.ALL_THEMES:
        return ''
    return _common_getter(session, theme_uuid,
                          _THEME_NAMES_CACHE, models.Theme)


def get_group_name(session: Session, group_uuid: str) -> str:
    """Return cached or find group name by uuid."""
    return _common_getter(session, group_uuid,
                          _GROUP_NAMES_CACHE, models.Group)


def _common_getter(session: Session, uuid: str, collection: Dict[str, str],
                   model: Union[Type[models.Theme], Type[models.Group]]
                   ) -> str:
    """Return cached or find in database."""
    value = collection.get(uuid)

    if value is not None:
        return value

    response = session.query(model).where(model.uuid == uuid).first()

    if response is not None:
        value = response.label
        collection[uuid] = value
        return value

    return constants.UNKNOWN


def get_graph(session: Session) -> dict:
    """Load navigation graph from db."""
    global _GRAPH_CACHE

    if _GRAPH_CACHE is not None:
        return _GRAPH_CACHE

    raw_graph = session.query(models.Helper) \
        .where(models.Helper.key == 'graph').first()

    if raw_graph:
        graph = ujson.loads(raw_graph.value)
    else:
        graph = {}

    _GRAPH_CACHE = graph

    return graph
