# -*- coding: utf-8 -*-

"""Run dev server.
"""
import sys

from omoide import commands
from omoide import constants
from omoide import infra
from omoide.application.app_factory import create_app
from omoide.database import operations


def act(command: commands.RunserverCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> None:
    """Run dev server."""
    static_db_path = filesystem.join(command.database_folder,
                                     constants.STATIC_DB_FILE_NAME)

    if filesystem.not_exists(static_db_path):
        stdout.red(f'Source database does not exist: {static_db_path}')
        sys.exit(1)

    engine = operations.create_read_only_database(
        folder=command.database_folder,
        filename=constants.STATIC_DB_FILE_NAME,
        filesystem=filesystem,
        echo=False,
    )

    app = create_app(command, engine)
    app.run(host=command.host, port=command.port, debug=command.reload)
