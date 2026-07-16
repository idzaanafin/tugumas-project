from app.core.extensions import login_manager
from app.core.extensions import db

from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)