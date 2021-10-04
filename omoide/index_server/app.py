# -*- coding: utf-8 -*-
"""Application server.
"""

import fastapi

from omoide.index_server import find
from omoide.index_server import objects
from omoide.index_server import reload
from omoide.index_server import singleton
from omoide.index_server import status

app = fastapi.FastAPI(openapi_url=None, docs_url=None, redoc_url=None)


async def get_singleton():
    """Get instance of a global state."""
    return singleton.Singleton()


@app.get('/')
async def do_search(
        query: objects.Query,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_model=objects.SearchResult):
    """Perform search on the in-memory database."""
    with state.lock:
        if query:
            result = find.specific_records(query, state.index)
        else:
            result = find.random_records(query, state.index)
    return result


@app.get('/status')
async def do_status(
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_model=status.Status):
    """Describe current state of the server."""
    return state.status


@app.post('/reload')
async def do_reload(
        state: singleton.Singleton = fastapi.Depends(get_singleton)):
    """Rebuild index."""
    await reload.do_reload(state)
    return {'result': 'Started reloading'}


@app.post('/update_root')
async def do_root_update(
        path: objects.NewDbPath,
        state: singleton.Singleton = fastapi.Depends(get_singleton)):
    """Refresh root folder location."""
    state.db_path = path.db_path
    return {'result': f'Now using {state.db_path}'}


@app.get('/healthcheck')
async def do_healthcheck():
    """Return something that can be used as service health check."""
    return {'result': 'ok'}


# FIXME
import uvicorn
uvicorn.run(app)
