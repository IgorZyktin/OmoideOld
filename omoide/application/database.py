# -*- coding: utf-8 -*-
"""Database tools used specifically by the Application.
"""
from collections import defaultdict
from typing import Optional, Dict, Type, Union, Any, Set

import ujson
from sqlalchemy import func, select, union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from omoide import search_engine, constants
from omoide.database import models


async def get_meta(session: AsyncSession,
                   meta_uuid: str) -> Optional[models.Meta]:
    """Load instance of Meta from db."""
    return await session.get(models.Meta, meta_uuid)


async def get_group(session: AsyncSession,
                    group_uuid: str) -> Optional[models.Group]:
    """Load instance of Group from db."""
    return await session.get(models.Group, group_uuid)


async def get_theme(session: AsyncSession,
                    theme_uuid: str) -> Optional[models.Theme]:
    """Load instance of Theme from db."""
    return await session.get(models.Theme, theme_uuid)


async def get_all_tags(session: AsyncSession, theme_uuid: str,
                       group_uuid: str, meta_uuid: str) -> list[str]:
    """Gather all tags from db."""
    stmt1 = select(models.TagTheme.value) \
        .where(models.TagTheme.theme_uuid == theme_uuid)

    stmt2 = select(models.TagGroup.value) \
        .where(models.TagGroup.group_uuid == group_uuid)

    stmt3 = select(models.TagMeta.value) \
        .where(models.TagMeta.meta_uuid == meta_uuid)

    stmt4 = union(stmt1, stmt2, stmt3)
    all_tags = (await session.execute(stmt4)).fetchall()

    return [x for x, in all_tags]


async def get_group_metas_uuids(session: AsyncSession,
                                group_uuid: str) -> list[str]:
    """Get all uuids within this group."""
    stmt = select(models.Meta.uuid).where(models.Meta.group_uuid == group_uuid)
    response = (await session.execute(stmt)).fetchall()
    return [x for x, in response]


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


async def get_newest_groups(session: Session) -> tuple[str, list[dict]]:
    """Get list of groups added on the last update.

    Example of as_dicts:
    [
        {
            'theme_label': 'Farm theme',
            'label': 'Farm',
            'uuid': 'g_ec0e0354-e8f6-4b07-95d0-46f0f8a6ed22'
        }
    ]
    """
    stmt = select(func.max(models.Group.registered_on))
    maximum = (await session.execute(stmt)).scalar_one_or_none()

    stmt = select(models.Theme.label, models.Group.label, models.Group.uuid) \
        .where(models.Group.registered_on == maximum) \
        .join(models.Theme, models.Theme.uuid == models.Group.theme_uuid) \
        .order_by(models.Theme.label, models.Group.label)
    groups = await session.execute(stmt)

    as_dicts = [
        dict(zip(['theme_label', 'label', 'uuid'],
                 section))
        for section in groups
    ]

    return maximum, as_dicts


async def get_statistic(session: AsyncSession,
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
        stmt = select(models.Helper.value).where(models.Helper.key == key)
        response = await session.execute(stmt)
        item = response.scalar()

        if item is not None:
            local_statistic = search_engine.Statistics.from_dict(
                source=ujson.loads(item)
            )
            statistic += local_statistic

    return statistic


_THEME_NAMES_CACHE: Dict[str, str] = {}
_GROUP_NAMES_CACHE: Dict[str, str] = {}
_GRAPH_CACHE: Optional[Dict[str, Any]] = None


async def get_theme_name(session: AsyncSession, theme_uuid: str) -> str:
    """Return cached or find theme name by uuid."""
    if theme_uuid == constants.ALL_THEMES:
        return ''
    return await _common_getter(session, theme_uuid,
                                _THEME_NAMES_CACHE, models.Theme)


async def get_group_name(session: AsyncSession, group_uuid: str) -> str:
    """Return cached or find group name by uuid."""
    return await _common_getter(session, group_uuid,
                                _GROUP_NAMES_CACHE, models.Group)


async def _common_getter(session: AsyncSession, uuid: str,
                         collection: Dict[str, str],
                         model: Type[models.Theme] | Type[models.Group]
                         ) -> str:
    """Return cached or find in database."""
    value = collection.get(uuid)

    if value is not None:
        return value

    stmt = select(model).where(model.uuid == uuid)
    response = await session.execute(stmt)
    value = response.scalar()
    print(response, value)

    if response is not None:
        value = response.label
        collection[uuid] = value
        return value

    return constants.UNKNOWN


async def get_graph(session: AsyncSession) -> dict:
    """Load navigation graph from db."""
    global _GRAPH_CACHE

    if _GRAPH_CACHE is not None:
        return _GRAPH_CACHE

    stmt = select(models.Helper).where(models.Helper.key == 'graph')
    raw_graph = (await session.execute(stmt)).first()

    if raw_graph:
        graph = ujson.loads(raw_graph[0].value)
    else:
        graph = {}

    _GRAPH_CACHE = graph

    return graph
