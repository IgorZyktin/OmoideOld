# -*- coding: utf-8 -*-

"""Tests.
"""
import asyncio
from unittest import mock
from unittest.mock import patch

from starlette.testclient import TestClient

from omoide.index_server.app import app, quietly_update_index_on_start

client = TestClient(app)


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


def test_app_healthcheck():
    # act
    response = client.get('/')

    # assert
    assert response.status_code == 200
    assert response.json() == {'result': 'ok'}


def test_app_status(fix_singleton):
    # act
    with patch('omoide.index_server.app.logic.reload',
               return_value=async_return('called')):
        with patch('omoide.utils.now',
                   return_value=fix_singleton.status.server_last_restart):
            response = client.get('/status')

    # assert
    assert response.status_code == 200
    assert response.json() == {
        'index_avg_bucket': 0.0,
        'index_buckets': 0,
        'index_comment': '',
        'index_last_reload': '2021-10-06 21:37:00+00:00',
        'index_last_reload_duration': 0,
        'index_max_bucket': 0,
        'index_min_bucket': 0,
        'index_records': 0,
        'index_size': '0 B',
        'index_status': 'init',
        'index_uptime': '0s',
        'server_last_restart': '2021-10-06 21:37:00+00:00',
        'server_size': '0 B',
        'server_uptime': '0s',
        'version': 'test',
    }


def test_app_update_database_folder_read(fix_singleton):
    # act
    response = client.post('/update_database_folder', json={})

    # assert
    assert response.status_code == 200
    assert response.json() == {'result': "Now using '/test/path'"}


def test_app_update_database_folder_write(fix_singleton):
    # act
    response = client.post('/update_database_folder', json={'path': '/new'})

    # assert
    assert response.status_code == 200
    assert response.json() == {'result': "Now using '/new'"}


def test_app_reload(fix_singleton):
    # act
    with patch('omoide.index_server.app.logic') as fake_logic:
        fake_logic.reload.return_value = async_return('called')
        response = client.post('/reload')

    # assert
    assert response.status_code == 200
    assert response.json() == {'result': 'Started reloading'}
    fake_logic.reload.assert_called_once_with(fix_singleton)


def test_app_search(fix_singleton):
    # arrange
    query = {'and_': [], 'or_': [], 'not_': [], 'page': 1, 'items_per_page': 2}
    fake_return = mock.Mock()
    fake_return.dict.return_value = {'ok': 1}

    # act
    with patch('omoide.index_server.app.logic') as fake_logic:
        fake_logic.search.return_value = async_return(fake_return)
        response = client.get('/search', json=query)

    # assert
    assert response.status_code == 200
    assert response.json() == {'ok': 1}
    fake_logic.search.assert_called_once_with(mock.ANY, fix_singleton)


def test_app_quietly_update_index_on_start():
    with patch('omoide.index_server.app.logic.reload',
               return_value=async_return('called')) as fake:
        asyncio.run(quietly_update_index_on_start())

    fake.assert_awaited_once()
