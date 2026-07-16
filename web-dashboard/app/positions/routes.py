from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import bp
from .services import create_position, delete_position, get_position, list_positions, update_position


@bp.get("/")
@login_required
def index():
    return render_template("positions/index.html", positions=list_positions(), title="Posisi")


@bp.get("/create")
@login_required
def create():
    return render_template("positions/create.html", title="Tambah Posisi")


@bp.post("/store")
@login_required
def store():
    nama = request.form.get("nama", "").strip()

    if not nama:
        flash("Nama position wajib diisi.", "danger")
        return redirect(url_for("positions.create"))

    try:
        create_position(nama)
        flash("Position berhasil ditambahkan.", "success")
        return redirect(url_for("positions.index"))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("positions.create"))


@bp.get("/<uuid:position_id>/edit")
@login_required
def edit(position_id):
    position = get_position(position_id)

    if not position:
        flash("Position tidak ditemukan.", "danger")
        return redirect(url_for("positions.index"))

    return render_template("positions/edit.html", position=position, title="Edit Position")


@bp.post("/<uuid:position_id>/update")
@login_required
def update(position_id):
    position = get_position(position_id)

    if not position:
        flash("Position tidak ditemukan.", "danger")
        return redirect(url_for("positions.index"))

    nama = request.form.get("nama", "").strip()

    if not nama:
        flash("Nama position wajib diisi.", "danger")
        return redirect(url_for("positions.edit", position_id=position.id))

    try:
        update_position(position, nama)
        flash("Position berhasil diperbarui.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("positions.index"))


@bp.post("/<uuid:position_id>/delete")
@login_required
def delete(position_id):
    position = get_position(position_id)

    if not position:
        flash("Position tidak ditemukan.", "danger")
        return redirect(url_for("positions.index"))

    try:
        delete_position(position)
        flash("Position berhasil dihapus.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("positions.index"))