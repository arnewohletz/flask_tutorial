from flask import Flask, request
import flaskr

app = Flask(__name__)


def main():
    app.run()

# routing to address (two possibilities):
# 1.flask.Flask.route() decorator
@app.route("/")
def hello():
    return "Hello World"
# 2. flask.Flask.add_url_rule() function
def get_purpose():
    return "I am here to serve - that's why they call me server"
app.add_url_rule("/purpose", view_func=get_purpose)


# redirect /users/page/1 -> /users/
@app.route('/users/', defaults={'page': 1})
# set /users/page/N -> show_users(N) (N must be of type int)
# these converter types can be int, string, float and path (string with slashes)
@app.route('/users/page/<int:page>')
def show_users(page):
    return "Hello my friend"


if __name__ == "__main__":
    main()
