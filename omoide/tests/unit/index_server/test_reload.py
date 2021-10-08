# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock

from omoide.index_server import logic, status


def test_index_server_reload_from_scratch(fix_singleton, fix_index):
    # arrange
    ref_index = fix_index
    state = fix_singleton
    initial_time = state.status.server_last_restart
    fake_loop = mock.Mock()

    async def fake_execute(*args):
        return ref_index, {'x': 1}

    # act
    with mock.patch('omoide.index_server.logic.'
                    'asyncio.get_event_loop', return_value=fake_loop):
        fake_loop.run_in_executor = fake_execute
        asyncio.run(logic.reload(state))

    # assert
    assert state.status.index_status == status.STATUS_ACTIVE
    assert state.status.server_last_restart == initial_time
    assert state.status.index_last_reload > initial_time
    assert state.index is ref_index
    assert state.status.x == 1


def test_index_server_reload_from_stable(fix_singleton, fix_index):
    # arrange
    ref_index = fix_index
    state = fix_singleton
    initial_time = state.status.server_last_restart
    fake_loop = mock.Mock()
    state.status.index_status = status.STATUS_ACTIVE

    async def fake_execute(*args):
        return ref_index, {'x': 1}

    # act
    with mock.patch('omoide.index_server.logic.'
                    'asyncio.get_event_loop', return_value=fake_loop):
        fake_loop.run_in_executor = fake_execute
        asyncio.run(logic.reload(state))

    # assert
    assert state.status.index_status == status.STATUS_ACTIVE
    assert state.status.server_last_restart == initial_time
    assert state.status.index_last_reload > initial_time
    assert state.index is ref_index
    assert state.status.x == 1


def test_index_server_fail_from_scratch(fix_singleton, fix_index):
    # arrange
    ref_index = fix_index
    state = fix_singleton
    initial_time = state.status.server_last_restart
    fake_loop = mock.Mock()
    state.status.index_status = status.STATUS_ACTIVE

    async def fake_execute(*args):
        raise ValueError

    # act
    with (mock.patch('omoide.index_server.logic.'
                     'asyncio.get_event_loop', return_value=fake_loop),
          mock.patch('omoide.index_server.logic.print'),
          mock.patch('omoide.index_server.logic.traceback') as fake_tr):
        fake_loop.run_in_executor = fake_execute
        asyncio.run(logic.reload(state))

    # assert
    fake_tr.print_exc.assert_called_once()
    assert state.status.index_status == status.STATUS_FAILED
    assert state.status.server_last_restart == initial_time
    assert state.status.index_last_reload == initial_time
    assert state.index is not ref_index
    assert not hasattr(state.status, 'x')
