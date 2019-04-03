import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# A blueprint contains multiple views
# A view function is a code you write to respond to requests

# Create a blueprint named 'auth', is defined in current file, so __name__ is
# passed. All URLs associated with this blueprint are prepended with 'auth'
# In practice, all blueprint files are saved within a directory named 'auth'
bp = Blueprint('auth', __name__, url_prefix='/auth')

# assign function to the blueprint (view function)
# assign function to URL '/function' and declare accepted request types
# this method allows GET and POST, but only POST makes the check
# when using GET, only the register.html page is displayed
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # 'url_for' creates the URL for the given endpoint
            # here: auth_login is used which refers to the login() function,
            # that is prepended by 'auth' due to the blueprint url_prefix setting
            # 'redirect' creates a respone object, that redirects client to the
            # specified location
            # Here, 'auth.login' refers to the auth/login.html
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

# registering another view functions
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # user_id is added to the session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# register a function that is executed before the view function
# here the attribute user is added to the 'g' context object (lives inside the
# application context)
@bp.before_app_request
def load_logged_in_user():

# The session object is a signed cookie, which can be used when a Flask.secret_key
# is configured, but in contrast to a cookie, the session is saved on the server.
# A session is saved on top of a cookie. A session cookie lasts until the
# client browser is closed, unless it is set to be permanent.
# The session object is like a dictionary that tracks modifications.
# Here, the 'user_id' key is retrieved.
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# the session can be emptied by calling the dict.clear() method
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# define a decorator (here: @login_required). The wrapped function is named 'view'
# using the convenience functin functools.wraps(f) enables a short definition
# of the wrapper function 'wrapped_view'
# This checks if context object 'g' has a value for attribute 'user' defined
# and redirects the user to /auth_login, if not
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
