# -*- coding: utf-8 -*-

"""Run production index server.
"""
import os

import psutil
import uvicorn

from omoide import commands
from omoide import infra
from omoide import utils
from omoide.constants import storage as storage_constants
from omoide.index_server import constants, status, search_engine
from omoide.index_server.app import app
from omoide.index_server.singleton import Singleton


def run_index(command: commands.RunIndexCommand,
              filesystem: infra.Filesystem,
              stdout: infra.STDOut) -> None:
    """Run dev server."""
    singleton = Singleton()
    singleton.filesystem = filesystem
    singleton.stdout = stdout
    singleton.status = status.Status(utils.now())
    singleton.index = search_engine.Index([], {})
    singleton.process = psutil.Process(os.getpid())
    singleton.version = constants.VERSION

    singleton.db_path = filesystem.join(
        command.database_folder,
        storage_constants.STATIC_DB_FILE_NAME,
    )

    uvicorn.run(
        app,
        host=command.host or constants.HOST,
        port=command.port or constants.PORT,
    )
