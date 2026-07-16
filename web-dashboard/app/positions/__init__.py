from flask import Blueprint

bp = Blueprint(
    "positions",
    __name__,
    url_prefix="/positions",
)

from . import routes