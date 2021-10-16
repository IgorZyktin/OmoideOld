# -*- coding: utf-8 -*-

"""Make migrations.
"""
from typing import List

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.infra import walking
from omoide.migration_engine import classes
from omoide.migration_engine.classes import passport as passport_module
from omoide.migration_engine.operations.make_migrations import schema


def run_make_migrations(command: commands.MakeMigrationsCommand,
                        filesystem: infra.Filesystem,
                        stdout: infra.STDOut) -> int:
    """Make migrations."""
    total_migrations = 0
    for top in walking.traverse_top(command, filesystem):
        stdout.print(f'\t{top}')

        for bottom in walking.traverse_bottom(command, top):
            unit_file_path = filesystem.join(
                bottom.leaf_folder,
                constants.UNIT_FILE_NAME,
            )

            if filesystem.not_exists(unit_file_path):
                stdout.gray(f'\t\t{bottom} Unit file does not exist')
                continue

            passport = passport_module.load_from_file(bottom)

            if passport.already_processed(
                    bottom, unit_file_path,
                    passport.make_migrations.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t{bottom} Migrations already created')
                continue

            content = filesystem.read_json(unit_file_path)
            new_migrations = schema.instantiate_commands(content=content)

            save_migrations(bottom, new_migrations)

            stdout.green(f'\t\t{bottom} Created migration file')
            total_migrations += len(new_migrations)
            passport.register_make_migrations(bottom, unit_file_path)
            passport.save_to_file(bottom)

    return total_migrations


def save_migrations(bottom: walking.Bottom,
                    migrations: List[classes.SQL]) -> str:
    """Save migration as SQL file."""
    path = bottom.filesystem.join(
        bottom.leaf_folder,
        constants.MIGRATION_FILE_NAME,
    )
    new_migrations = ';\n'.join(map(str, migrations))
    bottom.filesystem.write_file(path, new_migrations)
    return path
