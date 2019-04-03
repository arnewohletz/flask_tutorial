from flaskr import create_app


def test_config():
    # check that testing flag is not set when passing no arguments
    assert not create_app().testing
    # check that testing flag is set when passing 'testing' argument
    assert create_app({'TESTING': True}).testing

# flask exposes the werkzeug client which can be utilized to send requests
# to an application
# see: https://werkzeug.palletsprojects.com/en/0.15.x/test/#werkzeug.test.Client.get
def test_hello(client):
    # get() makes a GET request to the application
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
