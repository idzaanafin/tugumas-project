from sqlalchemy.exc import IntegrityError

from app.core.extensions import db
from app.models.position import Position


def list_positions():
	return db.session.query(Position).order_by(Position.nama.asc()).all()


def get_position(position_id):
	return db.session.get(Position, position_id)


def create_position(nama: str):
	position = Position(nama=nama.strip())
	db.session.add(position)

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("Nama posisi sudah ada.") from exc

	return position


def update_position(position: Position, nama: str):
	position.nama = nama.strip()

	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("Nama posisi sudah ada.") from exc

	return position


def delete_position(position: Position):
	db.session.delete(position)
	try:
		db.session.commit()
	except IntegrityError as exc:
		db.session.rollback()
		raise ValueError("posisi masih dipakai pegawai.") from exc
