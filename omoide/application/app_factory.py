# -*- coding: utf-8 -*-
"""Application.
"""
from functools import partial

import flask
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

import omoide.constants.project
import omoide.database.operations
from omoide import commands, constants, utils
from omoide import search_engine
from omoide.application import database, logic
from omoide.application.class_web_query import WebQuery


# pylint: disable=too-many-locals
def create_app(command: commands.RunserverCommand,
               engine: Engine) -> flask.Flask:
    """Create web application instance."""
    app = flask.Flask(import_name='omoide',
                      template_folder=command.templates_folder,
                      static_folder=command.static_folder)
    Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name
    query_builder = search_engine.QueryBuilder(search_engine.Query)

    with omoide.database.operations.session_scope(Session) as _session:
        search_index = database.get_index(_session)

    version = f'Version: {constants.VERSION}'

    @app.route('/')
    def index():
        """Entry page."""
        return flask.render_template('index.html')

    @app.context_processor
    def common_names():
        """Populate context with common names."""
        return {
            'title': 'Omoide',
            'note': version,
            'injection': command.injection,
            'byte_count_to_text': utils.byte_count_to_text,
            'sep_digits': utils.sep_digits,
            'web_query': '',
            'search_report': [],
        }

    @app.errorhandler(404)
    def page_not_found(exc):
        """Return not found page."""
        # TODO
        assert exc
        context = {
        }
        return flask.render_template('404.html', **context), 404

    @app.route('/navigation')
    def navigation():
        """Show selection fields for realm/theme."""
        web_query = WebQuery.from_request(flask.request.args)
        context = logic.make_navigation_response(Session, web_query)
        return flask.render_template('navigation.html', **context)

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        """Main page of the application."""
        web_query = WebQuery.from_request(flask.request.args)

        if flask.request.method == 'POST':
            web_query['q'] = flask.request.form.get('query', '')
            return flask.redirect(flask.url_for('search') + str(web_query))

        context = logic.make_search_response(maker=Session,
                                             web_query=web_query,
                                             query_builder=query_builder,
                                             index=search_index)

        return flask.render_template('search.html', **context)

    @app.route('/preview/<uuid>')
    def preview(uuid: str):
        """Show description for a single record."""
        not_found = partial(flask.abort, 404)
        web_query = WebQuery.from_request(flask.request.args)
        context = logic.make_preview_response(maker=Session,
                                              web_query=web_query,
                                              uuid=uuid,
                                              abort_callback=not_found)
        return flask.render_template('preview.html', **context)

    @app.route('/tags')
    def tags():
        """Show available tags."""
        web_query = WebQuery.from_request(flask.request.args)
        context = logic.make_tags_response(Session, web_query)
        return flask.render_template('tags.html', **context)

    @app.route('/feedback', methods=['GET', 'POST'])
    def feedback():
        """Show feedback form."""
        greet = False
        web_query = WebQuery.from_request(flask.request.args)
        user_query = web_query.get('q')

        if flask.request.method == 'POST':
            name = flask.request.form.get('name', '')
            _feedback = flask.request.form.get('feedback', '')
            logic.save_feedback(command.database_folder, name, _feedback)
            greet = True

        context = {
            'greet': greet,
            'web_query': web_query,
            'user_query': user_query,
        }
        return flask.render_template('feedback.html', **context)

    if command.static:
        @app.route('/content/<path:filename>')
        def serve_content(filename: str):
            """Serve files from main storage.

            Contents of the main storage are served through this function.
            It's not about static css or js files. Not supposed to be used
            in production.
            """
            return flask.send_from_directory(command.content_folder,
                                             filename, conditional=True)

    return app
