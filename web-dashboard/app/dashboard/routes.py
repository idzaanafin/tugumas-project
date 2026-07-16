from flask import render_template
from flask_login import login_required

from . import bp
from .services import get_dashboard_summary


@bp.route("/")
@login_required
def home():
    return render_template("dashboard/home.html", summary=get_dashboard_summary())