# -*- coding: utf-8 -*-

"""Sync.
"""
from sqlalchemy.orm import sessionmaker, Session

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.database import operations
from omoide.database.operations import synchronize
from omoide.infra import walking
from omoide.migration_engine.classes import passport as passport_module


# pylint: disable=too-many-locals
def run_sync(command: commands.SyncCommand,
             filesystem: infra.Filesystem,
             stdout: infra.STDOut) -> int:
    """Synchronize databases.

    Step 1: From leaf to branch.
    Step 2: From branch to root.
    """
    root_db_file = filesystem.join(command.storage_folder,
                                   constants.ROOT_DB_FILE_NAME)

    if filesystem.exists(root_db_file) and command.force:
        filesystem.delete_file(root_db_file)

    needs_schema = filesystem.not_exists(root_db_file)
    root_db = operations.create_database(
        folder=command.storage_folder,
        filename=constants.ROOT_DB_FILE_NAME,
        filesystem=filesystem,
        echo=False,
    )
    if needs_schema:
        operations.create_scheme(root_db)

    SessionRoot = sessionmaker(bind=root_db)  # pylint: disable=invalid-name
    session_root = SessionRoot()

    total_migrations = 0
    for top in walking.traverse_top(command, filesystem):
        stdout.print(f'\t{top}')
        branch_folder = filesystem.join(command.storage_folder, top.branch)
        branch_db_path = filesystem.join(branch_folder,
                                         constants.BRANCH_DB_FILE_NAME)

        if filesystem.exists(branch_db_path) and command.force:
            filesystem.delete_file(branch_db_path)

        needs_schema = filesystem.not_exists(branch_db_path)
        branch_db = operations.create_database(
            folder=branch_folder,
            filename=constants.BRANCH_DB_FILE_NAME,
            filesystem=filesystem,
            echo=False,
        )
        if needs_schema:
            operations.create_scheme(branch_db)

        session_branch = sessionmaker(bind=branch_db)()

        for bottom in walking.traverse_bottom(command, top):

            leaf_folder = filesystem.join(branch_folder, bottom.leaf)
            leaf_db_path = filesystem.join(leaf_folder,
                                           constants.LEAF_DB_FILE_NAME)

            if not filesystem.exists(leaf_db_path):
                stdout.gray(f'\t\t{bottom} Nothing to migrate')
                continue

            if command.force:
                filesystem.delete_file(leaf_db_path)

            passport = passport_module.load_from_file(bottom)
            if passport.already_processed(
                    bottom, leaf_db_path,
                    passport.sync.fingerprints) \
                    and not command.force:
                stdout.cyan(f'\t\t{bottom} Migrations already applied')
                continue

            total_migrations += sync_leaf(
                bottom=bottom,
                session_branch=session_branch,
                stdout=stdout,
            )

            passport.register_sync(bottom, leaf_db_path)
            passport.save_to_file(bottom)

        synchronize(session_from=session_branch, session_to=session_root)

        total_migrations += 1
        stdout.green(f'\t{top} Synchronized')
        branch_db.dispose()
        session_branch.close()

    root_db.dispose()
    session_root.close()

    return total_migrations


def sync_leaf(bottom: walking.Bottom, session_branch: Session,
              stdout: infra.STDOut) -> int:
    """Synchronize leaf -> branch."""
    leaf_db = operations.create_database(folder=bottom.leaf_folder,
                                         filename=constants.LEAF_DB_FILE_NAME,
                                         filesystem=bottom.filesystem,
                                         echo=False)
    operations.create_scheme(leaf_db)
    session_leaf = sessionmaker(bind=leaf_db)()

    synchronize(session_from=session_leaf, session_to=session_branch)

    stdout.yellow(f'\t\t{bottom} Synchronized')
    session_leaf.close()
    leaf_db.dispose()
    return 1
