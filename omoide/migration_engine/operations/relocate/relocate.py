# -*- coding: utf-8 -*-

"""Relocate.
"""
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

        raw_relocations = filesystem.read_json(relocation_file_path)
        relocations = [classes.Relocation(**x) for x in raw_relocations]
        total_new_relocations += len(relocations)

        for relocation in relocations:
            relocate_single_file(relocation, renderer, filesystem,
                                 stdout, command.force)

    return total_new_relocations


def relocate_single_file(relocation: classes.Relocation,
                         renderer: classes.Renderer,
                         filesystem: infra.Filesystem,
                         stdout: infra.STDOut,
                         force: bool) -> None:
    """Save one source file onto output files."""
    path_from = filesystem.join(relocation.folder_from,
                                relocation.source_filename)

    if filesystem.not_exists(path_from):
        raise FileNotFoundError(
            f'Original media file does not exist: {path_from}'
        )

    stdout.print(f'\t{relocation.source_filename}')
    for operation in relocation.operations:
        filesystem.ensure_folder_exists(operation.folder_to, stdout)
        path_to = filesystem.join(operation.folder_to,
                                  relocation.target_filename)

        if filesystem.exists(path_to) and not force:
            stdout.cyan(
                f'\t\tFile already exist: {relocation.target_filename}')
            continue

        if operation.operation_type == 'copy':
            filesystem.copy_file(path_from, path_to)
        else:
            renderer.resize(path_from, path_to,
                            operation.width, operation.height)
