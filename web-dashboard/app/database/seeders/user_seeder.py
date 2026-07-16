from app.core.extensions import db
from app.models.enums import UserRole
from app.models.user import User


def seed_user():
    user = db.session.query(User).filter_by(username="admin").first()

    if user:
        print("✓ Admin already exists")
        return

    admin = User(
        username="admin",
        full_name="Administrator",
        role=UserRole.SUPER_ADMIN,
    )

    admin.set_password("tmoadmin123")

    db.session.add(admin)

    print("✓ Admin created")