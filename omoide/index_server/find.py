# -*- coding: utf-8 -*-

"""Actual search operations.
"""
import math
import random
import time
from typing import TypeVar

from omoide import utils
from omoide.index_server import objects
from omoide.index_server import search_engine

T = TypeVar('T')


async def random_records(query: objects.Query,
                         index: search_engine.Index) -> objects.SearchResult:
    """Select random X records from the index."""
    start = time.perf_counter()
    total = utils.sep_digits(len(index))
    report = [f'Found {total} records in index.']

    if query.themes is not None and len(query.themes) == 0:
        chosen_records = []

    elif query.themes is not None and len(query.themes) != 0:
        chosen_records = await random_records_for_some_themes(query,
                                                              index, report)
    else:
        chosen_records = await random_records_for_all_themes(query,
                                                             index, report)

    duration = time.perf_counter() - start
    items = [x.dict() for x in chosen_records if x is not None]

    return objects.SearchResult(
        items=items,
        report=report,
        time=duration,
        page=1,
        total_pages=1,
        total_items=len(items),
        has_more=False,
    )


async def random_records_for_some_themes(query: objects.Query,
                                         index: search_engine.Index,
                                         report: list[str]
                                         ) -> list[search_engine.ShallowMeta]:
    """Select random X records from the index only for specific themes."""
    target_records = await _filter_themes(query, index, report)

    # note that size of the index might be smaller than
    # amount and random.sample will throw exception
    start = time.perf_counter()
    adequate_amount = min(query.items_per_page, len(target_records))
    chosen_records = random.sample(tuple(target_records), adequate_amount)
    duration = time.perf_counter() - start

    report.append(f'Complete shuffling in {duration:0.5f} sec.')
    return chosen_records


async def random_records_for_all_themes(query: objects.Query,
                                        index: search_engine.Index,
                                        report: list[str]
                                        ) -> list[search_engine.ShallowMeta]:
    """Select random N records from the index for all themes."""
    start = time.perf_counter()
    # note that size of the index might be smaller than
    # amount and random.sample will throw exception
    adequate_amount = min(query.items_per_page, len(index))
    chosen_records = random.sample(index.all_metas_tuple, adequate_amount)
    duration = time.perf_counter() - start

    report.append(f'Complete shuffling in {duration:0.5f} sec.')
    return chosen_records


async def specific_records(query: objects.Query,
                           index: search_engine.Index) -> objects.SearchResult:
    """Return all records, that match to a given query."""
    full_start = time.perf_counter()
    target_records = index.all_metas_set
    total = utils.sep_digits(len(target_records))
    report = [f'Found {total} records in index.']

    if query.themes is not None and len(query.themes) != 0:
        target_records = await _filter_themes(query, index, report)
    else:
        target_records = index.all_metas_set

    if query.or_:
        target_records = await _do_or(target_records, query, index, report)

    if query.and_:
        target_records = await _do_and(target_records, query, index, report)

    if query.not_:
        target_records = await _do_not(target_records, query, index, report)

    # -------------------------------------------------------------------------

    start = time.perf_counter()
    chosen_records = sorted(target_records, key=lambda meta: meta.number)
    duration = time.perf_counter() - start
    report.append(f'Complete sorting in {duration:0.5f} sec.')

    page = await get_max_page(len(chosen_records),
                              query.page, query.items_per_page)

    section = await paginate(
        sequence=chosen_records,
        page=page,
        items_per_page=query.items_per_page,
    )
    total_pages = int(math.ceil(len(chosen_records) / query.items_per_page))
    full_duration = time.perf_counter() - full_start

    return objects.SearchResult(
        items=[x.dict() for x in section],
        report=report,
        time=full_duration,
        page=page,
        total_items=len(chosen_records),
        total_pages=total_pages,
    )


async def _filter_themes(query: objects.Query, index: search_engine.Index,
                         report: list[str]) -> set[search_engine.ShallowMeta]:
    """Exclude themes from search."""
    start = time.perf_counter()
    target_records = index.all_metas_set

    temporary_or_: set[search_engine.ShallowMeta] = set()
    for theme_uuid in query.themes:
        with_theme = index.get_by_tag(theme_uuid)
        if with_theme:
            temporary_or_ = temporary_or_.union(with_theme)

    if temporary_or_:
        target_records = target_records.intersection(temporary_or_)

    total = utils.sep_digits(len(target_records))
    duration = time.perf_counter() - start

    total_themes = utils.sep_digits(len(query.themes))
    report.append(f'Found {total} records for {total_themes} '
                  f'themes in {duration:0.5f} sec.')
    return target_records


async def _do_or(target_records: set[search_engine.ShallowMeta],
                 query: objects.Query, index: search_engine.Index,
                 report: list[str]) -> set[search_engine.ShallowMeta]:
    """Perform OR operation."""
    or_start = time.perf_counter()
    actually_filtered = False
    temporary_or_: set[search_engine.ShallowMeta] = set()
    for tag in query.or_:
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        if with_tag:
            actually_filtered = True
            temporary_or_ = temporary_or_.union(with_tag)
            duration = time.perf_counter() - start
            total = utils.sep_digits(len(with_tag))
            report.append(f'> Found {total} records by '
                          f'tag {tag!r} in {duration:0.5f} sec.')
    if temporary_or_:
        target_records = target_records.intersection(temporary_or_)

    if actually_filtered:
        total = utils.sep_digits(len(target_records))
        duration = time.perf_counter() - or_start
        report.append(
            f'Got {total} records after OR in {duration:0.5f} sec.'
        )
    return target_records


async def _do_and(target_records: set[search_engine.ShallowMeta],
                  query: objects.Query, index: search_engine.Index,
                  report: list[str]) -> set[search_engine.ShallowMeta]:
    """Perform AND operation."""
    and_start = time.perf_counter()
    actually_filtered = False
    for tag in query.and_:
        actually_filtered = True
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        target_records = target_records.intersection(with_tag)
        duration = time.perf_counter() - start
        total = utils.sep_digits(len(with_tag))
        report.append(f'> Found {total} records '
                      f'by tag {tag!r} in {duration:0.5f} sec.')

    if actually_filtered:
        total = utils.sep_digits(len(target_records))
        duration = time.perf_counter() - and_start
        report.append(
            f'Got {total} records after AND in {duration:0.5f} sec.'
        )
    return target_records


async def _do_not(target_records: set[search_engine.ShallowMeta],
                  query: objects.Query, index: search_engine.Index,
                  report: list[str]) -> set[search_engine.ShallowMeta]:
    """Perform NOT operation."""
    not_start = time.perf_counter()
    actually_filtered = False
    for tag in query.not_:
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        if with_tag:
            actually_filtered = True
            target_records -= with_tag
            duration = time.perf_counter() - start
            total = utils.sep_digits(len(with_tag))
            report.append(f'> Found {total} records '
                          f'by tag {tag!r} in {duration:0.5f} sec.')

    if actually_filtered:
        total = utils.sep_digits(len(target_records))
        duration = time.perf_counter() - not_start
        report.append(
            f'Got {total} records after NOT in {duration:0.5f} sec.'
        )
    return target_records


async def get_max_page(total: int, page: int, items_per_page: int) -> int:
    """Calculate maximum page depending on amount of items."""
    possible_max_page = int(math.ceil(total / items_per_page))
    return min(page, possible_max_page)


async def paginate(sequence: list[T], page: int,
                   items_per_page: int) -> list[T]:
    """Extract specific page elements from sequence."""
    left = (page - 1) * items_per_page
    right = left + items_per_page
    section = sequence[left:right]
    return section
