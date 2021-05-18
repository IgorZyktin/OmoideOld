# -*- coding: utf-8 -*-
"""Fast lookup values, some statistic, etc.
"""
import json

from sqlalchemy.orm import Session

from omoide import infra, constants
from omoide import search_engine
from omoide.database import models


def build_helpers(session: Session, stdout: infra.STDOut) -> int:
    """Create fast lookup tables."""
    new_values = 0
    new_values += calculate_statistics(session, stdout)
    new_values += construct_navigation_info(session, stdout)
    return new_values


def calculate_statistics(session: Session, stdout: infra.STDOut) -> int:
    """Calculate statistics for all realms/themes."""
    stdout.print('\tCalculating statistics')
    new_values = 0

    all_stats = search_engine.Statistics()
    for theme in session.query(models.Theme).all():
        theme_stats = search_engine.Statistics()
        for group in theme.groups:
            for meta in group.metas:
                theme_stats.add(
                    item_date=meta.registered_on or group.registered_on,
                    item_size=meta.size,
                    item_tags=[x.value for x in meta.tags]
                )

        all_stats += theme_stats
        new_helper = models.Helper(
            key=f'stats__{theme.uuid}',
            value=json.dumps(theme_stats.as_dict(), ensure_ascii=False)
        )
        session.add(new_helper)
        new_values += 1

    new_helper = models.Helper(
        key=f'stats__{constants.ALL_THEMES}',
        value=json.dumps(all_stats.as_dict(), ensure_ascii=False)
    )
    session.add(new_helper)
    new_values += 1

    session.commit()
    return new_values


def construct_navigation_info(session: Session, stdout: infra.STDOut) -> int:
    """Build graph of available realms/themes."""
    stdout.print('\tConstructing graph')

    graph = {}
    for theme in session.query(models.Theme).order_by('label').all():
        graph[theme.uuid] = {
            'label': theme.label,
            'groups': {},
        }
        for group in theme.groups:
            graph[theme.uuid]['groups'][group.uuid] = {
                'label': group.label
            }

    new_helper = models.Helper(
        key='graph',
        value=json.dumps(graph, ensure_ascii=False)
    )

    session.add(new_helper)
    session.commit()

    return 1
