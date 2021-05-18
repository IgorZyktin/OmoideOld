# -*- coding: utf-8 -*-

"""Tests.
"""

import pytest

from omoide.search_engine.class_statistics import Statistics


@pytest.fixture
def statistics_fixture():
    inst = Statistics()
    inst.add('2021-10-01', 25, ['alpha', 'beta', 'gamma'])
    inst.add('2021-06-14', 250, ['alpha', 'cat', 'dog', 'fish'])
    inst.add('2021-02-28', 780, ['beta', 'home', 'ball', 'trust'])
    return inst


def test_statistics_creation(statistics_fixture):
    assert str(statistics_fixture) == '<Statistics, n=3>'


def test_statistics_as_dict(statistics_fixture):
    assert statistics_fixture.as_dict() == {
        'max_date': '2021-10-01',
        'min_date': '2021-02-28',
        'tags': {'alpha': 2,
                 'ball': 1,
                 'beta': 2,
                 'cat': 1,
                 'dog': 1,
                 'fish': 1,
                 'gamma': 1,
                 'home': 1,
                 'trust': 1},
        'total_items': 3,
        'total_size': 1055,
    }


def test_statistics_tags_by_frequency(statistics_fixture):
    assert statistics_fixture.tags_by_frequency == [
        ('alpha', 2),
        ('beta', 2),
        ('ball', 1),
        ('cat', 1),
        ('dog', 1),
        ('fish', 1),
        ('gamma', 1),
        ('home', 1),
        ('trust', 1),
    ]


def test_statistics_tags_by_alphabet(statistics_fixture):
    assert statistics_fixture.tags_by_alphabet == [
        ('A', ['alpha']),
        ('B', ['ball', 'beta']),
        ('C', ['cat']),
        ('D', ['dog']),
        ('F', ['fish']),
        ('G', ['gamma']),
        ('H', ['home']),
        ('T', ['trust']),
    ]


def test_statistics_sum(statistics_fixture):
    assert statistics_fixture.as_dict() == {
        'max_date': '2021-10-01',
        'min_date': '2021-02-28',
        'tags': {'alpha': 2,
                 'ball': 1,
                 'beta': 2,
                 'cat': 1,
                 'dog': 1,
                 'fish': 1,
                 'gamma': 1,
                 'home': 1,
                 'trust': 1},
        'total_items': 3,
        'total_size': 1055,
    }

    assert (statistics_fixture
            + statistics_fixture
            + statistics_fixture).as_dict() == {
               'max_date': '2021-10-01',
               'min_date': '2021-02-28',
               'tags': {'alpha': 6,
                        'ball': 3,
                        'beta': 6,
                        'cat': 3,
                        'dog': 3,
                        'fish': 3,
                        'gamma': 3,
                        'home': 3,
                        'trust': 3},
               'total_items': 9,
               'total_size': 3165,
           }


def test_statistics_not_implemented(statistics_fixture):
    with pytest.raises(TypeError):
        statistics_fixture + 25
