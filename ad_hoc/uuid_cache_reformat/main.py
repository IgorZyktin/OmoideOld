# -*- coding: utf-8 -*-

"""Script that changes cache files.
"""
import json
import os
from collections import defaultdict
from typing import Tuple

import sqlalchemy

DATABASE_PATH = 'D:\\PycharmProjects\\Omoide' \
                '\\omoide\\example\\database\\database.db'
STORAGE_PATH = 'D:\\PycharmProjects\\Omoide\\omoide\\example\\storage'


def iterate_on_sources(path: str):
    for path, dirs, files in os.walk(path):
        for file in files:
            if file == 'cache.json':
                yield os.path.join(path, file)


def read(path: str) -> dict:
    with open(path, mode='r', encoding='utf-8') as file:
        return json.load(file)


def write(path: str, content: dict) -> None:
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)


def get_group_filename_for_uuid(conn, uuid: str) -> Tuple[str, str]:
    stmt = sqlalchemy.text("""
    SELECT group_uuid, original_filename, original_extension 
    FROM metas WHERE uuid = :uuid
    """)
    group_uuid, filename, ext = conn.execute(stmt, {'uuid': uuid}).one()
    return group_uuid, f'{filename}.{ext}'


def get_uuid_for_filename(conn, filename: str) -> Tuple[str, str]:
    stmt = sqlalchemy.text("""
    SELECT uuid, group_uuid 
    FROM metas WHERE original_filename = :filename
    """)
    uuid, group_uuid = conn.execute(stmt, {'filename': filename}).one()
    return uuid, group_uuid


def handle_content(content: dict, conn):
    uuids = content.pop('uuids', {})
    files = defaultdict(dict)
    for group_uuid, elements in uuids.items():
        for filename, _ in elements.items():
            name = filename.split('.')[0]
            uuid, _group_uuid = get_uuid_for_filename(conn, name)
            files[group_uuid][filename] = uuid

    content['uuids'] = files


def main(storage: str, db_path: str):
    engine = sqlalchemy.create_engine(f'sqlite+pysqlite:///{db_path}')
    try:
        with engine.begin() as conn:
            for source_path in iterate_on_sources(storage):
                content = read(source_path)
                handle_content(content, conn)
                write(source_path, content)
                print(f'Complete', source_path)

    finally:
        engine.dispose()


if __name__ == '__main__':
    main(STORAGE_PATH, DATABASE_PATH)
