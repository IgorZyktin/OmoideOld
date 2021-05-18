"""Tests.
"""
import tempfile
from unittest import mock

import pytest

from omoide import infra


@pytest.fixture()
def filesystem():
    return infra.Filesystem()


def test_walk(filesystem):
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_stdout = mock.Mock()
        path_1 = filesystem.join(tmp_dir, 'source_1')
        path_2 = filesystem.join(tmp_dir, 'source_1', 'migration_1')
        path_3 = filesystem.join(tmp_dir, 'source_1', 'migration_2')
        path_4 = filesystem.join(tmp_dir, 'source_2', 'migration_3')
        path_5 = filesystem.join(tmp_dir, 'source_2', 'migration_4')

        for path in (path_1, path_2, path_3, path_4, path_5):
            filesystem.ensure_folder_exists(path, fake_stdout)

        gen = infra.walk(tmp_dir, filesystem,
                         branch='source_2', leaf='migration_3')

        assert list(gen) == [('source_2',
                              'migration_3',
                              filesystem.join(tmp_dir,
                                              'source_2',
                                              'migration_3'))]
