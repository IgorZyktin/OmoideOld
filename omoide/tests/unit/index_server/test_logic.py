# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock

from pympler.asizeof import asizeof

from omoide import utils
from omoide.index_server import logic, constants, status


def test_index_server_logic_analyze_index(fix_index):
    # arrange
    index = fix_index

    # act
    result = logic.analyze_index(fix_index)

    # assert
    assert result == {
        'index_avg_bucket': 2.25,
        'index_buckets': 4,
        'index_max_bucket': 5,
        'index_min_bucket': 2,
        'index_records': 9,
        'index_size': utils.byte_count_to_text(asizeof(index))
    }


def test_index_server_logic_index_pipeline(fix_parts, fix_tags, fix_index):
    # arrange
    ref_index = fix_index

    with mock.patch('omoide.index_server.logic.sqlalchemy') as fake_sa:
        # arrange
        path = '/some/path'
        fake_engine = mock.Mock()
        fake_sa.create_engine.return_value = fake_engine
        fake_sa.text = lambda x: str(x)

        fake_conn = mock.Mock()
        fake_manager = mock.Mock()
        fake_manager.__enter__ = mock.Mock(return_value=fake_conn)
        fake_manager.__exit__ = mock.Mock(return_value=None)
        fake_engine.begin.return_value = fake_manager

        def fake_execute(stmt: str) -> list[tuple]:
            if stmt == constants.SELECT_INDEX_TAGS:
                result = fix_tags
            else:
                result = fix_parts

            output = mock.Mock()
            output.fetchall.return_value = result
            return output

        fake_conn.execute = fake_execute

        # act
        index, params = logic.index_pipeline(path)

    # assert
    fake_sa.create_engine.assert_called_once_with(
        'sqlite+pysqlite:////some/path?uri=true', echo=False, future=True)
    fake_engine.dispose.assert_called_once()

    assert params == logic.analyze_index(ref_index)
    assert index.all_metas_tuple == ref_index.all_metas_tuple
    assert index.all_metas_set == ref_index.all_metas_set
    assert index.by_tags == ref_index.by_tags
    assert index.by_uuid == ref_index.by_uuid


def test_index_server_logic_format_status(fix_singleton):
    # arrange
    state = fix_singleton

    # act
    with mock.patch('omoide.utils.now',
                    return_value=state.status.server_last_restart):
        result = asyncio.run(logic.format_status(state))

    # assert
    assert result == {
        'index_avg_bucket': 0.0,
        'index_buckets': 0,
        'index_comment': '',
        'index_last_reload': str(state.status.server_last_restart),
        'index_last_reload_duration': 0,
        'index_max_bucket': 0,
        'index_min_bucket': 0,
        'index_records': 0,
        'index_size': '0 B',
        'index_status': 'init',
        'index_uptime': '0s',
        'server_last_restart': str(state.status.server_last_restart),
        'server_size': '0 B',
        'server_uptime': '0s',
        'version': 'test',
    }


def test_index_server_logic_search_on_empty_query(fix_query, fix_singleton):
    # arrange
    query = fix_query
    state = fix_singleton

    # act
    result = asyncio.run(logic.search(query, state))

    # assert
    assert result.page == 1
    assert result.total_pages == 1
    assert result.announce == constants.MESSAGE_INIT


def test_index_server_logic_search_on_empty_query_reload(fix_query,
                                                         fix_singleton):
    # arrange
    query = fix_query
    state = fix_singleton
    state.status.index_status = status.STATUS_RELOADING

    # act
    result = asyncio.run(logic.search(query, state))

    # assert
    assert result.page == 1
    assert result.total_pages == 1
    assert result.announce == constants.MESSAGE_RELOADING


def test_index_server_logic_search_on_empty_query_failed(fix_query,
                                                         fix_singleton):
    # arrange
    query = fix_query
    state = fix_singleton
    state.status.index_status = status.STATUS_FAILED

    # act
    result = asyncio.run(logic.search(query, state))

    # assert
    assert result.page == 1
    assert result.total_pages == 1
    assert result.announce == ''  # failed update not displayed to the user


def test_index_server_logic_search_with_query(fix_query,
                                              fix_singleton,
                                              fix_index):
    # arrange
    query = fix_query
    query.and_ = ['animal']
    state = fix_singleton
    state.index = fix_index

    # act
    result = asyncio.run(logic.search(query, state))

    # assert
    assert result.page == 1
    assert result.total_pages > 1
    assert result.total_items > query.items_per_page
    assert len(result.items) > 1
