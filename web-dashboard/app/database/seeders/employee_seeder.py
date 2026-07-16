from app.core.extensions import db
from app.models.employee import Employee


EMPLOYEES = [
    {
        "nip": "TMO-001",
        "nama": "Birin",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-002",
        "nama": "Ning",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-003",
        "nama": "Isti",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-004",
        "nama": "Edi",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-005",
        "nama": "Nanang",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-006",
        "nama": "Asep",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-007",
        "nama": "Tri",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-008",
        "nama": "Rismi",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-009",
        "nama": "Bu Tri",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-010",
        "nama": "Bu Siswi",
        "nomor_hp": "-",
    },
    {
        "nip": "TMO-011",
        "nama": "Supri",
        "nomor_hp": "-",
    },
]


def seed_employee():
    for item in EMPLOYEES:

        exists = db.session.query(Employee).filter_by(
            nip=item["nip"]
        ).first()

        if exists:
            continue

        db.session.add(
            Employee(
                nip=item["nip"],
                nama=item["nama"],
                nomor_hp=item["nomor_hp"],
            )
        )

    print("✓ Employee seeded")