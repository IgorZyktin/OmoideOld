# -*- coding: utf-8 -*-

"""Relocate.
"""
import math
from typing import Collection

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.migration_engine import classes


def act(command: commands.RelocateCommand,
        filesystem: infra.Filesystem, stdout: infra.STDOut) -> int:
    """Make relocations."""
    renderer = classes.Renderer()
    walk = infra.walk_sources_from_command(command, filesystem)

    total_new_relocations = 0
    for branch, leaf, _ in walk:
        storage_folder = filesystem.join(command.storage_folder, branch, leaf)
        relocation_file_path = filesystem.join(storage_folder,
                                               constants.RELOCATION_FILE_NAME)

        if filesystem.not_exists(relocation_file_path):
            stdout.gray(
                f'\t[{branch}][{leaf}] Relocation file does not exist'
            )
            continue

        raw_relocation = filesystem.read_json(relocation_file_path)
        relocation = classes.Relocation(**raw_relocation)
        total_new_relocations = 0

        groups = sorted(relocation.groups.keys())
        for group_key in groups:
            group = relocation.groups[group_key]
            theme_route, group_route = group_key.split(',')
            applied = relocate_single_group(group, renderer, filesystem,
                                            branch, leaf, theme_route,
                                            group_route, stdout, command.force)
            total_new_relocations += applied

    return total_new_relocations


def relocate_single_group(group: classes.OneGroup,
                          renderer: classes.Renderer,
                          filesystem: infra.Filesystem,
                          branch: str,
                          leaf: str,
                          theme_route: str,
                          group_route: str,
                          stdout: infra.STDOut,
                          force: bool) -> int:
    """Save one group as a whole."""
    one_file = list(group.files.values())[0]
    if filesystem.exists(one_file.conversions[0].folder_to) and not force:
        stdout.cyan(f'\t[{branch}][{leaf}] Already relocated')
        return 0

    stdout.green(
        f'\t[{branch}][{leaf}] Converting {theme_route}/{group_route}'
    )

    for file in with_progress(group.files.values(), stdout):
        relocate_single_file(file, group.folder_from, renderer,
                             filesystem, stdout)

    return sum(len(file.conversions) for file in group.files.values())


def relocate_single_file(file: classes.OneFile,
                         folder_from: str,
                         renderer: classes.Renderer,
                         filesystem: infra.Filesystem,
                         stdout: infra.STDOut) -> None:
    """Save one source file onto output files."""
    path_from = filesystem.join(folder_from, file.source_filename)

    if filesystem.not_exists(path_from):
        raise FileNotFoundError(
            f'Original media file does not exist: {path_from}'
        )

    for conversion in file.conversions:
        filesystem.ensure_folder_exists(conversion.folder_to, stdout)
        path_to = filesystem.join(conversion.folder_to, file.target_filename)

        if conversion.operation_type == 'copy':
            filesystem.copy_file(path_from, path_to)
        else:
            renderer.save_new_size(path_from, path_to,
                                   conversion.width, conversion.height)


def with_progress(iterable: Collection, stdout: infra.STDOut):
    """Iterate with progress bar."""
    sequence = list(iterable)
    total = len(sequence)
    bar_width = 65
    for i, element in enumerate(sequence, start=1):
        percent = i / total
        complete = math.ceil(bar_width * percent)
        left = bar_width - complete
        stdout.print('#' * complete + '_' * left + f' {percent:.1%}',
                     prefix='\r\t', end='')
        yield element
    stdout.print('', prefix='\r', end='')
