from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import bp
from .services import authenticate_user


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(username, password)

        if user:
            login_user(user)
            flash("Login berhasil.", "success")
            return redirect(url_for("dashboard.home"))

        flash("Username atau password salah.", "danger")

    return render_template("auth/login.html", title="Login")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Berhasil logout.", "success")
    return redirect(url_for("auth.login"))