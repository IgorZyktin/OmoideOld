# -*- coding: utf-8 -*-

"""Tests.
"""
import pytest

from omoide.search_engine.class_query import Query
from omoide.search_engine.class_query_builder import QueryBuilder


@pytest.fixture
def query_builder():
    return QueryBuilder(Query)


@pytest.fixture
def empty_query_dict():
    return {
        'and_': [],
        'or_': [],
        'not_': [],
    }


def test_query_builder_split_query(query_builder):
    f = query_builder.split_request_into_parts
    assert f('cats | dogs') == ['|', 'cats', '|', 'dogs']
    assert f('a + b - c') == ['|', 'a', '+', 'b', '-', 'c']


def test_query_builder_1(query_builder):
    text = 'cats | dogs'
    query = query_builder.from_query(text)

    assert query.as_dict() == {'and_': [],
                               'or_': ['cats', 'dogs'],
                               'not_': []}
    assert str(query) == '| cats | dogs'
    assert query.sequence == (('or', 'cats'), ('or', 'dogs'))


def test_query_builder_2(query_builder):
    text = '+ cats | dogs + turtle - frog'
    query = query_builder.from_query(text)

    assert query.as_dict() == {'and_': ['cats', 'turtle'],
                               'or_': ['dogs'],
                               'not_': ['frog']}
    assert str(query) == '+ cats + turtle | dogs - frog'
    assert query.sequence == (('and', 'cats'),
                              ('or', 'dogs'),
                              ('and', 'turtle'),
                              ('not', 'frog'))


def test_query_builder_3(query_builder):
    text = '|fly +fish -spiders'
    query = query_builder.from_query(text)
    assert query.as_dict() == {
        'and_': ['fish'],
        'or_': ['fly'],
        'not_': ['spiders'],
    }
    assert str(query) == '+ fish | fly - spiders'
    assert query.sequence == (
        ('or', 'fly'), ('and', 'fish'), ('not', 'spiders')
    )


def test_query_builder_wrong(query_builder):
    text = 'cats + - dogs'
    query = query_builder.from_query(text)
    assert str(query) == '+ - dogs | cats'
    assert query.sequence == (('or', 'cats'), ('and', '- dogs'))


def test_query_builder_empty(query_builder, empty_query_dict):
    text = ''
    query = query_builder.from_query(text)
    assert query.as_dict() == empty_query_dict
    assert str(query) == ''
