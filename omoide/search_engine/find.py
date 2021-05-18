# -*- coding: utf-8 -*-

"""Actual search operations.
"""
import random
import time
from typing import List, Tuple, Set, Optional

from omoide import search_engine
from omoide import utils


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def random_records(index: search_engine.Index,
                   active_themes: Optional[Set[str]],
                   amount: int
                   ) -> Tuple[List[search_engine.ShallowMeta], List[str]]:
    """Select random X records from index."""
    target_uuids = index.all_uuids

    total = utils.sep_digits(len(target_uuids))
    report = [f'Found {total} records in index.']

    if active_themes is not None:
        themes_start = time.perf_counter()
        total_themes = utils.sep_digits(len(active_themes))
        temporary_or_ = set()
        for theme_uuid in active_themes:
            with_theme = index.get_by_tag(theme_uuid)
            if with_theme:
                temporary_or_ = temporary_or_.union(with_theme)

        if temporary_or_:
            target_uuids = target_uuids.intersection(temporary_or_)

        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - themes_start
        report.append(f'Found {total} records on {total_themes} '
                      f'themes in {duration:0.4f} sec.')

        # note that size of the index might be smaller than
        # amount and random.sample will throw and exception
        shuffling_start = time.perf_counter()
        adequate_amount = min(amount, len(target_uuids))
        chosen_uuids = random.sample(tuple(target_uuids), adequate_amount)
        chosen_records = [index.by_uuid[x] for x in chosen_uuids]

        duration = time.perf_counter() - shuffling_start
        report.append(f'Complete shuffling in {duration:0.4f} sec.')

    else:
        shuffling_start = time.perf_counter()
        adequate_amount = min(amount, len(index))
        chosen_records = random.sample(index.all_metas, adequate_amount)

        duration = time.perf_counter() - shuffling_start
        report.append(f'Complete shuffling in {duration:0.4f} sec.')

    return chosen_records, report


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def specific_records(query: search_engine.Query,
                     index: search_engine.Index,
                     active_themes: Set[str]) \
        -> Tuple[List[search_engine.ShallowMeta], List[str]]:
    """Return all records, that match to a given query."""
    target_uuids = index.all_uuids
    total = utils.sep_digits(len(target_uuids))
    report = [f'Found {total} records in index.']

    if active_themes is not None and active_themes:
        themes_start = time.perf_counter()
        total_themes = utils.sep_digits(len(active_themes))
        temporary_or_ = set()
        for theme_uuid in active_themes:
            with_theme = index.get_by_tag(theme_uuid)
            if with_theme:
                temporary_or_ = temporary_or_.union(with_theme)

        if temporary_or_:
            target_uuids = target_uuids.intersection(temporary_or_)

        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - themes_start
        report.append(f'Found {total} records on {total_themes} '
                      f'themes in {duration:0.4f} sec.')

    # OR ----------------------------------------------------------------------

    if query.or_:
        or_start = time.perf_counter()
        temporary_or_ = set()
        for tag in query.or_:
            start = time.perf_counter()
            with_tag = index.get_by_tag(tag)
            if with_tag:
                temporary_or_ = temporary_or_.union(with_tag)
                duration = time.perf_counter() - start
                total = utils.sep_digits(len(with_tag))
                report.append('> Found {} records '
                              'by tag {} in {:0.4f} sec.'.format(total,
                                                                 repr(tag),
                                                                 duration))
        if temporary_or_:
            target_uuids = target_uuids.intersection(temporary_or_)

        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - or_start
        report.append(
            f'Found {total} records after OR in {duration:0.4f} sec.'
        )

    # AND ---------------------------------------------------------------------

    if query.and_:
        and_start = time.perf_counter()
        for tag in query.and_:
            start = time.perf_counter()
            with_tag = index.get_by_tag(tag)
            target_uuids = target_uuids.intersection(with_tag)
            duration = time.perf_counter() - start
            total = utils.sep_digits(len(with_tag))
            report.append('> Found {} records '
                          'by tag {} in {:0.4f} sec.'.format(total,
                                                             repr(tag),
                                                             duration))
        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - and_start
        report.append(
            f'Found {total} records after AND in {duration:0.4f} sec.'
        )

    # NOT ---------------------------------------------------------------------

    if query.not_:
        not_start = time.perf_counter()
        for tag in query.not_:
            start = time.perf_counter()
            with_tag = index.get_by_tag(tag)
            if with_tag:
                target_uuids -= with_tag
                duration = time.perf_counter() - start
                total = utils.sep_digits(len(with_tag))
                report.append('> Found {} records '
                              'by tag {} in {:0.4f} sec.'.format(total,
                                                                 repr(tag),
                                                                 duration))
        total = utils.sep_digits(len(target_uuids))
        duration = time.perf_counter() - not_start
        report.append(
            f'Found {total} records after NOT in {duration:0.4f} sec.'
        )

    # -------------------------------------------------------------------------

    sort_start = time.perf_counter()
    chosen_records = [index.by_uuid[x] for x in target_uuids]
    chosen_records.sort(key=lambda meta: meta.number)
    duration = time.perf_counter() - sort_start
    report.append(f'Complete sorting in {duration:0.4f} sec.')

    return chosen_records, report
