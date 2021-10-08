# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock
from unittest.mock import patch

from omoide.index_server import find


def test_index_server_find_random_empty_query_and_no_themes(fix_singleton,
                                                            fix_query,
                                                            fix_index):
    # arrange
    query = fix_query
    index = fix_index
    query.themes = []

    # act
    with patch('omoide.index_server.find.time.perf_counter', return_value=0.0):
        response = asyncio.run(find.random_records(query, index))
        result = response.dict()

    # assert
    assert result == {
        'items': [],
        'report': mock.ANY,
        'time': 0.0,
        'page': 1,
        'total_pages': 1,
        'total_items': 0,
        'announce': '',
    }


def test_index_server_find_random_empty_query_and_all_themes(fix_singleton,
                                                             fix_query,
                                                             fix_index):
    # arrange
    query = fix_query
    index = fix_index

    # act
    with patch('omoide.index_server.find.time.perf_counter', return_value=0.0):
        response = asyncio.run(find.random_records(query, index))
        result = response.dict()

    # assert
    assert result == {
        'items': mock.ANY,
        'report': mock.ANY,
        'time': 0.0,
        'page': 1,
        'total_pages': 1,
        'total_items': 4,
        'announce': '',
    }
    assert len(result['items']) == query.items_per_page


def test_index_server_find_random_empty_query_and_some_themes(fix_singleton,
                                                              fix_query,
                                                              fix_index):
    # arrange
    query = fix_query
    index = fix_index
    query.themes = ['animal']  # using tag as a theme

    # act
    with patch('omoide.index_server.find.time.perf_counter', return_value=0.0):
        response = asyncio.run(find.random_records(query, index))
        result = response.dict()

    # assert
    assert result == {
        'items': mock.ANY,
        'report': mock.ANY,
        'time': 0.0,
        'page': 1,
        'total_pages': 1,
        'total_items': 4,
        'announce': '',
    }
    assert len(result['items']) == query.items_per_page


def test_index_server_find_specific_all_themes(fix_singleton,
                                               fix_query,
                                               fix_index):
    # arrange
    query = fix_query
    index = fix_index
    query.and_ = ['animal']
    query.or_ = ['small']
    query.not_ = ['big']

    # act
    with patch('omoide.index_server.find.time.perf_counter', return_value=0.0):
        response = asyncio.run(find.specific_records(query, index))
        result = response.dict()

    # assert
    assert result == {
        'items': [{'number': 3, 'path': 'frog.jpg', 'uuid': 'u3'},
                  {'number': 4, 'path': 'ant.jpg', 'uuid': 'u4'}],
        'report': mock.ANY,
        'time': 0.0,
        'page': 1,
        'total_pages': 1,
        'total_items': 2,
        'announce': '',
    }


def test_index_server_find_specific_some_themes(fix_singleton,
                                                fix_query,
                                                fix_index):
    # arrange
    query = fix_query
    index = fix_index
    query.and_ = ['animal']
    query.or_ = ['small']
    query.not_ = ['big']
    query.themes = ['animal']  # using tag as a theme

    # act
    with patch('omoide.index_server.find.time.perf_counter', return_value=0.0):
        response = asyncio.run(find.specific_records(query, index))
        result = response.dict()

    # assert
    assert result == {
        'items': [{'number': 3, 'path': 'frog.jpg', 'uuid': 'u3'},
                  {'number': 4, 'path': 'ant.jpg', 'uuid': 'u4'}],
        'report': mock.ANY,
        'time': 0.0,
        'page': 1,
        'total_pages': 1,
        'total_items': 2,
        'announce': '',
    }
