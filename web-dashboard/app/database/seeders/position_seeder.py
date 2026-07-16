from app.core.extensions import db
from app.models.position import Position


POSITIONS = [    
    "Head Staff",
    "Staff",    
]


def seed_position():
    for name in POSITIONS:

        exists = db.session.query(Position).filter_by(
            nama=name
        ).first()

        if exists:
            continue

        db.session.add(
            Position(
                nama=name
            )
        )

    print("✓ Position seeded")