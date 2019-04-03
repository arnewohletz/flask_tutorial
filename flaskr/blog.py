from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

# define another blueprint
# there is no url_prefix, which means that this blueprint's root is '/'
bp = Blueprint('blog', __name__)

# render blog/index.html when 127.0.0.1:5000/ is called
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    # render index.html and pass posts variable into it
    return render_template('blog/index.html', posts=posts)

# render blog/create.html when 127.0.0.1:5000/create is called and user is logged in
# render auth/login when user is not logged in -> @login_required
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# return a post content as dict if the logged in user matches that blog's author
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # 'abort' raises a special exception that returns the HTTP status code
    # here: unknown blog id
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # here: logged in user is not equal to author id
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# renders blog/update.html if 127.0.0.1:5000/<blog_id>/update is called
# when triggered via POST request, the blog data is overwritten and user
# redirected to 127.0.0.1:5000/index
# Example URL: 127.0.0.1:5000/23/update
# id must be of type integer
# If triggered via GET request, the blog/update.html page is rendered
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Here the values are updated -> create() method uses INSERT
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# another view that can only be accessed via POST request
# it deletes the post from the database
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
