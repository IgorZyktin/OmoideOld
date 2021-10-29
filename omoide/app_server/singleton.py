# -*- coding: utf-8 -*-
"""Main state keeper.
"""
from typing import Type

from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from omoide import infra, search_engine


class Singleton(metaclass=infra.SingletonMeta):
    """Main state keeper.
    """
    version: str
    injection: str
    serve_static: bool
    content_folder: str
    database_folder: str
    db_path: str
    templates: Jinja2Templates
    session: Type[AsyncSession]
    query_builder: search_engine.QueryBuilder
