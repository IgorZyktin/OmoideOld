# -*- coding: utf-8 -*-
"""Main state keeper.
"""
from threading import Lock

from omoide import infra
from omoide.index_server.index import Index
from omoide.index_server.status import Status


class Singleton(metaclass=infra.SingletonMeta):
    """Main state keeper.
    """
    lock: Lock
    index: Index
    status: Status
    filesystem: infra.Filesystem
    stdout: infra.STDOut
    db_path: str
