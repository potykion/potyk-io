import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from potyk_io_back.core.db import db
from potyk_io_back.fin.auth import setup_login
from potyk_io_back.fin.entities import get_settings
from potyk_io_back.fin.pres import fin_bp
from potyk_io_back.potyk_io.pres import potyk_io_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "").lower() in {
        "1",
        "true",
        "yes",
    }
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    setup_login(app, fin_bp)
    app.register_blueprint(fin_bp)

    with app.app_context():
        db.create_all()
        get_settings()

    @app.template_filter("rub")
    def rub_filter(value: int) -> str:
        return f"{value:,}".replace(",", " ")

    app.register_blueprint(potyk_io_bp)
    return app
