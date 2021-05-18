# -*- coding: utf-8 -*-

"""Make migrations.
"""
from typing import List

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.migration_engine import classes
from omoide.migration_engine.operations.make_migrations import schema


def act(command: commands.MakeMigrationsCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> int:
    """Make migrations."""
    walk = infra.walk_storage_from_command(command, filesystem)

    total_migrations = 0
    for branch, leaf, leaf_folder in walk:
        unit_file_path = filesystem.join(leaf_folder, constants.UNIT_FILE_NAME)

        if filesystem.not_exists(unit_file_path):
            stdout.gray(f'\t[{branch}][{leaf}] Unit file does not exist')
            continue

        migration_file_path = filesystem.join(leaf_folder,
                                              constants.MIGRATION_FILE_NAME)

        if filesystem.exists(migration_file_path) and not command.force:
            stdout.cyan(f'\t[{branch}][{leaf}] Migration file already exist')
            continue

        content = filesystem.read_json(unit_file_path)
        new_migrations = schema.instantiate_commands(content=content)
        save_migrations(
            leaf_folder=leaf_folder,
            migrations=new_migrations,
            filesystem=filesystem,
        )
        stdout.green(f'\t[{branch}][{leaf}] Created migration file')
        total_migrations += len(new_migrations)

    return total_migrations


def save_migrations(leaf_folder: str,
                    migrations: List[classes.SQL],
                    filesystem: infra.Filesystem) -> str:
    """Save migration as SQL file."""
    file_path = filesystem.join(leaf_folder, constants.MIGRATION_FILE_NAME)
    filesystem.write_file(file_path, ';\n'.join(map(str, migrations)))
    return file_path
