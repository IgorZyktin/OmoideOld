# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock

from omoide.index_server import logic


def test_index_server_report_formation(fix_singleton,
                                       fix_query,
                                       fix_index):
    # arrange
    state = fix_singleton
    state.index = fix_index
    query = fix_query
    query.and_ = ['animal']
    query.or_ = ['small']
    query.not_ = ['big']
    query.themes = ['animal', 'small', 'big']  # using tags as themes

    start = -1.0

    def get_fake_time():
        nonlocal start
        start += 1.0
        return start

    # act
    with mock.patch('omoide.index_server.find.time') as fake_time:
        fake_time.perf_counter = get_fake_time
        response = asyncio.run(logic.search(query, state))
        result = response.dict()

    # assert
    assert result['time'] == 17.0
    assert result['report'] == [
        "Found 9 records in index.",
        "Found 7 records for 3 themes in 1.00000 sec.",
        "> Found 2 records by tag 'small' in 1.00000 sec.",
        "Got 2 records after OR in 3.00000 sec.",
        "> Found 5 records by tag 'animal' in 1.00000 sec.",
        "Got 2 records after AND in 3.00000 sec.",
        "> Found 2 records by tag 'big' in 1.00000 sec.",
        "Got 2 records after NOT in 3.00000 sec.",
        "Complete sorting in 1.00000 sec."
    ]
