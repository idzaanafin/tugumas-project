from app.core.extensions import db
from app.models.department import Department


DEPARTMENTS = [
    "Production",    
    "Finance",
    "Accounting",
    "Logistics",
]


def seed_department():
    for name in DEPARTMENTS:

        exists = db.session.query(Department).filter_by(
            nama=name
        ).first()

        if exists:
            continue

        db.session.add(
            Department(
                nama=name
            )
        )

    print("✓ Department seeded")