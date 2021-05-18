# -*- coding: utf-8 -*-
"""Business logic of the service.
"""
import datetime
import json
import time
from typing import Dict, Any, Callable, Optional, Set, List, Tuple

import ujson
from sqlalchemy.orm import sessionmaker, Session

from omoide import constants
from omoide import search_engine
from omoide import utils
from omoide.application import database as app_database
from omoide.application.class_paginator import Paginator
from omoide.application.class_web_query import WebQuery
from omoide.database import operations, models
from omoide.search_engine import find

_GRAPH_CACHE: Optional[Dict[str, Any]] = None


# pylint: disable=too-many-locals
def make_search_response(maker: sessionmaker, web_query: WebQuery,
                         query_builder: search_engine.QueryBuilder,
                         index: search_engine.Index) -> Dict[str, Any]:
    """Create context for search request."""
    start = time.perf_counter()

    with operations.session_scope(maker) as session:
        graph = app_database.get_graph(session)
        unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
        active_themes = extract_active_themes(unsafe_themes, graph)
        placeholder = get_placeholder_for_search(session, active_themes)

    user_query = web_query.get('q')
    current_page = int(web_query.get('page', '1'))
    search_query = query_builder.from_query(user_query)

    if not active_themes and active_themes is not None:
        uuids = []
        search_report = ['No themes to search on.']
    else:
        if search_query:
            uuids, search_report = find.specific_records(
                query=search_query,
                index=index,
                active_themes=active_themes or set(),
            )
        else:
            uuids, search_report = find.random_records(
                index=index,
                active_themes=active_themes,
                amount=constants.ITEMS_PER_PAGE,
            )

    paginator = Paginator(
        sequence=uuids,
        current_page=current_page,
        items_per_page=constants.ITEMS_PER_PAGE,
    )

    duration = time.perf_counter() - start
    note = get_note_for_search(len(paginator), duration)

    context = {
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'search_query': search_query,
        'paginator': paginator,
        'search_report': search_report,
        'note': note,
        'placeholder': placeholder,
    }
    return context


def make_navigation_response(maker: sessionmaker, web_query: WebQuery,
                             ) -> Dict[str, Any]:
    """Create context for navigation request (GET)."""
    with operations.session_scope(maker) as session:
        graph = app_database.get_graph(session)
        unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
        active_themes = extract_active_themes(unsafe_themes, graph)

    if active_themes is None:
        visibility = {x: True for x in graph}
        web_query['active_themes'] = constants.ALL_THEMES
    else:
        visibility = {x: (x in active_themes) for x in graph}

    context = {
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'graph': graph,
        'visibility': visibility,
        'visibility_json': ujson.dumps(visibility),
    }
    return context


def make_preview_response(maker: sessionmaker,
                          web_query: WebQuery,
                          uuid: str,
                          abort_callback: Callable) -> Dict[str, Any]:
    """Create context for preview request."""
    with operations.session_scope(maker) as session:
        meta = app_database.get_meta(session, uuid) or abort_callback()
        uuids = _get_group_uuids(meta)
        _next, _previous, paginator = _build_paginator(uuids, meta.uuid)

        all_tags = {
            *[x.value for x in meta.group.theme.tags],
            *[x.value for x in meta.group.tags],
            *[x.value for x in meta.tags],
        }
        session.expunge_all()

    context = {
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'paginator': paginator,
        'next': _next,
        'previous': _previous,
        'meta': meta,
        'tags': sorted(all_tags),
    }
    return context


def _get_group_uuids(meta: models.Meta) -> List[str]:
    """Gather all uuids in this group."""
    if meta.group.route == constants.NO_GROUP:
        return []

    return [x.uuid for x in meta.group.metas]


def _build_paginator(group_uuids: List[str], current_uuid: str) \
        -> Tuple[Optional[str], Optional[str], Paginator]:
    """Create Paginator instance that will help browsing group."""
    current_page = 0
    _next = None
    _previous = None
    for i, each_uuid in enumerate(group_uuids, start=1):
        if each_uuid == current_uuid:
            current_page = i

            if i > 1:
                _previous = group_uuids[i - 2]

            if i < len(group_uuids):
                _next = group_uuids[i]

            break

    paginator = Paginator(group_uuids,
                          current_page=current_page,
                          items_per_page=1)

    return _next, _previous, paginator


def make_tags_response(maker: sessionmaker,
                       web_query: WebQuery) -> Dict[str, Any]:
    """Create context for tags request."""
    with operations.session_scope(maker) as session:
        graph = app_database.get_graph(session)
        unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
        active_themes = extract_active_themes(unsafe_themes, graph)
        statistic = app_database.get_statistic(session, active_themes)

    context = {
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'statistic': statistic,
    }
    return context


def get_note_for_search(total: int, duration: float) -> str:
    """Return description of search duration."""
    total = utils.sep_digits(total)
    duration = '{:0.4f}'.format(duration)
    note = f'Found {total} records in {duration} seconds'
    return note


def get_placeholder_for_search(session: Session,
                               active_themes: Optional[Set[str]]) -> str:
    """Return placeholder for search input."""
    if active_themes is None:
        return ''

    if len(active_themes) == 1:
        current_theme = list(active_themes)[0]
        theme_name = app_database.get_theme_name(session, current_theme)
        placeholder = 'Searching on {}'.format(repr(theme_name))
    elif len(active_themes) > 1:
        placeholder = 'Searching on {}-x themes'.format(len(active_themes))
    else:
        placeholder = 'No active theme'

    return placeholder


def extract_active_themes(raw_themes: str, graph: dict) -> Optional[Set[str]]:
    """Safely parse and extract theme uuids."""
    if raw_themes != constants.ALL_THEMES:
        active_themes = set()
        candidates = [
            x.strip()
            for x in constants.THEMES_SEPARATION.split(raw_themes)
        ]

        for candidate in candidates:
            if is_correct_theme_uuid(candidate):
                active_themes.add(candidate)
    else:
        active_themes = None

    if active_themes == ['']:
        active_themes = None

    existing_themes = set(graph.keys())
    if active_themes == existing_themes:
        active_themes = None

    return active_themes


def is_correct_theme_uuid(uuid: str) -> bool:
    """Return True if uuid is valid and does not look like SQL injection."""
    if len(uuid) != constants.UUID_LEN:
        return False
    return constants.STRICT_THEME_UUID_PATTERN.match(uuid)


def save_feedback(folder: str, name: str, feedback: str) -> None:
    """Save user feedback.

    Temporary way, this design is terrible.
    """
    moment = datetime.datetime.now()

    payload = {
        'moment': str(moment),
        'name': str(name)[:constants.MAX_TEXT_INPUT_SIZE],
        'feedback': str(feedback)[:constants.MAX_TEXT_INPUT_SIZE],
    }
    text = json.dumps(payload, ensure_ascii=False)
    path = f'{folder}/feedback.txt'

    try:
        with open(path, mode='a', encoding='utf-8') as file:
            file.write(text + '\n')
    except Exception as exc:
        print(f'Failed to save feedback because of: {exc}')
