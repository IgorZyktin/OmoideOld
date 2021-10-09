# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide.search_engine.class_query import Query


@pytest.fixture
def query_sequence():
    return [
        ('+', 'and_this'),
        ('-', 'not_this'),
        ('|', 'or_this'),
        ('|', 'or_that'),
        ('+', 'and_that'),
    ]


@pytest.fixture
def query(query_sequence):
    return Query(and_=frozenset(['and_this', 'and_that']),
                 or_=frozenset(['or_this', 'or_that']),
                 not_=frozenset(['not_this']),
                 sequence=query_sequence)


@pytest.fixture
def empty_query():
    return Query(and_=frozenset(),
                 or_=frozenset(),
                 not_=frozenset(),
                 sequence=[])


@pytest.fixture
def query_valid_dict():
    return {'and_': ['and_that', 'and_this'],
            'or_': ['or_that', 'or_this'],
            'not_': ['not_this']}


def test_query_contains(query, empty_query):
    assert 'and_this' in query.and_
    assert 'unknown' not in empty_query.or_

    assert query
    assert not empty_query


def test_query_as_dict(query, empty_query, query_valid_dict):
    assert query.as_dict() == query_valid_dict

    assert empty_query.as_dict() == {'and_': [],
                                     'or_': [],
                                     'not_': []}


def test_query_as_keywords(query, empty_query):
    assert query.as_keywords() == {'and_': ['+ and_that', '+ and_this'],
                                   'or_': ['| or_that', '| or_this'],
                                   'not_': ['- not_this']}

    assert empty_query.as_keywords() == {'and_': [],
                                         'or_': [],
                                         'not_': []}


def test_query_as_keyword_pairs(query, empty_query):
    assert query.as_keyword_pais() == {
        'and_': [('+', 'and_that'), ('+', 'and_this')],
        'not_': [('-', 'not_this')],
        'or_': [('|', 'or_that'), ('|', 'or_this')]
    }

    assert empty_query.as_keyword_pais() == {'and_': [],
                                             'or_': [],
                                             'not_': []}


def test_query_repr(query, empty_query):
    assert repr(query) == '<Query, n=5>'
    assert repr(empty_query) == '<Query, n=0>'


def test_query_str(query, empty_query):
    assert str(query) == (
        '+ and_that + and_this | or_that | or_this - not_this'
    )
    assert str(empty_query) == ''


def test_query_append_and(query, query_valid_dict):
    assert query.as_dict() == query_valid_dict

    new_query = query.append_and('new', 'word')

    assert new_query is not query
    assert new_query.as_dict() == {
        'and_': ['and_that', 'and_this', 'new', 'word'],
        'not_': ['not_this'],
        'or_': ['or_that', 'or_this']
    }


def test_query_append_or(query, query_valid_dict):
    assert query.as_dict() == query_valid_dict

    new_query = query.append_or('new', 'word')

    assert new_query is not query
    assert new_query.as_dict() == {
        'and_': ['and_that', 'and_this'],
        'or_': ['new', 'or_that', 'or_this', 'word'],
        'not_': ['not_this'],
    }


def test_query_append_not(query, query_valid_dict):
    assert query.as_dict() == query_valid_dict

    new_query = query.append_not('new', 'word')

    assert new_query is not query
    assert new_query.as_dict() == {
        'and_': ['and_that', 'and_this'],
        'or_': ['or_that', 'or_this'],
        'not_': ['new', 'not_this', 'word'],
    }
