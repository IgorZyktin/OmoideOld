# -*- coding: utf-8 -*-

"""Sync.
"""
from sqlalchemy.orm import sessionmaker, Session

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.database import operations
from omoide.database.operations import synchronize


# pylint: disable=too-many-locals
def act(command: commands.SyncCommand,
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
    for branch in filesystem.list_folders(command.storage_folder):

        if command.branch != 'all' and command.branch != branch:
            continue

        stdout.yellow(f'\t[{branch}]')
        branch_folder = filesystem.join(command.storage_folder, branch)
        branch_db_file = filesystem.join(branch_folder,
                                         constants.BRANCH_DB_FILE_NAME)

        if filesystem.exists(branch_db_file) and command.force:
            filesystem.delete_file(branch_db_file)

        needs_schema = filesystem.not_exists(branch_db_file)
        branch_db = operations.create_database(
            folder=branch_folder,
            filename=constants.BRANCH_DB_FILE_NAME,
            filesystem=filesystem,
            echo=False,
        )
        if needs_schema:
            operations.create_scheme(branch_db)

        session_branch = sessionmaker(bind=branch_db)()

        for leaf in filesystem.list_folders(branch_folder):

            if command.leaf != 'all' and command.leaf != leaf:
                continue

            leaf_folder = filesystem.join(branch_folder, leaf)
            leaf_db_file = filesystem.join(leaf_folder,
                                           constants.LEAF_DB_FILE_NAME)

            if not filesystem.exists(leaf_db_file):
                stdout.gray(f'\t[{branch}][{leaf}] Nothing to migrate')
                return 0

            total_migrations += sync_leaf(
                leaf_folder=leaf_folder,
                leaf=leaf,
                session_branch=session_branch,
                filesystem=filesystem,
                stdout=stdout,
            )

        synchronize(session_from=session_branch, session_to=session_root)
        total_migrations += 1
        stdout.green(f'\t[{branch}] Synchronized')
        branch_db.dispose()
        session_branch.close()

    root_db.dispose()
    session_root.close()

    return total_migrations


def sync_leaf(leaf_folder: str, leaf: str, session_branch: Session,
              filesystem: infra.Filesystem, stdout: infra.STDOut) -> int:
    """Synchronize leaf -> branch."""
    leaf_db = operations.create_database(folder=leaf_folder,
                                         filename=constants.LEAF_DB_FILE_NAME,
                                         filesystem=filesystem,
                                         echo=False)

    session_leaf = sessionmaker(bind=leaf_db)()

    synchronize(session_from=session_leaf, session_to=session_branch)
    stdout.yellow(f'\t * [{leaf}] Synchronized')
    leaf_db.dispose()
    session_leaf.close()
    return 1
