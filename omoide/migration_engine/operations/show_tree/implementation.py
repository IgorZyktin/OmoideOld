# -*- coding: utf-8 -*-
"""Display folder tree.
"""
from datetime import datetime

from omoide import commands
from omoide import infra
from omoide import utils
from omoide.constants import storage as storage_constants
from omoide.infra import walking


def run_show_tree(command: commands.ShowTreeCommand,
                  filesystem: infra.Filesystem,
                  stdout: infra.STDOut) -> None:
    """Display folder tree."""
    for top in walking.traverse_top(command, filesystem, 'sources_folder'):
        stdout.green(f'\t{top}')
        for bottom in walking.traverse_bottom(command, top):
            _one_step(bottom, stdout)


def _one_step(bottom: walking.Bottom, stdout: infra.STDOut) -> None:
    """Single step of the main cycle."""
    source_path = bottom.filesystem.join(bottom.leaf_folder,
                                         storage_constants.SOURCE_FILE_NAME)

    if bottom.filesystem.not_exists(source_path):
        stdout.red(f'\t\t{bottom} Source file does not exist')
        return

    fingerprint = bottom.filesystem.get_fingerprint(source_path)
    size = utils.byte_count_to_text(fingerprint['size'])
    last_update = datetime.fromtimestamp(fingerprint['modified'])

    stdout.print(f'\t\t{bottom} {last_update}, {size}')
