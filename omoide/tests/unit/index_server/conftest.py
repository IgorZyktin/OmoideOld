# -*- coding: utf-8 -*-

"""Tests.
"""
import datetime
from unittest import mock

import pytest

from omoide import infra
from omoide.index_server import objects
from omoide.index_server import search_engine
from omoide.index_server import singleton
from omoide.index_server import status


@pytest.fixture
def fix_empty_index():
    return search_engine.Index(all_metas=[], by_tags={})


@pytest.fixture
def fix_index():
    all_metas = [
        search_engine.ShallowMeta('u1', 1, 'cat.jpg'),
        search_engine.ShallowMeta('u2', 2, 'dog.jpg'),
        search_engine.ShallowMeta('u3', 3, 'frog.jpg'),
        search_engine.ShallowMeta('u4', 4, 'ant.jpg'),
        search_engine.ShallowMeta('u5', 5, 'bird.jpg'),
        search_engine.ShallowMeta('u6', 6, 'box.jpg'),
        search_engine.ShallowMeta('u7', 7, 'building.jpg'),
        search_engine.ShallowMeta('u8', 8, 'river.jpg'),
        search_engine.ShallowMeta('u9', 9, 'sky.jpg'),
    ]

    by_tags = {
        'animal': frozenset(['u1', 'u2', 'u3', 'u4', 'u5']),
        'object': frozenset(['u6', 'u7', 'u8']),
        'small': frozenset(['u3', 'u4']),
        'big': frozenset(['u7', 'u8']),
    }
    return search_engine.Index(all_metas=all_metas, by_tags=by_tags)


@pytest.fixture
def fix_singleton(fix_empty_index):
    inst = singleton.Singleton()
    inst.version = 'test'
    inst.process = mock.Mock()
    inst.process.memory_info.return_value = [0, 38476234, 0]
    inst.filesystem = infra.Filesystem()
    inst.stdout = infra.STDOut()
    inst.status = status.Status(
        datetime.datetime(2021, 10, 6, 21, 37).replace(
            tzinfo=datetime.timezone.utc)
    )
    inst.index = fix_empty_index
    inst.db_path = '/test/path'
    return inst


@pytest.fixture
def fix_empty_query():
    return objects.Query(
        and_=[],
        or_=[],
        not_=[],
        page=1,
        items_per_page=4,
        themes=None,
    )


@pytest.fixture
def fix_query():
    return objects.Query(
        and_=['animal'],
        or_=['small'],
        not_=['big'],
        page=1,
        items_per_page=4,
        themes=None,
    )
