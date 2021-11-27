# -*- coding: utf-8 -*-
"""Application server.

This component is facing toward the user and display search results.
"""
import asyncio
import http

import fastapi
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import RedirectResponse

from omoide import utils
from omoide.app_server import singleton, logic
from omoide.app_server.class_web_query import WebQuery


async def get_singleton() -> singleton.Singleton:
    """Get instance of a global state."""
    return singleton.Singleton()


app = fastapi.FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)


@app.get('/')
@app.get('/search')
@app.post('/search')
async def search(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse | RedirectResponse):
    """Main page of the application."""
    web_query = WebQuery.from_request(request.query_params)

    if request.method == 'POST':
        form = await request.form()
        web_query['q'] = form.get('query', '')
        return RedirectResponse(request.url_for('search') + str(web_query),
                                status_code=http.HTTPStatus.SEE_OTHER)

    async with state.session() as session:
        response = await logic.make_search_response(session, web_query,
                                                    state.query_builder)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'injection': state.injection,
        **response,
    }
    return state.templates.TemplateResponse('index.html', context)


@app.get('/preview/{uuid}')
async def show_preview(
        request: fastapi.Request,
        uuid: str,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show selection fields for themes."""
    web_query = WebQuery.from_request(request.query_params)

    def abort_callback():
        raise fastapi.HTTPException(status_code=404)

    async with state.session() as session:
        response = await logic.make_preview_response(session, web_query,
                                                     uuid, abort_callback)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'byte_count_to_text': utils.byte_count_to_text,
        'injection': state.injection,
        **response,
    }
    return state.templates.TemplateResponse('preview.html', context)


@app.get('/tags')
async def show_tags(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show available tags."""
    web_query = WebQuery.from_request(request.query_params)

    async with state.session() as session:
        response = await logic.make_tags_response(session, web_query)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'byte_count_to_text': utils.byte_count_to_text,
        'sep_digits': utils.sep_digits,
        'injection': state.injection,
        **response,
    }
    return state.templates.TemplateResponse('tags.html', context)


@app.get('/newest')
async def show_newest(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show list of groups added on the last update."""
    web_query = WebQuery.from_request(request.query_params)

    async with state.session() as session:
        response = await logic.make_newest_response(session)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'injection': state.injection,
        **response,
    }
    return state.templates.TemplateResponse('newest.html', context)


@app.get('/navigation')
async def show_navigation(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show selection fields for themes."""
    web_query = WebQuery.from_request(request.query_params)

    async with state.session() as session:
        response = await logic.make_navigation_response(session, web_query)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'injection': state.injection,
        **response,
    }
    return state.templates.TemplateResponse('navigation.html', context)


@app.get('/feedback')
@app.post('/feedback')
async def show_feedback(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show feedback form."""
    greet = False
    web_query = WebQuery.from_request(request.query_params)

    if request.method == 'POST':
        form = await request.form()
        given_name = form.get('name', '')
        given_text = form.get('feedback', '')
        given_path = form.get('path', '')
        task = asyncio.to_thread(logic.save_feedback,
                                 state.database_folder,
                                 given_name,
                                 given_text,
                                 given_path)
        asyncio.create_task(task)
        greet = True

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'on_feedback_page': True,
        'greet': greet,
        'injection': state.injection,
    }
    return state.templates.TemplateResponse('feedback.html', context)


@app.get('/help')
async def show_help(
        request: fastapi.Request,
        state: singleton.Singleton = fastapi.Depends(get_singleton),
        response_class=HTMLResponse):
    """Show help page."""
    web_query = WebQuery.from_request(request.query_params)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
        'injection': state.injection,
    }
    return state.templates.TemplateResponse('help.html', context)


@app.exception_handler(StarletteHTTPException)
async def handle_errors(request: fastapi.Request, exc: fastapi.HTTPException,
                        response_class=HTMLResponse):
    """Return error page."""
    web_query = WebQuery.from_request(request.query_params)

    context = {
        'request': request,
        'web_query': web_query,
        'user_query': web_query.get('q'),
    }

    state = await get_singleton()

    if exc.status_code == 404:
        response = state.templates.TemplateResponse('404.html',
                                                    context, 404)
    else:
        response = state.templates.TemplateResponse('error.html',
                                                    context, exc.status_code)
    return response
