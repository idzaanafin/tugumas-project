from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import bp
from .services import (
    create_employee,
    delete_employee,
    get_employee,
    list_departments,
    list_employees,
    list_positions,
    update_employee,
)
from app.models.enums import EmployeeStatus, EmploymentType


@bp.get("/")
@login_required
def index():
    return render_template("employees/index.html", employees=list_employees(), title="Pegawai")


@bp.get("/create")
@login_required
def create():
    return render_template(
        "employees/create.html",
        employee=None,
        departments=list_departments(),
        positions=list_positions(),
        employment_types=list(EmploymentType),
        employee_statuses=list(EmployeeStatus),
        title="Tambah Pegawai",
    )


@bp.post("/store")
@login_required
def store():
    nip = request.form.get("nip", "").strip()
    nama = request.form.get("nama", "").strip()
    nomor_hp = request.form.get("nomor_hp", "").strip()

    if not nip or not nama or not nomor_hp:
        flash("NIP, nama, dan nomor HP wajib diisi.", "danger")
        return redirect(url_for("employees.create"))

    try:
        create_employee(request.form, request.files.get("foto"))
        flash("Pegawai berhasil ditambahkan.", "success")
        return redirect(url_for("employees.index"))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("employees.create"))


@bp.get("/<uuid:employee_id>/edit")
@login_required
def edit(employee_id):
    employee = get_employee(employee_id)

    if not employee:
        flash("Pegawai tidak ditemukan.", "danger")
        return redirect(url_for("employees.index"))

    return render_template(
        "employees/edit.html",
        employee=employee,
        departments=list_departments(),
        positions=list_positions(),
        employment_types=list(EmploymentType),
        employee_statuses=list(EmployeeStatus),
        title="Edit Pegawai",
    )


@bp.post("/<uuid:employee_id>/update")
@login_required
def update(employee_id):
    employee = get_employee(employee_id)

    if not employee:
        flash("Pegawai tidak ditemukan.", "danger")
        return redirect(url_for("employees.index"))

    try:
        update_employee(employee, request.form, request.files.get("foto"))
        flash("Pegawai berhasil diperbarui.", "success")
        return redirect(url_for("employees.index"))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("employees.edit", employee_id=employee.id))


@bp.post("/<uuid:employee_id>/delete")
@login_required
def delete(employee_id):
    employee = get_employee(employee_id)

    if not employee:
        flash("Pegawai tidak ditemukan.", "danger")
        return redirect(url_for("employees.index"))

    delete_employee(employee)
    flash("Pegawai berhasil dihapus.", "success")
    return redirect(url_for("employees.index"))