import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    # creating a temporary, secure file in current file's directory
    # first returned value is the opened file
    # second returned value is the absolute path to this file
    db_fd, db_path = tempfile.mkstemp()

    # app is instantiated setting passing a test_config dict
    # the database is set to temporary file
    # testing is a built-in variable which propagates any occuring errors rather
    # than handling them
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    # access the application context and create database
    # then execute given sql script
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    # start test execution here and pass application into tests
    yield app

    # as a test teardown, close the file and deletes it
    os.close(db_fd)
    os.unlink(db_path)

# fixture which passes the app's test_client into the decorated test function
# test_client is then interacting with the flask application during tests
@pytest.fixture
def client(app):
    return app.test_client()

# fixture which passes the app's test_cli_runner into the decorated test function
# test_cli_runner is a FLaskCliRunner instance, used to test CLI commands
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# class defines methods that login and logout a user
# this is important, since the authentification tests require a user to be
# either logged in or logged out
class AuthActions(object):
    # constructor utilizes the Werkzeug client to make requests
    def __init__(self, client):
        self._client = client

    # returns a POST request that calls the application's login method using the passed in
    # user credentials
    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    # returns a GET request that calls the applicatin's logout method
    def logout(self):
        return self._client.get('/auth/logout')

# passes user authentification class to test
@pytest.fixture
def auth(client):
    return AuthActions(client)
