from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from potyk_io_back.auth.forms import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class SecretUser(UserMixin):
    def __init__(self, secret: str):
        self.secret = secret

    def get_id(self) -> str:
        return self.secret


def setup_login(app):
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(secret):
        return SecretUser(secret)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("auth.login", next=request.path))

    login_manager.init_app(app)


def _safe_next(next_url: str | None) -> str:
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return url_for("fin.index")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.is_submitted():
        if form.validate():
            login_user(SecretUser(form.secret.data))
            return redirect(_safe_next(request.args.get("next")))
        flash("неверный секрет", "error")
    return render_template("auth/login.html", form=form)


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
