# -*- coding: utf-8 -*-
"""Index server.

This component encapsulate search logic inside.

Initially, all of it were placed inside application. But since it used
Gunicorn with four workers, total launch time started to grow. At some moment
server restart stated taking too long from Gunicorn point of view, so
application could not even start. Separate server makes possible to contain
index only in a single exemplar for any amount of workers and also can easily
make hot reload of the index without downtime.

There is a possibility of a race condition. Some request may happen in same
exact moment as index reload. Since we usually only add content to the index,
this is considered as non critical situation. On the next search request user
will get new version of the content.
"""
import asyncio

import fastapi

from omoide.index_server import logic
from omoide.index_server import objects
from omoide.index_server import singleton


async def get_singleton() -> singleton.Singleton:
    """Get instance of a global state."""
    return singleton.Singleton()


async def quietly_update_index_on_start() -> None:
    """Initialize search index."""
    state = await get_singleton()
    asyncio.create_task(logic.reload(state))


app = fastapi.FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    on_startup=[quietly_update_index_on_start]
)


@app.get('/')
async def do_healthcheck() -> dict:
    """Return something that can be used as service health check."""
    return {'result': 'ok'}


@app.get('/search')
async def do_search(
        query: objects.Query,
        state: singleton.Singleton = fastapi.Depends(get_singleton)) -> dict:
    """Perform search on the in-memory database."""
    result = await logic.search(query, state)
    return result.dict()


@app.get('/status')
async def do_status(
        state: singleton.Singleton = fastapi.Depends(get_singleton)) -> dict:
    """Describe current state of the server.

    Example response:
    {
        "version": "2021-10-04",
        "server_last_restart": "2021-10-05 20:15:21.050520+00:00",
        "server_uptime": "15s",
        "server_size": "99.6 MiB",
        "index_status": "active",
        "index_last_reload": "2021-10-05 20:15:24.813976+00:00",
        "index_last_reload_duration": 3.74,
        "index_uptime": "11s",
        "index_comment": "",
        "index_records": 19733,
        "index_buckets": 20289,
        "index_avg_bucket": 0.97,
        "index_min_bucket": 1,
        "index_max_bucket": 17846,
        "index_size": "46.8 MiB"
    }
    """
    return await logic.format_status(state)


@app.post('/reload')
async def do_reload(
        state: singleton.Singleton = fastapi.Depends(get_singleton)) -> dict:
    """Rebuild index."""
    await logic.reload(state)
    return {'result': 'Started reloading'}


@app.post('/update_database_folder')
async def do_update_database_folder(
        path: objects.NewDbPath,
        state: singleton.Singleton = fastapi.Depends(get_singleton)) -> dict:
    """Refresh database file location.

    Example request:
    {
        "path": "/some/test/path.db"
    }

    Example response:
    {
        "result": "Now using '/some/test/path.db'"
    }
    """
    state.db_path = path.path or state.db_path
    return {'result': f'Now using {state.db_path!r}'}
