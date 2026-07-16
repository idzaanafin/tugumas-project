from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import bp
from .services import create_department, delete_department, get_department, list_departments, update_department


@bp.get("/")
@login_required
def index():
    return render_template("departments/index.html", departments=list_departments(), title="Departemen")


@bp.get("/create")
@login_required
def create():
    return render_template("departments/create.html", title="Tambah Departemen")


@bp.post("/store")
@login_required
def store():
    nama = request.form.get("nama", "").strip()

    if not nama:
        flash("Nama departemen wajib diisi.", "danger")
        return redirect(url_for("departments.create"))

    try:
        create_department(nama)
        flash("Departemen berhasil ditambahkan.", "success")
        return redirect(url_for("departments.index"))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("departments.create"))


@bp.get("/<uuid:department_id>/edit")
@login_required
def edit(department_id):
    department = get_department(department_id)

    if not department:
        flash("Departemen tidak ditemukan.", "danger")
        return redirect(url_for("departments.index"))

    return render_template("departments/edit.html", department=department, title="Edit Departemen")


@bp.post("/<uuid:department_id>/update")
@login_required
def update(department_id):
    department = get_department(department_id)

    if not department:
        flash("Departemen tidak ditemukan.", "danger")
        return redirect(url_for("departments.index"))

    nama = request.form.get("nama", "").strip()

    if not nama:
        flash("Nama departemen wajib diisi.", "danger")
        return redirect(url_for("departments.edit", department_id=department.id))

    try:
        update_department(department, nama)
        flash("Departemen berhasil diperbarui.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("departments.index"))


@bp.post("/<uuid:department_id>/delete")
@login_required
def delete(department_id):
    department = get_department(department_id)

    if not department:
        flash("Departemen tidak ditemukan.", "danger")
        return redirect(url_for("departments.index"))

    try:
        delete_department(department)
        flash("Departemen berhasil dihapus.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("departments.index"))