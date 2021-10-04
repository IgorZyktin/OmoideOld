# -*- coding: utf-8 -*-

"""Run production index server.
"""
import uvicorn

from omoide import commands
from omoide import infra
from omoide.constants import storage as storage_constants
from omoide.index_server.app import app
from omoide.index_server.singleton import Singleton


def act(command: commands.RunserverCommand,
        filesystem: infra.Filesystem,
        stdout: infra.STDOut) -> None:
    """Run dev server."""
    singleton = Singleton()
    singleton.filesystem = filesystem
    singleton.stdout = stdout
    singleton.db_path = filesystem.join(command.database_folder,
                                        storage_constants.STATIC_DB_FILE_NAME)

    uvicorn.run(app, host=command.host, port=command.port)
