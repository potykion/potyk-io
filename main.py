import os

from flask import Flask

from potyk_io_back.potyk_io.pres import potyk_io_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]
    app.register_blueprint(potyk_io_bp)
    return app
