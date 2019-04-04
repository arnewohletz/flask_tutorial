import pytest
from flaskr.db import get_db

# using client and auth fixture
def test_index(client, auth):
    response = client.get('/')
    # Check if 'Log In' is in response.data
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')

    assert b'Log Out' in response.data # OK -> Logout button
    assert b'test title' in response.data # OK -> Initial first post title
    assert b'by test on 2018-01-01' in response.data # OK -> Initial first post date
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data # OK -> Edit link for post 1

# check if webpages redirects to login page when attempting to send POST
# request to create, delete or update a post entry (because of @login.required
# fixture for all these view functions)
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

# test that other user's post cannot be edited
def test_author_required(app, client, auth):
    # change the post author to another user (again: entering applications context
    # is required here)
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data

# test that attempting to edit not existing posts leads to 404 error return code
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

# test if adding a post increases entries in database by 1
def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

# test if editing (initinal) post tile is applied
def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


# test that a post cannot be updated with an empty title
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

# test whether user is navigated to '/' when post is deleted
# and whether this post was deleted from the database
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
