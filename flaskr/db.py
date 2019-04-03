import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# use 'g' (application context object) to store request as attribute
# 'current_app' is used since ./__init__.py does not save the 'app' variable
# hence it is not available here without importing it
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Define which type a data row is returned as (here: sqlite3.Row)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    # Remove database from 'g'
    db = g.pop('db', None)

    # If still there, it is closed
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    # open schema.sql file for application (same as 'open' in common python)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# define click command
@click.command('init-db')
# make sure, that 'init_db_command' is available as callback function in the
# applications context (can then be called via current_app.init_db_command())
# By doing so, app does not need to be imported here
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # 'close_db()' and 'init_db_command()' functions must be registered to be
    # available from within the application instance. Since the application is
    # created by a factory (see __init__()), the instance isn't available when
    # writing the functions (cannot use 'app' here), we must make these available.
    #
    # app.teardown_appcontext(func): assign a function that is called when the
    # app context, that handles the current request is ended. This happens
    # after the response is sent and the context is popped from the stack of
    # active contexts.
    # For each new request, a new app context is created (and also a request context,
    # that behaves similar but created after the app context and is destroyed
    # before the app context is destroyed) which contains a full
    # functional copy of the original application. This copy is pushed onto the
    # active contexts stack. This copy is referenced as 'current_app'
    #
    # Here we pass in the 'app' Application instance, and assign the 'close_db()'
    # function to the 'teardown_appcontext' attribute ('close_db' is the executed
    # when application context is pulled from the stack)
    # to application parameters (here: 'teardown_appcontext' & 'cli.add_command')
    # tell flask to call the 'close_db()' function when application context ends
    # an application context ends when
    app.teardown_appcontext(close_db)
    # Here we add a new cli command, which is the function init_db_command
    # Since above, this is defined as click command (@click.command('init-db'))
    # it can now be executed via: flask init-db
    app.cli.add_command(init_db_command)
