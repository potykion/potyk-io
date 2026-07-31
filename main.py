import os

import flask
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]

    @app.route("/")
    def index():
        return flask.render_template("index.html")



    return app
