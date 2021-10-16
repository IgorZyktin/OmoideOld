# -*- coding: utf-8 -*-

"""Relocate.
"""
import math
from typing import Collection

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.migration_engine import classes
from omoide.infra import walking
from omoide.migration_engine.classes import passport as passport_module


def run_relocate(command: commands.RelocateCommand,
                 filesystem: infra.Filesystem,
                 stdout: infra.STDOut) -> int:
    """Make relocations."""
    renderer = classes.Renderer()
    total_new_relocations = 0

    for top in walking.traverse_top(command, filesystem):
        stdout.print(f'\t{top}')

        for bottom in walking.traverse_bottom(command, top):
            storage_folder = filesystem.join(
                command.storage_folder,
                bottom.branch,
                bottom.leaf
            )

            relocation_file_path = filesystem.join(
                storage_folder,
                constants.RELOCATION_FILE_NAME,
            )

            if not filesystem.exists(relocation_file_path):
                stdout.gray(f'\t\t{bottom} Relocation file does not exist')
                continue

            passport = passport_module.load_from_file(bottom)

            if passport.already_processed(
                    bottom, relocation_file_path,
                    passport.relocate.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t{bottom} Relocations already applied')
                continue

            raw_relocation = filesystem.read_json(relocation_file_path)
            relocation = classes.Relocation(**raw_relocation)

            groups = sorted(relocation.groups.keys())
            for group_key in groups:
                group = relocation.groups[group_key]
                theme_route, group_route = group_key.split(',')
                applied = relocate_single_group(bottom, group, renderer,
                                                theme_route, group_route,
                                                stdout, command.force)
                total_new_relocations += applied

            passport.register_relocate(bottom, relocation_file_path)
            passport.save_to_file(bottom)

    return total_new_relocations


def relocate_single_group(bottom: walking.Bottom,
                          group: classes.OneGroup,
                          renderer: classes.Renderer,
                          theme_route: str,
                          group_route: str,
                          stdout: infra.STDOut,
                          force: bool) -> int:
    """Save one group as a whole."""
    one_file = list(group.files.values())[0]
    if bottom.filesystem.exists(one_file.conversions[0].folder_to) \
            and not force:
        stdout.cyan(f'\t\t{bottom} Already relocated '
                    f'{theme_route}/{group_route}')
        return 0

    stdout.green(
        f'\t\t{bottom} Converting {theme_route}/{group_route}'
    )

    for file in with_progress(group.files.values(), stdout):
        relocate_single_file(bottom, file, group.folder_from, renderer, stdout)

    return sum(len(file.conversions) for file in group.files.values())


def relocate_single_file(bottom: walking.Bottom,
                         file: classes.OneFile,
                         folder_from: str,
                         renderer: classes.Renderer,
                         stdout: infra.STDOut, newline: bool = True) -> None:
    """Save one source file onto output files."""
    path_from = bottom.filesystem.join(folder_from, file.source_filename)

    if bottom.filesystem.not_exists(path_from):
        raise FileNotFoundError(
            f'Original media file does not exist: {path_from}'
        )

    for conversion in file.conversions:
        if newline:
            prefix = '\n\t\t\t'
        else:
            prefix = '\t\t\t'

        created = bottom.filesystem.ensure_folder_exists(
            conversion.folder_to, stdout, prefix=prefix)
        newline = not created

        path_to = bottom.filesystem.join(conversion.folder_to,
                                         file.target_filename)

        if conversion.operation_type == 'copy':
            bottom.filesystem.copy_file(path_from, path_to)
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

    stdout.print('', prefix='\r', end='\n')
