# -*- coding: utf-8 -*-
"""Main state keeper.
"""
import psutil

from omoide import infra
from omoide.index_server.status import Status
from omoide.index_server.search_engine import Index


class Singleton(metaclass=infra.SingletonMeta):
    """Main state keeper.
    """
    index: Index
    status: Status
    filesystem: infra.Filesystem
    stdout: infra.STDOut
    db_path: str
    version: str
    process: psutil.Process
