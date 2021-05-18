# -*- coding: utf-8 -*-

"""Command line command execution.
"""
from omoide import commands, infra
from omoide.application import runserver
from omoide.migration_engine import operations as migration_operations


def perform_unite(command: commands.UniteCommand,
                  filesystem: infra.Filesystem,
                  stdout: infra.STDOut) -> None:
    """Perform unite command."""
    stdout.magenta('[UNITE] Parsing source files and making unit files')
    total = migration_operations.unite.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} unit files created')


def perform_make_migrations(command: commands.MakeMigrationsCommand,
                            filesystem: infra.Filesystem,
                            stdout: infra.STDOut) -> None:
    """Perform unite command."""
    stdout.magenta('[MAKE MIGRATIONS] Creating migration files')
    total = migration_operations.make_migrations.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} migration operations created')


def perform_make_relocations(command: commands.MakeRelocationsCommand,
                             filesystem: infra.Filesystem,
                             stdout: infra.STDOut) -> None:
    """Perform make_relocations command."""
    stdout.magenta('[MAKE RELOCATIONS] Creating relocation files')
    total = migration_operations.make_relocations.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Total {total} relocation operations created')


def perform_migrate(command: commands.MigrateCommand,
                    filesystem: infra.Filesystem,
                    stdout: infra.STDOut) -> None:
    """Perform migration command."""
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
    stdout.magenta('[FREEZE] Making static app_database')
    migration_operations.freeze.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta('Successfully created static app_database')


def perform_runserver(command: commands.RunserverCommand,
                      filesystem: infra.Filesystem,
                      stdout: infra.STDOut) -> None:
    """Perform command."""
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
    stdout.magenta('[SHOW_TREE] Displaying folder tree')
    total = migration_operations.show_tree.act(
        command=command,
        filesystem=filesystem,
        stdout=stdout,
    )
    stdout.magenta(f'Got {total} subfolders')
