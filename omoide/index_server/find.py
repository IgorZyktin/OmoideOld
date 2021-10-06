# -*- coding: utf-8 -*-

"""Actual search operations.
"""
import random
import time
from typing import TypeVar

from omoide import utils
from omoide.index_server import objects
from omoide.index_server import search_engine

T = TypeVar('T')


def random_records(query: objects.Query,
                   index: search_engine.Index) -> objects.SearchResult:
    """Select random X records from the index."""
    total = utils.sep_digits(len(index.all_uuids))
    report = [f'Found {total} records in index.']

    if query.themes is not None and len(query.themes) == 0:
        chosen_records = []
    elif query.themes is not None and len(query.themes) != 0:
        chosen_records = random_records_for_some_themes(query, index, report)
    else:
        chosen_records = random_records_for_all_themes(query, index, report)

    return objects.SearchResult(
        items=[x.dict() for x in chosen_records if x is not None],
        report=report,
        page=1,
        has_more=False,
    )


def random_records_for_some_themes(query: objects.Query,
                                   index: search_engine.Index,
                                   report: list[str]
                                   ) -> list[search_engine.ShallowMeta]:
    """Select random X records from the index only for specific themes."""
    target_uuids = _filter_themes(query, index, report)

    # note that size of the index might be smaller than
    # amount and random.sample will throw exception
    start = time.perf_counter()
    adequate_amount = min(query.items_per_page, len(target_uuids))
    chosen_uuids = random.sample(tuple(target_uuids), adequate_amount)
    chosen_records = [index.by_uuid.get(x) for x in chosen_uuids]
    duration = time.perf_counter() - start
    report.append(f'Complete shuffling in {duration:0.4f} sec.')
    return chosen_records


def random_records_for_all_themes(query: objects.Query,
                                  index: search_engine.Index,
                                  report: list[str]
                                  ) -> list[search_engine.ShallowMeta]:
    """Select random N records from the index for all themes."""
    start = time.perf_counter()
    # note that size of the index might be smaller than
    # amount and random.sample will throw exception
    adequate_amount = min(query.items_per_page, len(index))
    chosen_records = random.sample(index.all_metas, adequate_amount)
    duration = time.perf_counter() - start
    report.append(f'Complete shuffling in {duration:0.4f} sec.')
    return chosen_records


def specific_records(query: objects.Query,
                     index: search_engine.Index) -> objects.SearchResult:
    """Return all records, that match to a given query."""
    target_uuids = index.all_uuids
    total = utils.sep_digits(len(target_uuids))
    report = [f'Found {total} records in index.']

    if query.themes is not None and len(query.themes) != 0:
        target_uuids = _filter_themes(query, index, report)
    else:
        target_uuids = index.all_uuids

    if query.or_:
        target_uuids = _do_or(target_uuids, query, index, report)

    if query.and_:
        target_uuids = _do_and(target_uuids, query, index, report)

    if query.not_:
        target_uuids = _do_not(target_uuids, query, index, report)

    # -------------------------------------------------------------------------

    start = time.perf_counter()
    chosen_records = [
        value
        for x in target_uuids
        if (value := index.by_uuid.get(x)) is not None
    ]
    chosen_records.sort(key=lambda meta: meta.number)
    duration = time.perf_counter() - start
    report.append(f'Complete sorting in {duration:0.4f} sec.')

    page = get_max_page(len(chosen_records), query.page, query.items_per_page)
    section, has_more = paginate(
        sequence=chosen_records,
        page=page,
        items_per_page=query.items_per_page,
    )

    return objects.SearchResult(
        items=[x.dict() for x in section],
        report=report,
        page=page,
        has_more=has_more,
    )


def _filter_themes(query: objects.Query, index: search_engine.Index,
                   report: list[str]) -> set[str]:
    """Exclude themes from search."""
    start = time.perf_counter()
    target_uuids = index.all_uuids

    temporary_or_ = set()
    for theme_uuid in query.themes:
        with_theme = index.get_by_tag(theme_uuid)
        if with_theme:
            temporary_or_ = temporary_or_.union(with_theme)

    if temporary_or_:
        target_uuids = target_uuids.intersection(temporary_or_)

    total = utils.sep_digits(len(target_uuids))
    duration = time.perf_counter() - start

    total_themes = utils.sep_digits(len(query.themes))
    report.append(f'Found {total} records for {total_themes} '
                  f'themes in {duration:0.4f} sec.')
    return target_uuids


def _do_or(target_uuids: set[str], query: objects.Query,
           index: search_engine.Index, report: list[str]) -> set[str]:
    """Perform OR operation."""
    or_start = time.perf_counter()
    actually_filtered = False
    temporary_or_ = set()
    for tag in query.or_:
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        if with_tag:
            actually_filtered = True
            temporary_or_ = temporary_or_.union(with_tag)
            duration = time.perf_counter() - start
            total = utils.sep_digits(len(with_tag))
            report.append(f'> Found {total} records by '
                          f'tag {tag!r} in {duration:0.4f} sec.')
    if temporary_or_:
        target_uuids = target_uuids.intersection(temporary_or_)

    if actually_filtered:
        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - or_start
        report.append(
            f'Found {total} records after OR in {duration:0.4f} sec.'
        )
    return target_uuids


def _do_and(target_uuids: set[str], query: objects.Query,
            index: search_engine.Index, report: list[str]) -> set[str]:
    """Perform AND operation."""
    and_start = time.perf_counter()
    actually_filtered = False
    for tag in query.and_:
        actually_filtered = True
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        target_uuids = target_uuids.intersection(with_tag)
        duration = time.perf_counter() - start
        total = utils.sep_digits(len(with_tag))
        report.append(f'> Found {total} records '
                      f'by tag {tag!r} in {duration:0.4f} sec.')

    if actually_filtered:
        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - and_start
        report.append(
            f'Found {total} records after AND in {duration:0.4f} sec.'
        )
    return target_uuids


def _do_not(target_uuids: set[str], query: objects.Query,
            index: search_engine.Index, report: list[str]) -> set[str]:
    """Perform NOT operation."""
    not_start = time.perf_counter()
    actually_filtered = False
    for tag in query.not_:
        start = time.perf_counter()
        with_tag = index.get_by_tag(tag)
        if with_tag:
            actually_filtered = True
            target_uuids -= with_tag
            duration = time.perf_counter() - start
            total = utils.sep_digits(len(with_tag))
            report.append(f'> Found {total} records '
                          f'by tag {tag!r} in {duration:0.4f} sec.')

    if actually_filtered:
        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - not_start
        report.append(
            f'Found {total} records after NOT in {duration:0.4f} sec.'
        )
    return target_uuids


def get_max_page(total: int, page: int, items_per_page: int) -> int:
    """Calculate maximum page depending on amount of items."""
    possible_max_page = total // items_per_page
    return min(page, possible_max_page)


def paginate(sequence: list[T], page: int,
             items_per_page: int) -> tuple[list[T], bool]:
    """Extract specific page elements from sequence."""
    left = (page - 1) * items_per_page
    right = left + items_per_page
    return sequence[left:right], bool(sequence[right:])
