# -*- coding: utf-8 -*-
"""Business logic of the service.
"""
import datetime
import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional, Set, List, Tuple

import aiohttp
import ujson
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from omoide import constants
from omoide import search_engine
from omoide import utils
from omoide.app_server.class_web_query import WebQuery
from omoide.application import database as app_database
from omoide.application.class_paginator import Paginator, Paginator2
from omoide.database import models
from omoide.index_server import constants as index_constants

_GRAPH_CACHE: Optional[Dict[str, Any]] = None
INDEX_URL = f'http://{index_constants.HOST}:{index_constants.PORT}/search'


@dataclass
class IndexItem:
    uuid: str
    path: str
    number: int


@dataclass
class IndexResponse:
    items: list[IndexItem]
    report: list[str]
    time: float
    page: int
    total_pages: int
    total_items: int
    announce: str


# pylint: disable=too-many-locals
async def make_search_response(session: AsyncSession,
                               web_query: WebQuery,
                               query_builder: search_engine.QueryBuilder
                               ) -> Dict[str, Any]:
    """Create context for search request."""
    start = time.perf_counter()

    graph = await app_database.get_graph(session)
    unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
    active_themes = extract_active_themes(unsafe_themes, graph)
    placeholder = await get_placeholder_for_search(session, active_themes)
    user_query = web_query.get('q')
    user_query = aggressively_filter(user_query)
    current_page = int(web_query.get('page', '1'))
    search_query = query_builder.from_query(user_query)

    if not active_themes and active_themes is not None:
        response = IndexResponse([], ['No themes to search on.'],
                                 0.0, 0, 0, 0, '')
    else:
        async with aiohttp.ClientSession(conn_timeout=1.0) as session:
            payload = {
                'and_': list(search_query.and_),
                'or_': list(search_query.or_),
                'not_': list(search_query.not_),
                'page': current_page,
                'items_per_page': constants.ITEMS_PER_PAGE,
                'themes': active_themes,
            }
            async with session.get(INDEX_URL, json=payload) as response:
                body = await response.text()
                response = parse_index_response(body)

    paginator = Paginator2(
        sequence=response.items,
        current_page=response.page,
        items_per_page=constants.ITEMS_PER_PAGE,
        pages_in_block=constants.PAGES_IN_BLOCK,
        total_items=response.total_items,
    )

    duration = time.perf_counter() - start
    note = get_note_for_search(len(paginator), duration)

    context = {
        'search_query': search_query,
        'paginator': paginator,
        'search_report': response.report,
        'note': note,
        'announce': response.announce,
        'placeholder': placeholder,
    }
    return context


async def make_navigation_response(session: AsyncSession,
                                   web_query: WebQuery) -> Dict[str, Any]:
    """Create context for navigation request (GET)."""
    graph = await app_database.get_graph(session)
    unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
    active_themes = extract_active_themes(unsafe_themes, graph)

    if active_themes is None:
        visibility = {x: True for x in graph}
        web_query['active_themes'] = constants.ALL_THEMES
    else:
        visibility = {x: (x in active_themes) for x in graph}

    return {
        'graph': graph,
        'visibility': visibility,
        'visibility_json': ujson.dumps(visibility),
    }


async def make_preview_response(session: AsyncSession,
                                web_query: WebQuery,
                                uuid: str,
                                abort_callback: Callable) -> Dict[str, Any]:
    """Create context for preview request."""
    meta = await app_database.get_meta(session, uuid)
    group = await app_database.get_group(session, meta.group_uuid)

    if not meta or not group:
        return abort_callback()

    theme = await app_database.get_theme(session, group.theme_uuid)

    if not theme:
        return abort_callback()

    uuids = await _get_group_uuids(session, group)
    _next, _previous, paginator = _build_paginator(uuids, meta.uuid)

    all_tags = await app_database.get_all_tags(session, theme.uuid,
                                               group.uuid, meta.uuid)
    session.expunge_all()

    response = {
        'uuid': meta.uuid,
        'folded': web_query.get('folded') == 'yes',
        'paginator': paginator,
        'next': _next,
        'previous': _previous,
        'meta': meta,
        'group': group,
        'theme': theme,
        'tags': sorted(all_tags),
    }
    return response


