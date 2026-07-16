from app import create_app
from app.core.extensions import db

from app.database.seeders.department_seeder import seed_department
from app.database.seeders.position_seeder import seed_position
from app.database.seeders.user_seeder import seed_user
from app.database.seeders.employee_seeder import seed_employee


app = create_app()

with app.app_context():

    print("===== DATABASE SEEDER =====")

    seed_department()
    seed_position()
    seed_user()
    seed_employee()

    db.session.commit()

    print("===== DONE =====")