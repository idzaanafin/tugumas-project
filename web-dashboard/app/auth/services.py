from app.core.extensions import db
from app.models.user import User


def get_user_by_username(username: str):
	username = username.strip()
	if not username:
		return None

	return db.session.query(User).filter_by(username=username).first()


def authenticate_user(username: str, password: str):
	user = get_user_by_username(username)

	if not user or not user.is_active:
		return None

	if not user.check_password(password):
		return None

	return user
