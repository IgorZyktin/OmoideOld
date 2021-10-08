# -*- coding: utf-8 -*-

"""Tests.
"""
from unittest import mock

from omoide import commands, infra
from omoide.index_server import implementation, status
from omoide.index_server.singleton import Singleton


def test_index_server_implementation():
    # arrange
    command = commands.RunIndexCommand(
        host='test.com',
        port=9999,
        root='/root',
        database_folder='/root/db',
    )
    filesystem = infra.Filesystem()
    stdout = infra.STDOut()

    # act
    with mock.patch('omoide.index_server.implementation.uvicorn') as fake_uv:
        implementation.run_index(command, filesystem, stdout)
        singleton = Singleton()

    # assert
    assert singleton.status.index_status == status.STATUS_INIT
    fake_uv.run.assert_called_once_with(mock.ANY, host='test.com', port=9999)
