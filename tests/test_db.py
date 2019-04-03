import sqlite3

import pytest
from flaskr.db import get_db # get database content as dict

# test if the database returns the same content each time it is called.
# The application context must be accessible for all test modules
# outside of the factory, because only then can it be used
def test_get_close_db(app):
    with app.app_context(): # access application context
        db = get_db() # get database content
        assert db is get_db() # compare first db content with second

    # mock a sqlite3.ProgrammingError on the enclosed command
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    # assert that ---> I don't get this. Why should 'closed' be within the
    # string representation of the ProgrammingError???
    assert 'closed' in str(e)


# CLI test runner is passed into the function
# monkeypatch import needed to prevent actual initialization of the db
# but instead only checking the CLI output message ("Initializing the database")
def test_init_db_command(runner, monkeypatch):
    # set up recorder to verify that fake_init_db() has been executed
    class Recorder(object):
        called = False

    # fake init_db function that only sets the Recorder.called flag
    def fake_init_db():
        Recorder.called = True

    # monkeypatch is used to replace flaskr.db.init_db view function
    # with the fake_init_db
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # issue CLI command 'flask init-db'
    result = runner.invoke(args=['init-db'])
    # Checking CLI ouput message
    assert 'Initialized' in result.output
    # Checking if fake_init_db executed
    assert Recorder.called
