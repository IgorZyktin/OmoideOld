# -*- coding: utf-8 -*-
"""Main state keeper.
"""

from omoide import infra


class Singleton(metaclass=infra.SingletonMeta):
    """Main state keeper.
    """
    version: str
    injection: str
