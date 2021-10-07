# -*- coding: utf-8 -*-
"""Service logic implementation.
"""
import asyncio
import concurrent
import sys
import time
import traceback
from collections import defaultdict

import sqlalchemy
from pympler import asizeof

from omoide import utils
from omoide.index_server import find
from omoide.index_server import objects
from omoide.index_server import search_engine
from omoide.index_server import singleton
from omoide.index_server import status


async def search(query: objects.Query,
                 state: singleton.Singleton) -> objects.SearchResult:
    """Perform fast search using index."""
    match state.status.index_status:
        case status.STATUS_INIT:
            announce = 'Please wait a few minutes for server init after reload'
        case status.STATUS_RELOADING:
            announce = ('New content is loading right now and '
                        'will be available in a few minutes')
        case _:
            announce = ''

    if query:
        result = await find.specific_records(query, state.index)
    else:
        result = await find.random_records(query, state.index)

    result.announce = announce
    return result


async def format_status(state: singleton.Singleton) -> dict:
    """Format server state as a dictionary."""
    server_size = state.process.memory_info()[0]
    return await state.status.make_report(
        now=utils.now(),
        server_size=utils.byte_count_to_text(server_size),
        version=state.version,
    )


async def reload(state: singleton.Singleton) -> None:
    """Quietly reload index without downtime."""
    start = time.perf_counter()
    state.status.index_status = status.STATUS_RELOADING
    loop = asyncio.get_event_loop()
    index = state.index

    # noinspection PyBroadException
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            index, params = await loop.run_in_executor(
                executor, index_pipeline, state.db_path)
    except Exception as exc:
        traceback.print_exc()
        print(f'Failed on db path: {state.db_path}')
        state.status.index_status = status.STATUS_FAILED
        state.status.index_comment = f'{type(exc)} {exc}'
        params = {}
    else:
        state.status.index_status = status.STATUS_ACTIVE
        state.status.index_comment = ''
    finally:
        stop = time.perf_counter()

    state.status.index_last_reload_duration = round(stop - start, 2)
    state.status.index_last_reload = utils.now()

    for param_name, param_value in params.items():
        setattr(state.status, param_name, param_value)

    state.index = index


def index_pipeline(db_path: str) -> tuple[search_engine.Index, dict]:
    """Process raw data into fully functional index."""
    parts, tags = actually_load_from_database(db_path)
    index = create_index(parts, tags)
    params = analyze_index(index)
    return index, params


def actually_load_from_database(db_path: str
                                ) -> tuple[list[tuple], list[tuple]]:
    """Load index components from database."""
    engine = sqlalchemy.create_engine(
        f'sqlite+pysqlite:///{db_path}?uri=true',
        echo=False,
        future=True,
    )

    stmt_parts = sqlalchemy.text("""
    SELECT meta_uuid, number, path_to_thumbnail 
    FROM index_metas
    ORDER BY number;
    """)

    stmt_tags = sqlalchemy.text("""
    SELECT tag, uuid 
    FROM index_tags
    ORDER BY id;
    """)

    with engine.begin() as conn:
        parts = conn.execute(stmt_parts).fetchall()
        tags = conn.execute(stmt_tags).fetchall()

    return list(parts), list(tags)


def create_index(parts: list[tuple], tags: list[tuple]) -> search_engine.Index:
    """Instantiate index from its components."""
    all_metas = [
        search_engine.ShallowMeta(
            uuid=uuid,
            number=number,
            path_to_thumbnail=path,
        )
        for uuid, number, path in parts
    ]

    by_tags = defaultdict(set)
    for tag, uuid in tags:
        # this optimisation can save up to 50% of the index size in bytes
        by_tags[sys.intern(tag.lower())].add(sys.intern(uuid))

    index = search_engine.Index(
        all_metas=all_metas,
        by_tags={
            tag: frozenset(uuids)
            for tag, uuids in by_tags.items()
        },
    )

    parts.clear()
    tags.clear()

    return index


def analyze_index(index: search_engine.Index) -> dict:
    """Format index parameters."""
    _size_bytes = asizeof.asizeof(index)
    index_records = len(index)
    index_buckets = len(index.by_tags)
    index_avg_bucket = round(index_records / (index_buckets or 1), 2)

    index_min_bucket = index_records
    index_max_bucket = 0
    for uuids in index.by_tags.values():
        total = len(uuids)
        if total > index_max_bucket:
            index_max_bucket = total
        if total < index_min_bucket:
            index_min_bucket = total

    return {
        'index_records': index_records,
        'index_buckets': index_buckets,
        'index_avg_bucket': index_avg_bucket,
        'index_min_bucket': index_min_bucket,
        'index_max_bucket': index_max_bucket,
        'index_size': utils.byte_count_to_text(_size_bytes),
    }
