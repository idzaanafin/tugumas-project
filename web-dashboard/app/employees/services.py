from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.core.extensions import db
from app.models.department import Department
from app.models.employee import Employee
from app.models.enums import EmployeeStatus, EmploymentType
from app.models.position import Position


UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads" / "employees"


def list_employees():
	return (
		db.session.query(Employee)
		.options(selectinload(Employee.department), selectinload(Employee.position))
		.order_by(Employee.nip.asc())
		.all()
	)


def get_employee(employee_id):
	return db.session.get(Employee, employee_id)


def _parse_optional_uuid(value: str | None, field_label: str):
	value = (value or "").strip()
	if not value:
		return None

	try:
		uuid.UUID(value)
	except ValueError as exc:
		raise ValueError(f"{field_label} tidak valid.") from exc

	return value


def _parse_optional_date(value: str | None, field_label: str):
	value = (value or "").strip()
	if not value:
		return None

	try:
		return datetime.strptime(value, "%Y-%m-%d").date()
	except ValueError as exc:
		raise ValueError(f"{field_label} tidak valid.") from exc


def _parse_optional_enum(enum_class, value: str | None, field_label: str):
	value = (value or "").strip()
	if not value:
		return None

	try:
		return enum_class[value]
	except KeyError:
		try:
			return enum_class(value)
		except ValueError as exc:
			allowed_values = ", ".join(member.value for member in enum_class)
			raise ValueError(f"{field_label} tidak valid. Pilihan: {allowed_values}.") from exc


def _enum_value(enum_member):
	if enum_member is None:
		return None

	return enum_member.value


def _integrity_message(exc: IntegrityError):
	orig = getattr(exc, "orig", None)
	diag = getattr(orig, "diag", None)
	constraint_name = getattr(diag, "constraint_name", "") or ""
	error_text = str(exc).lower()

	if "email" in constraint_name or "email" in error_text:
		return "Email pegawai sudah digunakan."

	if "nip" in constraint_name or "nip" in error_text:
		return "NIP pegawai sudah digunakan."

	return "Data pegawai tidak valid atau melanggar aturan unik."


def _save_photo(upload: FileStorage | None):
	if not upload or not upload.filename:
		return None

	UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

	filename = secure_filename(upload.filename)
	unique_name = f"{uuid.uuid4().hex}_{filename}"
	destination = UPLOAD_DIR / unique_name
	upload.save(destination)

	return f"uploads/employees/{unique_name}"


def _delete_photo(photo_path: str | None):
	if not photo_path:
		return

	file_name = Path(photo_path).name
	file_path = UPLOAD_DIR / file_name

	if file_path.exists():
		file_path.unlink()


def create_employee(form, photo_file: FileStorage | None):
	employee = Employee(
		nip=form.get("nip", "").strip(),
		nama=form.get("nama", "").strip(),
		nomor_hp=form.get("nomor_hp", "").strip(),
		email=(form.get("email", "").strip() or None),
		department_id=_parse_optional_uuid(form.get("department_id"), "Department"),
		position_id=_parse_optional_uuid(form.get("position_id"), "Position"),
		employment_type=_enum_value(_parse_optional_enum(EmploymentType, form.get("employment_type"), "Employment type")),
		status=_enum_value(_parse_optional_enum(EmployeeStatus, form.get("status"), "Status")) or EmployeeStatus.ACTIVE.value,
		tanggal_masuk=_parse_optional_date(form.get("tanggal_masuk"), "Tanggal masuk"),
		foto=_save_photo(photo_file),
	)

	db.session.add(employee)

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		_delete_photo(employee.foto)
		raise ValueError(_integrity_message(exc)) from exc

	return employee


def update_employee(employee: Employee, form, photo_file: FileStorage | None):
	new_photo = _save_photo(photo_file)
	old_photo = employee.foto

	employee.nip = form.get("nip", "").strip()
	employee.nama = form.get("nama", "").strip()
	employee.nomor_hp = form.get("nomor_hp", "").strip()
	employee.email = form.get("email", "").strip() or None
	employee.department_id = _parse_optional_uuid(form.get("department_id"), "Department")
	employee.position_id = _parse_optional_uuid(form.get("position_id"), "Position")
	employee.employment_type = _enum_value(_parse_optional_enum(EmploymentType, form.get("employment_type"), "Employment type"))
	employee.status = _enum_value(_parse_optional_enum(EmployeeStatus, form.get("status"), "Status")) or EmployeeStatus.ACTIVE.value
	employee.tanggal_masuk = _parse_optional_date(form.get("tanggal_masuk"), "Tanggal masuk")

	if new_photo:
		employee.foto = new_photo

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		if new_photo:
			_delete_photo(new_photo)
		raise ValueError(_integrity_message(exc)) from exc

	if new_photo:
		_delete_photo(old_photo)

	return employee


def delete_employee(employee: Employee):
	photo_path = employee.foto
	db.session.delete(employee)
	db.session.commit()
	_delete_photo(photo_path)


def list_departments():
	return db.session.query(Department).order_by(Department.nama.asc()).all()


def list_positions():
	return db.session.query(Position).order_by(Position.nama.asc()).all()
