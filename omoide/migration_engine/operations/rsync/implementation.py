# -*- coding: utf-8 -*-
"""Update replica.
"""

from omoide import commands
from omoide import infra
from omoide.constants import storage as storage_constants
from omoide.infra import walking


def run_rsync(command: commands.RSyncCommand,
              filesystem: infra.Filesystem,
              stdout: infra.STDOut) -> int:
    """Update replica."""
    stdout.magenta(f'From: {command.content_folder}')
    stdout.magenta(f'  To: {command.content_folder_to}')

    filesystem.ensure_folder_exists(command.content_folder, stdout,
                                    prefix='\t')
    filesystem.ensure_folder_exists(command.content_folder_to, stdout,
                                    prefix='\t')

    top_folders = (
        storage_constants.MEDIA_CONTENT_FOLDER_NAME,
        storage_constants.MEDIA_PREVIEW_FOLDER_NAME,
        storage_constants.MEDIA_THUMBNAILS_FOLDER_NAME,
    )

    total = 0
    for each in top_folders:
        path = filesystem.join(command.content_folder, each)
        path_to = filesystem.join(command.content_folder_to, each)
        filesystem.ensure_folder_exists(path, stdout, prefix='\t')
        filesystem.ensure_folder_exists(path_to, stdout, prefix='\t')

        setattr(command, each, path)
        stdout.yellow(f'Synchronizing {each}')

        for top in walking.traverse_top(command, filesystem, each):
            stdout.green(f'\t{top}')
            for bottom in walking.traverse_bottom(command, top):
                copies_made = rsync_one_folder(bottom, stdout, path, path_to)
                total += copies_made

    return total


def rsync_one_folder(bottom: walking.Bottom, stdout: infra.STDOut,
                     base_path: str, base_path_to: str) -> int:
    """Synchronize one folder.

    This is a primitive instrument, it is not actually checking file sizes
    and contents. It is supposed to work fast on thousands of files,
    so we're looking only on names.
    """
    path_from = bottom.leaf_folder
    addition = bottom.filesystem.extract_addition(base_path, path_from)
    path_to = bottom.filesystem.join(base_path_to, *addition)
    bottom.filesystem.ensure_folder_exists(path_to, stdout, prefix='\t\t')

    files_from = set(bottom.filesystem.list_files(path_from))
    files_to = set(bottom.filesystem.list_files(path_to))
    delta = files_from - files_to

    if not delta:
        return 0

    copies_made = 0
    filenames = sorted(delta)

    for filename in infra.with_progress(filenames, stdout, prefix='\t'):
        full_path_from = bottom.filesystem.join(path_from, filename)
        full_path_to = bottom.filesystem.join(path_to, filename)
        bottom.filesystem.copy_file(full_path_from, full_path_to)
        copies_made += 1

    return copies_made
