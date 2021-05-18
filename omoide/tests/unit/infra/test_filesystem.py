# -*- coding: utf-8 -*-

"""Tests.
"""
import os
import tempfile
from functools import lru_cache
from unittest import mock

import pytest

from omoide import infra


@pytest.fixture()
def filesystem():
    return infra.Filesystem()


@lru_cache
def get_local_folder():
    path = os.path.abspath(os.getcwd())
    tried = [path]

    for _ in range(10):
        files = os.listdir(path)
        if 'infra' in files and 'tests' in files:
            return os.path.abspath(path)

        path = os.path.join(path, '..')
        tried.append(path)

    raise FileNotFoundError(
        f'Unable to find root folder (tried {tried})'
    )  # pragma: no cover


def test_filesystem_split_extension(filesystem):
    test_data = [
        ('somefile.txt', ('somefile', 'txt')),
        ('some other file.db', ('some other file', 'db')),
    ]
    for filename, ref in test_data:
        assert filesystem.split_extension(filename) == ref


def test_filesystem_join(filesystem):
    assert filesystem.join('folder_a', 'folder_b') \
           == os.path.join('folder_a', 'folder_b')


def test_filesystem_read_nonexistent(filesystem):
    path = 'somewhere'

    with pytest.raises(FileNotFoundError):
        filesystem.read_file(path)


def test_filesystem_read_nonexistent_json(filesystem):
    path = 'somewhere'

    with pytest.raises(FileNotFoundError):
        filesystem.read_json(path)


def test_filesystem_copy_file(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path1 = filesystem.join(tmp_dir, 'test1.txt')
        path2 = filesystem.join(tmp_dir, 'test2.txt')
        filesystem.write_file(path1, '{"something": 25}')
        filesystem.copy_file(path1, path2)
        content = filesystem.read_json(path2)
        assert content == {'something': 25}


def test_filesystem_move_file(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path1 = filesystem.join(tmp_dir, 'test1.txt')
        path2 = filesystem.join(tmp_dir, 'test2.txt')
        filesystem.write_file(path1, 'something')
        filesystem.move_file(path1, path2)
        content = filesystem.read_file(path2)
        assert content == 'something'
        assert not os.path.exists(path1)


def test_filesystem_delete_file(filesystem):
    payload = {"tag": "something"}
    with tempfile.TemporaryDirectory() as tmp_dir:
        path1 = filesystem.join(tmp_dir, 'test1.txt')
        filesystem.write_json(path1, payload)
        assert filesystem.read_json(path1) == payload

        assert os.path.exists(path1)
        filesystem.delete_file(path1)
        assert not os.path.exists(path1)


def test_filesystem_absolute(filesystem):
    path = os.getcwd()
    assert filesystem.absolute(path) == os.path.abspath(path)


def test_filesystem_cut_tail(filesystem):
    parts = ['folder_a', 'folder_b', 'folder_c']
    path = os.path.join(*parts)
    assert filesystem.cut_tail(path) == os.path.join(*parts[:-1])


def test_filesystem_listdir(filesystem):
    contents = filesystem.listdir(get_local_folder())
    assert 'infra' in contents
    assert 'tests' in contents


def test_filesystem_list_files(filesystem):
    contents = filesystem.list_files(get_local_folder())
    assert '__init__.py' in contents
    assert 'infra' not in contents


def test_filesystem_list_folders(filesystem):
    contents = filesystem.list_folders(get_local_folder())
    assert '__init__.py' not in contents
    assert 'infra' in contents


def test_filesystem_ensure_folder_exists_one_level(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = filesystem.join(tmp_dir, 'folder')
        assert not os.path.exists(path)
        fake_stdout = mock.Mock()
        filesystem.ensure_folder_exists(path, fake_stdout, '>')
        assert os.path.exists(path)

    fake_stdout.light_green.assert_called_once()
    assert not os.path.exists(path)


def test_filesystem_ensure_folder_exists_deep(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = filesystem.join(tmp_dir, 'a', 'b', 'c', 'd', 'e')
        assert not os.path.exists(path)
        fake_stdout = mock.Mock()
        filesystem.ensure_folder_exists(path, fake_stdout, '>')
        assert os.path.exists(path)

    assert len(fake_stdout.mock_calls) == 5
    assert not os.path.exists(path)


def test_filesystem_existence(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_stdout = mock.Mock()
        path = filesystem.join(tmp_dir, 'a')

        assert not filesystem.exists(path)
        assert filesystem.not_exists(path)

        filesystem.ensure_folder_exists(path, fake_stdout, '>')

        assert filesystem.exists(path)
        assert not filesystem.not_exists(path)

    assert len(fake_stdout.mock_calls) == 1
