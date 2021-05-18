# -*- coding: utf-8 -*-
"""Production application launcher.
"""

from omoide import commands, constants, infra
from omoide.application import app_factory
from omoide.database import operations

filesystem = infra.Filesystem()
root = filesystem.absolute('/media/pi/FLASH/omoide')
injection_path = filesystem.join(root, constants.INJECTION_FILE_NAME)

try:
    INJECTION = filesystem.read_file(injection_path)
except FileNotFoundError:
    INJECTION = ''

command = commands.RunserverCommand(
    reload=False,
    static=False,
    injection=INJECTION,
    database_folder=filesystem.join(root, constants.DATABASE_FOLDER_NAME),
    content_folder=filesystem.join(root, constants.CONTENT_FOLDER_NAME),
    templates_folder='/home/pi/Omoide/omoide/application/templates',
)

engine = operations.create_read_only_database(
    folder=filesystem.join(root, constants.DATABASE_FOLDER_NAME),
    filename=constants.STATIC_DB_FILE_NAME,
    filesystem=filesystem,
    echo=False,
)

app = app_factory.create_app(command, engine)
