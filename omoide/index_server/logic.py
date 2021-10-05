# -*- coding: utf-8 -*-
"""Service logic implementation.
"""
import asyncio
import concurrent
import sys
import time
from collections import defaultdict

import sqlalchemy
from pympler import asizeof

from omoide import utils
from omoide.index_server import find, singleton, status
from omoide.index_server import objects
from omoide.index_server import structures


def search(query: objects.Query,
           index: structures.Index) -> objects.SearchResult:
    """Perform fast search using index."""
    if query:
        result = find.specific_records(query, index)
    else:
        result = find.random_records(query, index)
    return result


async def format_status(state: singleton.Singleton) -> dict:
    """Format server state as a dictionary."""
    server_size = state.process.memory_info()[0]
    return state.status.make_report(
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

    # can potentially create race condition
    state.index = index


def index_pipeline(db_path: str) -> tuple[structures.Index, dict]:
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


def create_index(parts: list[tuple], tags: list[tuple]) -> structures.Index:
    """Instantiate index from its components."""
    all_metas = [
        structures.ShallowMeta(
            uuid=uuid,
            number=number,
            path_to_thumbnail=path,
        )
        for uuid, number, path in parts
    ]

    by_tags = defaultdict(set)
    for tag, uuid in tags:
        by_tags[sys.intern(tag.lower())].add(sys.intern(uuid))

    index = structures.Index(
        all_metas=all_metas,
        by_tags={
            tag: frozenset(uuids)
            for tag, uuids in by_tags.items()
        },
    )

    parts.clear()
    tags.clear()

    return index


def analyze_index(index: structures.Index) -> dict:
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
