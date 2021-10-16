# -*- coding: utf-8 -*-

"""Files/folders iteration tools.
"""
from dataclasses import dataclass
from typing import Iterator, Tuple, Generator

from omoide.commands import instances
from omoide.infra.class_filesystem import Filesystem

__all__ = [
    'walk_sources_from_command',
    'walk_storage_from_command',
    'walk',
    'traverse_top',
    'traverse_bottom',
    'Top',
    'Bottom',
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


@dataclass
class Top:
    """Top level descriptive instance.

    Created because I got tired of passing all the arguments around.
    """
    number: int
    total: int
    position: str
    root_folder: str
    branch: str
    branch_folder: str
    filesystem: Filesystem
    revision: str
    last_update: str

    def __str__(self) -> str:
        """Format as report header."""
        return f'[{self.position}][{self.branch}]'


@dataclass
class Bottom:
    """Bottom level descriptive instance.

    Created because I got tired of passing all the arguments around.
    """
    number: int
    total: int
    position: str
    root_folder: str
    branch: str
    branch_folder: str
    leaf: str
    leaf_folder: str
    filesystem: Filesystem
    revision: str
    last_update: str

    def __str__(self) -> str:
        """Format as report header."""
        return f'[{self.position}][{self.leaf}]'


def format_position(number: int, total: int) -> str:
    """Make cute position description.

    >>> format_position(75, 248)
    ' 75 of 248'
    """
    digits = len(str(total))
    left = str(number).rjust(digits, ' ')
    right = str(total).rjust(digits, ' ')
    return f'{left} of {right}'


def traverse_top(command: instances.FilesRelatedCommand,
                 filesystem: Filesystem,
                 folder_kind: str = 'storage_folder'
                 ) -> Generator[Top, None, None]:
    """Traverse top level of folders."""
    folder = getattr(command, folder_kind)
    branches = [
        branch
        for branch in filesystem.list_folders(folder)
        if command.branch in ('all', branch)
    ]
    total = len(branches)

    for i, branch_name in enumerate(branches, start=1):
        yield Top(
            number=i,
            total=total,
            position=format_position(i, total),
            root_folder=command.root_folder,
            branch=branch_name,
            branch_folder=filesystem.join(folder, branch_name),
            filesystem=filesystem,
            revision=command.revision,
            last_update=command.now,
        )


def traverse_bottom(command: instances.FilesRelatedCommand,
                    top: Top) -> Generator[Bottom, None, None]:
    """Traverse bottom level of folders."""
    leaves = [
        leaf
        for leaf in top.filesystem.list_folders(top.branch_folder)
        if command.leaf in ('all', leaf)
    ]
    total = len(leaves)

    for i, leaf_name in enumerate(leaves, start=1):
        yield Bottom(
            number=i,
            total=total,
            position=format_position(i, total),
            root_folder=top.root_folder,
            branch=top.branch,
            branch_folder=top.branch_folder,
            leaf=leaf_name,
            leaf_folder=top.filesystem.join(top.branch_folder, leaf_name),
            filesystem=top.filesystem,
            revision=top.revision,
            last_update=top.last_update,
        )
