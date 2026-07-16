from flask import Flask
from flask_cors import CORS

from app.core.config import Config
from app.core.extensions import db, login_manager, migrate
from app.core.menu import MENU


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    app.context_processor(lambda: {"MENU": MENU})

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Flask-Login user loader
    from app.core import auth

    # Import models agar terdeteksi Alembic
    from app import models

    # Register Blueprint
    from app.auth import bp as auth_bp
    from app.dashboard import bp as dashboard_bp
    from app.employees import bp as employees_bp
    from app.attendance import bp as attendance_bp
    from app.departments import bp as departments_bp
    from app.positions import bp as positions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(positions_bp)

    @app.template_filter("smart_hours")
    def smart_hours(value):
        if value is None:
            return "-"

        if float(value).is_integer():
            return int(value)

        return value

    return app
