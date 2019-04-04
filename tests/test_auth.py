import pytest
from flask import g, session
from flaskr.db import get_db

# during tests, 'with app.app_context()'' is always required when an action within
# the application is called without using a request.
# from the test perspective, the appliation is outside of its scope and cannot
# be accessed, but only requests can be made and response values checked.
# so if, for example, a database check should be made within a test, then this
# cannot be done with a request here, but the application's context must be accessed
# first and then the database can be queried

# the passed in 'client' is a werkzeug.test.Client instance, which allows to
# send requests to the application for testing purposes
def test_register(client, app):
    # test if GET request to /auth/register page returns proper status code
    assert client.get('/auth/register').status_code == 200
    # send a post request with valid user credentials
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # check if request redirects to the login page after the register is sent
    # the response.headers['Location'] value contains the URI of the
    # newly created resource (here: http://localhost/auth/login)
    # see: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
    assert 'http://localhost/auth/login' == response.headers['Location']

    # enter the app's context to acccess db directly
    with app.app_context():
        # check if user 'a' exists
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


# execute the decorated test function with these variables sets:
# 1. empty username and password
# 2. empty password
# 3. already registered user
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    # assign response object to be response object of a POST request
    # the data parameter overwrites all containing parameters values
    # existing in the associated view function
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # check if the message string is within the response's data
    # response.data is a string containing all ... CHECK DURING DEBUGGING
    assert message in response.data


# test login function (very similar to test_register)
# here, the 'auth' method is passed (since it is a fixture in conftest.py, it
# is available here), which is a AuthActions object that extends
# a client object with a special login() and logout() method that use a test
# user
# 'auth' is a fixture function (can never have arguments)
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login() # login with test user ()
    assert response.headers['Location'] == 'http://localhost/'

    # using client within a with statement allows accessing the context
    # variables, that are usually only accessible before the response is
    # returned (e.g. session)
    with client:
        client.get('/') # go to index page
        # check if session's user_id is '1', which should be the case since
        # it is assigned the value of the id field value in the database
        # and that should be '1' since it is the first registered user_id
        # and therefor has the id = 1 in the database .... THAT IS STRANGE
        # the user is logging in, but how can I be sure, the login is successful
        # since the user is not registered first ())or is he?)
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

# execute the decorated test function with these variables sets:
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    # check if correct message is in the response (same as above)
    response = auth.login(username, password)
    assert message in response.data
