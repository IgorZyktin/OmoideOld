# -*- coding: utf-8 -*-

"""Test unite command with active cache.

We're testing situation with unite command when some of source
folders do have cache and some do not. Problem that we're checking -
repeated generation of UUIDs during cache use.
"""
import tempfile
from typing import Tuple
from unittest import mock

from omoide import constants, commands
from omoide.__main__ import run
from omoide.infra import Filesystem


def test_unite_with_cache(unite_with_cache_folder_structure,
                          unite_with_cache_sources,
                          unite_with_cache_caches,
                          unite_with_cache_media_files):
    # arrange
    filesystem = Filesystem()
    structure = unite_with_cache_folder_structure

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = filesystem.absolute(tmp_dir)
        sources_path = filesystem.join(root, constants.SOURCES_FOLDER_NAME)
        storage_path = filesystem.join(root, constants.STORAGE_FOLDER_NAME)

        _create_folder_structure(filesystem, sources_path, structure)
        _create_folder_structure(filesystem, storage_path, structure)
        _create_jsons_sources(filesystem, sources_path,
                              unite_with_cache_sources)
        _create_jsons_caches(filesystem, storage_path,
                             unite_with_cache_caches)
        _create_media_files(filesystem, sources_path,
                            unite_with_cache_media_files)

        command = commands.UniteCommand(
            now='2021-08-21 08:44:00',
            revision='some_revision',
            force=True,
            sources_folder=sources_path,
            storage_folder=storage_path,
        )

        # apply
        run(command, stdout=mock.Mock())
        caches, units = _gather_contents(filesystem, storage_path, structure)

    # assert
    _assert_variables_are_fine(caches, unite_with_cache_caches)
    _assert_uuids_are_fine(caches)


def _create_folder_structure(filesystem: Filesystem, path: str,
                             structure: dict) -> None:
    for source, subfolders in structure.items():
        for subfolder in subfolders:
            folder = filesystem.join(path, source, subfolder)
            filesystem.ensure_folder_exists(folder)


def _create_jsons_sources(filesystem: Filesystem, path: str,
                          sources: dict) -> None:
    for (source, migration), content in sources.items():
        full_path = filesystem.join(path,
                                    source, migration,
                                    constants.SOURCE_FILE_NAME)
        filesystem.write_json(full_path, content)


def _create_jsons_caches(filesystem: Filesystem, path: str,
                         caches: dict) -> None:
    for (source, migration), content in caches.items():
        full_path = filesystem.join(path,
                                    source, migration,
                                    constants.CACHE_FILE_NAME)
        filesystem.write_json(full_path, content)


def _create_media_files(filesystem: Filesystem, path: str,
                        files: dict) -> None:
    for subfolders, filenames in files.items():
        directory = filesystem.join(path, *subfolders)
        filesystem.ensure_folder_exists(directory)
        for filename in filenames:
            full_path = filesystem.join(directory, filename)
            with open(full_path, mode='wb') as file:
                file.write(b'')


def _gather_contents(filesystem: Filesystem, path: str, structure: dict
                     ) -> Tuple[dict, dict]:
    """Load results of run."""
    caches = {}
    units = {}

    for source, subfolders in structure.items():
        for subfolder in subfolders:
            cache_file = filesystem.join(path, source, subfolder,
                                         constants.CACHE_FILE_NAME)
            unit_file = filesystem.join(path, source, subfolder,
                                        constants.UNIT_FILE_NAME)
            caches[(source, subfolder)] = filesystem.read_json(cache_file)
            units[(source, subfolder)] = filesystem.read_json(unit_file)

    return caches, units


def _assert_variables_are_fine(caches: dict, original_caches: dict):
    assert caches != original_caches

    for key in original_caches.keys():
        if original_caches[key]:
            assert caches[key] == original_caches[key]

    uuids_variables = []
    for value in caches.values():
        uuids_variables.extend(value['variables']['themes'].values())
        uuids_variables.extend(value['variables']['groups'].values())
        uuids_variables.extend(value['variables']['metas'].values())
        uuids_variables.extend(value['variables']['synonyms'].values())

    assert len(uuids_variables) == len(set(uuids_variables))


def _assert_uuids_are_fine(caches: dict) -> None:
    uuids = []
    for value in caches.values():
        uuids.extend(value['uuids'])

    assert len(uuids) == len(set(uuids))
