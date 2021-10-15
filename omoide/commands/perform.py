# -*- coding: utf-8 -*-

"""Command line command execution.
"""
from omoide import commands, infra


def perform_unite(command: commands.UniteCommand,
                  filesystem: infra.Filesystem,
                  stdout: infra.STDOut) -> None:
    """Perform unite command."""
    from omoide.migration_engine.operations.unite import implementation
    stdout.magenta('[UNITE] Parsing source files and making unit files')
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
    from omoide.migration_engine import operations as migration_operations
    stdout.magenta('[MIGRATE] Applying migrations')
    total = migration_operations.migrate.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} migration operations applied')


def perform_relocate(command: commands.RelocateCommand,
                     filesystem: infra.Filesystem,
                     stdout: infra.STDOut) -> None:
    """Perform relocation command."""
    from omoide.migration_engine import operations as migration_operations
    stdout.magenta('[RELOCATE] Applying relocations')
    total = migration_operations.relocate.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} relocation operations applied')


def perform_sync(command: commands.SyncCommand,
                 filesystem: infra.Filesystem,
                 stdout: infra.STDOut) -> None:
    """Perform sync command."""
    from omoide.migration_engine import operations as migration_operations
    stdout.magenta('[SYNC] Synchronizing databases')
    total = migration_operations.sync.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} databases synchronized')


def perform_freeze(command: commands.FreezeCommand,
                   filesystem: infra.Filesystem,
                   stdout: infra.STDOut) -> None:
    """Perform freeze command."""
    from omoide.migration_engine import operations as migration_operations
    stdout.magenta('[FREEZE] Making static database')
    migration_operations.freeze.act(
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
    from omoide.migration_engine import operations as migration_operations
    stdout.magenta('[SHOW_TREE] Displaying folder tree')
    total = migration_operations.show_tree.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Got {total} subfolders')


def perform_run_index(command: commands.RunIndexCommand,
                      filesystem: infra.Filesystem,
                      stdout: infra.STDOut) -> None:
    """Perform command."""
    from omoide.index_server import implementation
    stdout.magenta('[RUN_INDEX] Starting index server')
    implementation.run_index(command=command,
                             filesystem=filesystem,
                             stdout=stdout)
