# -*- coding: utf-8 -*-

"""Files/folders iteration tools.
"""
from typing import Iterator, Tuple

from omoide.commands import instances
from omoide.infra.class_filesystem import Filesystem

__all__ = [
    'walk_sources_from_command',
    'walk_storage_from_command',
    'walk',
]


def walk_sources_from_command(command: instances.FilesRelatedCommand,
                              filesystem: Filesystem
                              ) -> Iterator[Tuple[str, str, str]]:
    """Typical iteration by command settings."""
    return walk(command.sources_folder, filesystem,
                command.branch, command.leaf)


def walk_storage_from_command(command: instances.FilesRelatedCommand,
                              filesystem: Filesystem
                              ) -> Iterator[Tuple[str, str, str]]:
    """Typical iteration by command settings."""
    return walk(command.storage_folder, filesystem,
                command.branch, command.leaf)


def walk(folder: str, filesystem: Filesystem, branch: str = 'all',
         leaf: str = 'all') -> Iterator[Tuple[str, str, str]]:
    """Iterate on nested folders."""
    for current_branch in filesystem.list_folders(folder):
        if branch not in ('all', current_branch):
            continue

        branch_folder = filesystem.join(folder, current_branch)
        for current_leaf in filesystem.list_folders(branch_folder):

            if leaf not in ('all', current_leaf):
                continue

            leaf_folder = filesystem.join(branch_folder, current_leaf)

            yield current_branch, current_leaf, leaf_folder
