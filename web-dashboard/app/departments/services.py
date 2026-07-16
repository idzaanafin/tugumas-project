from sqlalchemy.exc import IntegrityError

from app.core.extensions import db
from app.models.department import Department


def list_departments():
	return db.session.query(Department).order_by(Department.nama.asc()).all()


def get_department(department_id):
	return db.session.get(Department, department_id)


def create_department(nama: str):
	department = Department(nama=nama.strip())
	db.session.add(department)

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("Nama department sudah digunakan.") from exc

	return department


def update_department(department: Department, nama: str):
	department.nama = nama.strip()

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("Nama department sudah digunakan.") from exc

	return department


def delete_department(department: Department):
	db.session.delete(department)
	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("Department masih dipakai pegawai.") from exc
