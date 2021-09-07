# -*- coding: utf-8 -*-

"""Actual code of the script.
"""
import gzip
import os
from typing import List, Dict

import sqlalchemy
from sqlalchemy.engine import Engine


def gather_filenames(folder: str) -> List[str]:
    """Get log filenames from logs folder."""
    all_filenames = os.listdir(folder)

    def is_access(filename: str) -> bool:
        """Return True for access prefixes."""
        return filename.startswith('custom')

    def is_correct_ext(filename: str) -> bool:
        """Return True for log and gz files."""
        return filename.endswith('.log') or filename.endswith('.gz')

    return [x for x in all_filenames
            if is_access(x) and is_correct_ext(x)]


def get_lines(path: str) -> List[str]:
    """Get contents of the file as list of strings."""
    if path.endswith('.log'):
        with open(path, mode='r', encoding='utf-8') as file:
            contents = file.readlines()
    elif path.endswith('.gz'):
        with gzip.open(path, mode='rb') as file:
            contents = file.read().decode('utf-8').split('\n')
    else:
        raise NameError(f'Unknown file extension: {path}')

    return contents


def split_line(raw_request: str) -> Dict[str, str]:
    """Separate request into parts."""
    parts = raw_request.split('|')

    if not parts:
        return {}

    ts, ip, stat, sent, dur, length, url, ref, ag = parts

    request = {
        'time': ts,
        'ip': ip,
        'status': stat,
        'bytes_sent': int(sent),
        'request_time': float(dur),
        'request_length': int(length),
        'url': url,
        'referer': ref,
        'user_agent': ag,
    }

    return request


def dump_request(request: dict, conn, table) -> None:
    """Save request to the database."""
    stmt = table.insert().values(**request)
    conn.execute(stmt)


def get_newest_time(engine: Engine, table) -> str:
    """Find time of the newest request."""
    stmt = sqlalchemy.select(sqlalchemy.func.max(table.c.time))

    with engine.begin() as conn:
        response = conn.execute(stmt).scalar()

    return response or ''
