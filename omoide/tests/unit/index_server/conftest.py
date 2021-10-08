# -*- coding: utf-8 -*-

"""Tests.
"""
import datetime
from collections import defaultdict
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
def fix_parts():
    return [
        ('u1', 1, 'cat.jpg'),
        ('u2', 2, 'dog.jpg'),
        ('u3', 3, 'frog.jpg'),
        ('u4', 4, 'ant.jpg'),
        ('u5', 5, 'bird.jpg'),
        ('u6', 6, 'box.jpg'),
        ('u7', 7, 'building.jpg'),
        ('u8', 8, 'river.jpg'),
        ('u9', 9, 'sky.jpg'),
    ]


@pytest.fixture
def fix_tags():
    return [
        ('animal', 'u1'),
        ('animal', 'u2'),
        ('animal', 'u3'),
        ('animal', 'u4'),
        ('animal', 'u5'),
        ('object', 'u6'),
        ('object', 'u7'),
        ('object', 'u8'),
        ('small', 'u3'),
        ('small', 'u4'),
        ('big', 'u7'),
        ('big', 'u8'),
    ]


@pytest.fixture
def fix_index(fix_parts, fix_tags):
    all_metas = [search_engine.ShallowMeta(*x) for x in fix_parts]

    grouped = defaultdict(list)
    for tag, uuid in fix_tags:
        grouped[tag].append(uuid)

    by_tags = {tag: frozenset(uuids) for tag, uuids in grouped.items()}

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
def fix_query():
    return objects.Query(
        and_=[],
        or_=[],
        not_=[],
        page=1,
        items_per_page=4,
        themes=None,
    )
