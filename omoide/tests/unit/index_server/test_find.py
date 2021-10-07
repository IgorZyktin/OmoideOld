# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock
from unittest.mock import patch

from omoide.index_server import find


def test_find_random_empty_query_and_no_themes(fix_singleton,
                                               fix_empty_query,
                                               fix_index):
    # arrange
    query = fix_empty_query
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
        'has_more': False,
        'announce': '',
    }


def test_find_random_empty_query_and_all_themes(fix_singleton,
                                                fix_empty_query,
                                                fix_index):
    # arrange
    query = fix_empty_query
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
        'has_more': False,
        'announce': '',
    }
    assert len(result['items']) == query.items_per_page


def test_find_random_empty_query_and_some_themes(fix_singleton,
                                                 fix_empty_query,
                                                 fix_index):
    # arrange
    query = fix_empty_query
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
        'has_more': False,
        'announce': '',
    }
    assert len(result['items']) == query.items_per_page


def test_find_specific_all_themes(fix_singleton, fix_query, fix_index):
    # arrange
    query = fix_query
    index = fix_index

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
        'has_more': False,
        'announce': '',
    }


def test_find_specific_some_themes(fix_singleton, fix_query, fix_index):
    # arrange
    query = fix_query
    index = fix_index
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
        'has_more': False,
        'announce': '',
    }
