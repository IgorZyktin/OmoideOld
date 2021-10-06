# -*- coding: utf-8 -*-
"""Server status object.
"""
import datetime

from omoide import utils

STATUS_INIT = 'init'
STATUS_ACTIVE = 'active'
STATUS_RELOADING = 'reloading'
STATUS_FAILED = 'failed'


class Status:
    """Description of the server status."""

    def __init__(self, now: datetime.datetime) -> None:
        """"""
        self.index_status = STATUS_INIT
        self.server_last_restart = now
        self.index_last_reload = now
        self.index_last_reload_duration = 0
        self.index_comment = ''
        self.index_records = 0
        self.index_buckets = 0
        self.index_avg_bucket = 0.0
        self.index_min_bucket = 0
        self.index_max_bucket = 0
        self.index_size = '0 B'

    async def make_report(self, now: datetime.datetime,
                          server_size: str, version: str) -> dict:
        """Format server state as a dictionary."""
        server_uptime = int((now - self.server_last_restart).total_seconds())
        index_uptime = int((now - self.index_last_reload).total_seconds())
        return {
            'version': version,
            'server_last_restart': str(self.server_last_restart),
            'server_uptime': utils.human_readable_time(server_uptime),
            'server_size': server_size,
            'index_status': self.index_status,
            'index_last_reload': str(self.index_last_reload),
            'index_last_reload_duration': self.index_last_reload_duration,
            'index_uptime': utils.human_readable_time(index_uptime),
            'index_comment': self.index_comment,
            'index_records': self.index_records,
            'index_buckets': self.index_buckets,
            'index_avg_bucket': self.index_avg_bucket,
            'index_min_bucket': self.index_min_bucket,
            'index_max_bucket': self.index_max_bucket,
            'index_size': self.index_size,
        }
