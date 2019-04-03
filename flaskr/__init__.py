import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # have your tests use a different config than the real application
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # import the db module, which contains the function init_app()
    from . import db
    db.init_app(app)

    # register the blueprint ('auth.bd')
    from . import auth
    app.register_blueprint(auth.bp)

    # register another blueprint ('blog.bp') -> associated with 'blog.bp'
    from . import blog
    app.register_blueprint(blog.bp)
    # since the blog's index.html is supposed to reside in /, and hence is usually
    # associated to via 'blog.index' is also supposed to be associated via 'index'
    # so
    app.add_url_rule('/', endpoint='index')

    return app
