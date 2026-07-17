from datetime import date, datetime

from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required

from . import bp
from .services import (
    create_attendance,
    delete_attendance,
    get_attendance,
    get_attendance_form_context,
    get_employee_month_detail,
    get_today_attendance_preview,
    list_employees,
    list_month_options,
    process_scan_attendance,
    resolve_period,
    update_attendance,
)


@bp.get("/")
@login_required
def index():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    current_year = date.today().year
    current_month = date.today().month

    # ================= STATE 3: KARTU DETAIL PEGAWAI (PAGINATION) =================
    if year and month:
        employees = list_employees()
        
        if not employees:
            context = {"view": "table", "empty": True, "selected_year": year, "selected_month": month}
            return render_template("attendance/index.html", title="Data Kosong", **context)
            
        emp_idx = request.args.get("emp_idx", type=int, default=0)
        emp_idx = max(0, min(emp_idx, len(employees) - 1))
        current_emp = employees[emp_idx]
        
        detail_context = get_employee_month_detail(current_emp.id, year, month)
                        
        count_hadir = sum(1 for d in detail_context['days'] if d['status'] == 'H' and d['jam_kerja'] >= 7 and not d['date'].weekday() == 5) + \
                      sum(0.5 for d in detail_context['days'] if d['status'] == 'H' and d['jam_kerja'] < 7 and not d['date'].weekday() == 5) + \
                      sum(1 for d in detail_context['days'] if d['status'] == 'H' and d['jam_kerja'] >= 5 and d['date'].weekday() == 5) + \
                      sum(0.5 for d in detail_context['days'] if d['status'] == 'H' and d['jam_kerja'] < 5 and d['date'].weekday() == 5)

        count_izin = sum(1 for d in detail_context['days'] if d['status'] == 'I')
        count_alpa = sum(1 for d in detail_context['days'] if d['status'] == 'A')
        
        context = {
            "view": "table",
            "selected_year": year,
            "selected_month": month,
            "month_label": detail_context["month_label"],
            "employee": current_emp,
            "employees_list": [{"idx": i, "id": e.id, "nama": e.nama} for i, e in enumerate(employees)],
            "days": detail_context["days"],
            "summary": {"hadir": count_hadir, "izin": count_izin, "alpa": count_alpa},
            "emp_idx": emp_idx,
            "total_emp": len(employees),
            "prev_idx": emp_idx - 1 if emp_idx > 0 else None,
            "next_idx": emp_idx + 1 if emp_idx < len(employees) - 1 else None,
        }
        return render_template("attendance/index.html", title="Absensi", **context)
    
    # ================= STATE 2: PILIH BULAN =================
    if year:
        context = {
            "view": "month",
            "selected_year": year,
            "month_options": list_month_options(),
            "current_year": current_year,
            "current_month": current_month,
        }
        return render_template("attendance/index.html", title=f"Pilih Bulan - {year}", **context)

    # ================= STATE 1: PILIH TAHUN =================
    start_year = request.args.get("start_year", type=int, default=current_year - 3)
    year_options = [start_year + i for i in range(4)]
    
    context = {
        "view": "year",
        "year_options": year_options,
        "start_year": start_year,
        "prev_start": start_year - 4,
        "next_start": start_year + 4,
        "current_year": current_year,
    }
    return render_template("attendance/index.html", title="Pilih Tahun", **context)


@bp.get("/create")
@login_required
def create():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    day = request.args.get("day", type=int)
    selected_employee_id = request.args.get("employee_id")
    selected_date = None
    if year and month and day:
        selected_date = f"{year:04d}-{month:02d}-{day:02d}"

    context = get_attendance_form_context(year=year, month=month)
    context.update(
        {
            "mode": "create",
            "selected_employee_id": selected_employee_id,
            "selected_date": selected_date,
            "form_action": url_for("attendance.store"),
            "cancel_url": url_for("attendance.index", year=context["selected_year"], month=context["selected_month"]),
        }
    )
    return render_template("attendance/form.html", title="Tambah Absensi", **context)


@bp.get("/<uuid:attendance_id>/edit")
@login_required
def edit(attendance_id):
    attendance = get_attendance(attendance_id)
    if not attendance:
        flash("Absensi tidak ditemukan.", "danger")
        return redirect(url_for("attendance.index"))

    context = get_attendance_form_context(attendance, attendance.tanggal_absensi.year, attendance.tanggal_absensi.month)
    context.update(
        {
            "mode": "edit",
            "selected_employee_id": str(attendance.employee_id),
            "selected_date": attendance.tanggal_absensi.isoformat(),
            "form_action": url_for("attendance.update", attendance_id=attendance.id),
            "cancel_url": url_for(
                "attendance.index",
                year=attendance.tanggal_absensi.year,
                month=attendance.tanggal_absensi.month,
            ),
        }
    )
    return render_template("attendance/form.html", title="Edit Absensi", **context)


@bp.post("/store")
@login_required
def store():
    try:
        attendance = create_attendance(request.form)
        flash("Absensi berhasil ditambahkan.", "success")
        return redirect(url_for("attendance.index", year=attendance.tanggal_absensi.year, month=attendance.tanggal_absensi.month))
    except ValueError as exc:
        flash(str(exc), "danger")
        year, month = resolve_period(request.form.get("return_year", type=int), request.form.get("return_month", type=int))
        return redirect(url_for("attendance.create", year=year, month=month))


@bp.post("/<uuid:attendance_id>/update")
@login_required
def update(attendance_id):
    attendance = get_attendance(attendance_id)
    if not attendance:
        flash("Absensi tidak ditemukan.", "danger")
        return redirect(url_for("attendance.index"))

    try:
        attendance = update_attendance(attendance, request.form)
        flash("Absensi berhasil diperbarui.", "success")
        return redirect(url_for("attendance.index", year=attendance.tanggal_absensi.year, month=attendance.tanggal_absensi.month))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("attendance.edit", attendance_id=attendance.id))


@bp.post("/<uuid:attendance_id>/delete")
@login_required
def delete(attendance_id):
    attendance = get_attendance(attendance_id)
    if not attendance:
        flash("Absensi tidak ditemukan.", "danger")
        return redirect(url_for("attendance.index"))

    year = attendance.tanggal_absensi.year
    month = attendance.tanggal_absensi.month
    delete_attendance(attendance)
    flash("Absensi berhasil dihapus.", "success")
    return redirect(url_for("attendance.index", year=year, month=month))


@bp.post("/scanner/scan")
def api_scan():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "Body request harus berupa JSON"}), 400

    employee_id = data.get("employee_id")
    scan_timestamp = data.get("timestamp")

    if not employee_id or not scan_timestamp:
        return jsonify({"status": "error", "message": "employee_id dan timestamp wajib dikirim"}), 400

    try:
        scan_datetime = datetime.fromisoformat(scan_timestamp[:19])
        result = process_scan_attendance(employee_id, scan_datetime)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except ValueError as exc:
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": f"Terjadi kesalahan internal: {str(exc)}"
        }), 500


@bp.get("/scanner/today")
def api_scan_today():
    try:
        data = get_today_attendance_preview()
        
        total_hadir = sum(1 for item in data if item["status"] != "-")
        
        return jsonify({
            "status": "success",
            "tanggal": date.today().isoformat(),
            "total_hadir": total_hadir,
            "data": data
        }), 200
    except Exception as exc:
        return jsonify({
            "status": "error",
            "message": f"Gagal memuat data: {str(exc)}"
        }), 500