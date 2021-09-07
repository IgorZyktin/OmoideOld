# -*- coding: utf-8 -*-

"""Script that parses NGINX logs.
"""
import os

import sqlalchemy
from sqlalchemy.engine import Engine

import code
import constants


def main() -> None:
    """Entry point."""
    db_path = os.path.join(constants.LOGS_FOLDER, constants.LOGS_DB_NAME)
    engine = sqlalchemy.create_engine(f'sqlite+pysqlite:///{db_path}')
    filenames = code.gather_filenames(constants.LOGS_FOLDER)

    if not filenames:
        print('Nothing to parse')
        return

    metadata = sqlalchemy.MetaData(bind=engine)
    table = sqlalchemy.Table(
        'requests',
        metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer,
                          primary_key=True, autoincrement=True),
        sqlalchemy.Column('time', sqlalchemy.String(25),
                          nullable=False, index=True),
        sqlalchemy.Column('ip', sqlalchemy.String(15),
                          nullable=False, index=True),
        sqlalchemy.Column('status', sqlalchemy.String(8),
                          nullable=False, index=True),
        sqlalchemy.Column('bytes_sent', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('request_time', sqlalchemy.Float, nullable=False),
        sqlalchemy.Column('request_length', sqlalchemy.Integer,
                          nullable=False),
        sqlalchemy.Column('url', sqlalchemy.Text,
                          nullable=False, index=True),
        sqlalchemy.Column('referer', sqlalchemy.Text, nullable=False),
        sqlalchemy.Column('user_agent', sqlalchemy.Text, nullable=False),
    )
    metadata.create_all()
    newest_time = code.get_newest_time(engine, table)
    if newest_time:
        print(f'Got newest time: {newest_time}')

    try:
        for filename in filenames:
            print('Handling', filename)
            handle_single_file(constants.LOGS_FOLDER, filename,
                               table, engine, newest_time)
    finally:
        engine.dispose()


def handle_single_file(path: str, filename: str,
                       table: sqlalchemy.Table, engine: Engine,
                       newest_time: str) -> None:
    """Parse and save contents of one file."""
    full_path = os.path.join(path, filename)
    lines = code.get_lines(full_path)

    with engine.begin() as conn:
        for line in lines:
            request = code.split_line(line)

            if not request:
                continue

            if request['time'] > newest_time:
                code.dump_request(request, conn, table)

    os.rename(full_path, os.path.join(path, '_' + filename))


if __name__ == '__main__':
    main()