async def _get_group_uuids(session: AsyncSession,
                           group: models.Group) -> List[str]:
    """Gather all uuids in this group."""
    if group.route == constants.NO_GROUP:
        return []

    return await app_database.get_group_metas_uuids(session, group.uuid)


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
                          items_per_page=1,
                          pages_in_block=constants.PAGES_IN_BLOCK)

    return _next, _previous, paginator


async def make_tags_response(session: AsyncSession,
                             web_query: WebQuery) -> Dict[str, Any]:
    """Create context for tags request."""
    graph = await app_database.get_graph(session)
    unsafe_themes = web_query.get('active_themes', constants.ALL_THEMES)
    active_themes = extract_active_themes(unsafe_themes, graph)
    statistic = await app_database.get_statistic(session, active_themes)

    response = {
        'statistic': statistic,
    }
    return response


async def make_newest_response(session: Session) -> dict[str, Any]:
    """Create context for newest request."""
    last_update, groups = await app_database.get_newest_groups(session)
    return {
        'last_update': last_update,
        'newest': groups,
    }


def get_note_for_search(total: int, duration: float) -> str:
    """Return description of search duration."""
    total = utils.sep_digits(total)
    duration = '{:0.4f}'.format(duration)
    note = f'Found {total} records in {duration} seconds'
    return note


async def get_placeholder_for_search(session: AsyncSession,
                                     active_themes: Optional[Set[str]]) -> str:
    """Return placeholder for search input."""
    if active_themes is None:
        return ''

    if len(active_themes) == 1:
        current_theme = list(active_themes)[0]
        theme_name = await app_database.get_theme_name(session, current_theme)
        placeholder = 'Searching on {}'.format(repr(theme_name))
    elif len(active_themes) > 1:
        placeholder = 'Searching on {}-x themes'.format(len(active_themes))
    else:
        placeholder = 'No active theme'

    return placeholder


def extract_active_themes(raw_themes: str, graph: dict) -> Optional[Set[str]]:
    """Safely parse and extract theme uuids."""
    raw_themes = aggressively_filter(raw_themes)

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


def save_feedback(folder: str, name: str, feedback: str, path: str) -> None:
    """Save user feedback.

    Temporary way, this design is terrible.
    """
    moment = datetime.datetime.now()

    payload = {
        'moment': str(moment),
        'name': str(name)[:constants.MAX_TEXT_INPUT_SIZE],
        'feedback': str(feedback)[:constants.MAX_TEXT_INPUT_SIZE],
        'path': str(path)[:constants.MAX_TEXT_INPUT_SIZE],
    }
    text = json.dumps(payload, ensure_ascii=False)
    path = f'{folder}/feedback.txt'

    with open(path, mode='a', encoding='utf-8') as file:
        try:
            file.write(text + '\n')
        except Exception as exc:
            file.write(f'Failed to save feedback because of: {exc}\n')


def aggressively_filter(string: str) -> str:
    """Drop all unwanted characters. Extremely strict filter.

    >>> aggressively_filter('Dude, where is my car?!')
    'Dude, where is my car'
    """
    if not string:
        return ''

    letters = list(string)
    for i, letter in enumerate(letters):
        if letter not in constants.ALLOWED_SYMBOLS:
            letters[i] = ''

    return ''.join(letters)


def parse_index_response(body: str) -> IndexResponse:
    """Convert index response into objects."""
    payload = ujson.loads(body)
    items = [IndexItem(**x) for x in payload.get('items', [])]

    return IndexResponse(
        items=items,
        report=payload.get('report', []),
        time=payload.get('time', -1.0),
        page=payload.get('page', -1),
        total_pages=payload.get('total_pages', -1),
        total_items=payload.get('total_items', -1),
        announce=payload.get('announce', ''),
    )
