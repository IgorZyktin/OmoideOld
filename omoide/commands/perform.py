# -*- coding: utf-8 -*-

"""Command line command execution.
"""
import time
from contextlib import contextmanager

from omoide import commands, infra
from omoide import utils


@contextmanager
def chronograph(stdout: infra.STDOut) -> None:
    """Calculate and print time of execution."""
    start = time.monotonic()
    try:
        yield
    finally:
        duration = time.monotonic() - start
        string = utils.human_readable_time(int(duration))
        stdout.magenta(f'Operation took: {string}')


def perform_unite(command: commands.UniteCommand,
                  filesystem: infra.Filesystem,
                  stdout: infra.STDOut) -> None:
    """Perform unite command."""
    from omoide.migration_engine.operations.unite import implementation
    stdout.magenta('[UNITE] Parsing source files and making unit files')

    with chronograph(stdout):
        total = implementation.run_unite(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} unit files created')


def perform_make_migrations(command: commands.MakeMigrationsCommand,
                            filesystem: infra.Filesystem,
                            stdout: infra.STDOut) -> None:
    """Perform unite command."""
    from omoide.migration_engine.operations \
        .make_migrations import implementation
    stdout.magenta('[MAKE MIGRATIONS] Creating migration files')

    with chronograph(stdout):
        total = implementation.run_make_migrations(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} migration operations created')


def perform_make_relocations(command: commands.MakeRelocationsCommand,
                             filesystem: infra.Filesystem,
                             stdout: infra.STDOut) -> None:
    """Perform make_relocations command."""
    from omoide.migration_engine.operations \
        .make_relocations import implementation
    stdout.magenta('[MAKE RELOCATIONS] Creating relocation files')

    with chronograph(stdout):
        total = implementation.run_make_relocations(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} relocation operations created')


def perform_migrate(command: commands.MigrateCommand,
                    filesystem: infra.Filesystem,
                    stdout: infra.STDOut) -> None:
    """Perform migration command."""
    from omoide.migration_engine.operations.migrate import implementation
    stdout.magenta('[MIGRATE] Applying migrations')

    with chronograph(stdout):
        total = implementation.run_migrate(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} migration operations applied')


def perform_relocate(command: commands.RelocateCommand,
                     filesystem: infra.Filesystem,
                     stdout: infra.STDOut) -> None:
    """Perform relocation command."""
    from omoide.migration_engine.operations.relocate import implementation
    stdout.magenta('[RELOCATE] Applying relocations')

    with chronograph(stdout):
        total = implementation.run_relocate(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} relocation operations applied')


def perform_sync(command: commands.SyncCommand,
                 filesystem: infra.Filesystem,
                 stdout: infra.STDOut) -> None:
    """Perform sync command."""
    from omoide.migration_engine.operations.sync import implementation
    stdout.magenta('[SYNC] Synchronizing databases')

    with chronograph(stdout):
        total = implementation.run_sync(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta(f'Total {total} databases synchronized')


def perform_freeze(command: commands.FreezeCommand,
                   filesystem: infra.Filesystem,
                   stdout: infra.STDOut) -> None:
    """Perform freeze command."""
    from omoide.migration_engine.operations.freeze import implementation
    stdout.magenta('[FREEZE] Making static database')

    with chronograph(stdout):
        implementation.run_freeze(
            command=command,
            filesystem=filesystem,
            stdout=stdout,
        )
        stdout.magenta('Successfully created static database')


def perform_runserver(command: commands.RunserverCommand,
                      filesystem: infra.Filesystem,
                      stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.application import runserver
    stdout.magenta('[RUNSERVER] Starting development server')
    runserver.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )


def perform_show_tree(command: commands.ShowTreeCommand,
                      filesystem: infra.Filesystem,
                      stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.migration_engine.operations.show_tree import implementation
    stdout.magenta('[SHOW_TREE] Displaying folder tree')
    implementation.run_show_tree(command=command,
                                 filesystem=filesystem,
                                 stdout=stdout)


def perform_rsync(command: commands.RSyncCommand,
                  filesystem: infra.Filesystem,
                  stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.migration_engine.operations.rsync import implementation
    stdout.magenta('[RSYNC] Synchronizing replica')
    with chronograph(stdout):
        total = implementation.run_rsync(command=command,
                                         filesystem=filesystem,
                                         stdout=stdout)
        stdout.magenta(f'Successfully synchronized {total} files')


def perform_run_index(command: commands.RunIndexCommand,
                      filesystem: infra.Filesystem,
                      stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.index_server import implementation
    stdout.magenta('[RUN_INDEX] Starting index server')
    implementation.run_index(command=command,
                             filesystem=filesystem,
                             stdout=stdout)


def perform_run_app(command: commands.RunAppCommand,
                    filesystem: infra.Filesystem,
                    stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.app_server import implementation
    stdout.magenta('[RUN_APP] Starting web application')
    implementation.run_app(command=command,
                           filesystem=filesystem,
                           stdout=stdout)
