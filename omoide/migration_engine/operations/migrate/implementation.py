# -*- coding: utf-8 -*-

"""Migrate.
"""
import sqlalchemy as sa

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.database import operations
from omoide.infra import walking
from omoide.migration_engine.classes import passport as passport_module


# pylint: disable=too-many-locals
def run_migrate(command: commands.MigrateCommand,
                filesystem: infra.Filesystem,
                stdout: infra.STDOut) -> int:
    """Migrate."""
    total_new_migrations = 0
    for top in walking.traverse_top(command, filesystem):
        stdout.print(f'\t{top}')

        for bottom in walking.traverse_bottom(command, top):
            migration_path = filesystem.join(bottom.leaf_folder,
                                             constants.MIGRATION_FILE_NAME)

            if not filesystem.exists(migration_path):
                stdout.gray(f'\t\t{bottom} Migration file does not exist')
                continue

            passport = passport_module.load_from_file(bottom)
            local_db_path = filesystem.join(bottom.leaf_folder,
                                            constants.LEAF_DB_FILE_NAME)

            if passport.already_processed(
                    bottom, local_db_path,
                    passport.migrate.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t{bottom} Migrations already applied')
                continue

            if filesystem.exists(local_db_path):
                filesystem.delete_file(local_db_path)
                new_migration = False
            else:
                new_migration = True

            engine = operations.restore_database_from_scratch(
                folder=bottom.leaf_folder,
                filename=constants.LEAF_DB_FILE_NAME,
                filesystem=filesystem,
                echo=False,
            )

            content = filesystem.read_file(migration_path)
            migrations = content.split(';')

            with engine.connect() as conn:
                trans = conn.begin()
                try:
                    for migration in migrations:
                        conn.execute(sa.text(migration))
                    trans.commit()
                except Exception:
                    trans.rollback()
                    raise

            total_new_migrations += len(migrations)

            if new_migration:
                stdout.green(f'\t\t{bottom} Applied migrations')
            else:
                stdout.yellow(f'\t\t{bottom} Re-applied migrations')

            passport.register_migrate(bottom, local_db_path)
            passport.save_to_file(bottom)

    return total_new_migrations
