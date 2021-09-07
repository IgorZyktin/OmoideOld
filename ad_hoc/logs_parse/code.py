# -*- coding: utf-8 -*-

"""Actual code of the script.
"""
import gzip
import os
import re
from typing import List, Dict

import sqlalchemy
from sqlalchemy.engine import Engine


def gather_filenames(folder: str) -> List[str]:
    """Get log filenames from logs folder."""
    all_filenames = os.listdir(folder)

    def is_access(filename: str) -> bool:
        """Return True for access prefixes."""
        return filename.startswith('access')

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


REFERENCE_REQUEST = '66.249.70.29 - - [16/May/2021:00:04:06 +0300] ' \
                    '"GET /preview/all_themes/67de6f78-16de-4d37-a8f2' \
                    '-4b97bea35a24 HTTP/1.1" 200 2075 "-" "Mozilla/5.0 ' \
                    '(Linux; Android 6.0.1; Nexus 5X Build/MMB29P) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' \
                    '90.0.4430.97 Mobile Safari/537.36 (compatible; ' \
                    'Googlebot/2.1; +http://www.google.com/bot.html)"'

nginx_format = re.compile(
    r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) '
    r'- '
    r'- \[(?P<time>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} '
    r'(\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.1")) '
    r'(?P<statuscode>\d{3}) (?P<bytes>\d+) '
    r'(["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])',
    re.IGNORECASE
)


def split_line(raw_request: str) -> Dict[str, str]:
    """Separate request into parts."""
    parts = nginx_format.match(raw_request)
    if not parts:
        return {}

    groups = parts.groupdict()
    groups['time'] = normalize_time(groups['time'])

    return groups


def normalize_time(raw_time: str) -> str:
    """Convert time to ISO format.

    >>> normalize_time('[16/May/2021:00:04:06 +0300]')
    '2021-05-16T00:04:06+03:00'
    """
    raw_time = raw_time.strip('[]')
    day, hr_month, rest = raw_time.split('/')
    month = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12',
    }[hr_month.lower()]
    year, hours, minutes, rest = rest.split(':')
    seconds, timezone = rest.split(' ')
    timezone = timezone[:-2] + ':' + timezone[-2:]
    return f'{year}-{month}-{day}T{hours}:{minutes}:{seconds}{timezone}'


def dump_request(request: dict, conn, table) -> None:
    """Save request to the database."""
    request['bytes'] = int(request['bytes'])
    stmt = table.insert().values(**request)
    conn.execute(stmt)


def get_newest_time(engine: Engine, table) -> str:
    """Find time of the newest request."""
    stmt = sqlalchemy.select(sqlalchemy.func.max(table.c.time))

    with engine.begin() as conn:
        response = conn.execute(stmt).scalar()

    return response or ''
