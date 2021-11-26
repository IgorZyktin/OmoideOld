# -*- coding: utf-8 -*-

"""Run production index server.
"""
import sys
from asyncio import current_task

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import sessionmaker

from omoide import commands, utils, search_engine
from omoide import infra
from omoide.app_server import constants
from omoide.app_server.app import app
from omoide.app_server.singleton import Singleton
from omoide.constants import storage as storage_constants
from omoide.database import operations


def run_app(command: commands.RunAppCommand,
            filesystem: infra.Filesystem,
            stdout: infra.STDOut) -> None:
    """Run dev server."""
    static_db_path = filesystem.join(command.database_folder,
                                     storage_constants.STATIC_DB_FILE_NAME)

    if filesystem.not_exists(static_db_path):
        stdout.red(f'Source database does not exist: {static_db_path}')
        sys.exit(1)

    engine = operations.create_async_read_only_database(
        folder=command.database_folder,
        filename=storage_constants.STATIC_DB_FILE_NAME,
        filesystem=filesystem,
        echo=False,
    )
    async_session_factory = sessionmaker(engine, class_=AsyncSession)
    AsyncScopedSession = async_scoped_session(async_session_factory,
                                              scopefunc=current_task)

    singleton = Singleton()
    singleton.filesystem = filesystem
    singleton.stdout = stdout
    singleton.version = constants.VERSION
    singleton.templates = Jinja2Templates(directory=command.templates_folder)
    singleton.content_folder = command.content_folder
    singleton.database_folder = command.database_folder
    singleton.db_path = filesystem.join(
        command.database_folder,
        storage_constants.STATIC_DB_FILE_NAME,
    )
    singleton.session = AsyncScopedSession
    singleton.query_builder = search_engine.QueryBuilder(search_engine.Query)

    if command.static:
        app.mount('/static',
                  StaticFiles(directory=command.static_folder),
                  name='static')
        app.mount('/content',
                  StaticFiles(directory=command.content_folder),
                  name='content')

    uvicorn.run(
        app,
        # 'omoide.app_server.app:app',
        host=command.host,
        port=command.port,
        debug=command.debug,
        # reload=command.reload,
    )
