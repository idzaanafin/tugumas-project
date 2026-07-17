from __future__ import annotations

import calendar
import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.core.extensions import db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.enums import AttendanceStatus
import math

MONTH_NAMES_ID = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]

WEEKDAY_SHORT_ID = ["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]


def list_employees():
    return db.session.query(Employee).all()


def get_employee(employee_id):
    return db.session.get(Employee, employee_id)


def get_attendance(attendance_id):
    return db.session.get(Attendance, attendance_id)


def list_year_options():
    min_date, max_date = db.session.query(
        func.min(Attendance.tanggal_absensi),
        func.max(Attendance.tanggal_absensi),
    ).one()

    current_year = date.today().year
    if not min_date or not max_date:
        return list(range(current_year - 2, current_year + 2))

    start_year = min(min_date.year, current_year - 2)
    end_year = max(max_date.year, current_year + 2)
    return list(range(start_year, end_year + 1))


def list_month_options():
    return [
        {"value": index + 1, "label": month_name}
        for index, month_name in enumerate(MONTH_NAMES_ID)
    ]


def resolve_period(year: int | None = None, month: int | None = None):
    now = date.today()
    selected_year = year or now.year
    selected_month = month or now.month

    if selected_month < 1 or selected_month > 12:
        selected_month = now.month

    return selected_year, selected_month


def _format_time(value: time | None):
    return value.strftime("%H:%M") if value else "-"


def _status_label(status: str | None):
    if not status:
        return "Belum tercatat"

    for member in AttendanceStatus:
        if status == member.value:
            return member.label

    return status


def _parse_uuid(value: str | None, field_label: str):
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field_label} wajib diisi.")

    try:
        uuid.UUID(value)
    except ValueError as exc:
        raise ValueError(f"{field_label} tidak valid.") from exc

    return value


def _parse_date(value: str | None, field_label: str):
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field_label} wajib diisi.")

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_label} tidak valid.") from exc


def _parse_time(value: str | None, field_label: str):
    value = (value or "").strip()
    if not value:
        return None

    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"{field_label} tidak valid.") from exc


def _parse_status(value: str | None):
    value = (value or "").strip()
    if not value:
        raise ValueError("Status absensi wajib diisi.")

    for member in AttendanceStatus:
        if value == member.value or value == member.name:
            return member.value

    allowed = ", ".join(member.value for member in AttendanceStatus)
    raise ValueError(f"Status absensi tidak valid. Pilihan: {allowed}.")


def _parse_note(value: str | None):
    value = (value or "").strip()
    return value or None

def calculate_hours(value):
    value = round(value, 1)  # Round to 1 decimal place
    # if value is None or value < 1.0:
        # return 0.0
    return round(value*2)/2  # Round to nearest 0.5

def work_hours(start_time: time, end_time: time, is_saturday: bool) -> float:
    """Calculate work hours between two time objects."""
    if not start_time or not end_time:
        return 0.0    

    if start_time < time(8, 15):
        start_time = time(8, 00)        
    
    if end_time > time(13, 20) and is_saturday:
        end_time = time(13, 30)
    elif end_time > time(15, 50) and not is_saturday:
        end_time = time(16, 00)
    

    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)

    if is_saturday:
        rest = 0.0
    else:
        rest = 1.0

    if end_dt < start_dt:
        # If end time is before start time, assume it crosses midnight
        end_dt += timedelta(days=1)

    duration = end_dt - start_dt
    duration =  duration.total_seconds() / 3600.0
    
    if end_time > time(12, 0):
        duration -= rest
    
    return duration

def overtime_hours(start_time: time, end_time: time, is_saturday: bool) -> float:
    """Calculate overtime hours based on work hours."""
    if not start_time or not end_time:
        return 0.0

    default_start = time(7,30)
    default_end = time(16,00) if not is_saturday else time(13,30)
    # calculate early overtime (before default start) and late overtime (after default end)
    early_overtime = 0.0
    late_overtime = 0.0
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    ds_dt = datetime.combine(date.today(), default_start)
    de_dt = datetime.combine(date.today(), default_end)

    if start_dt < ds_dt:
        early_overtime = (ds_dt - start_dt).total_seconds() / 3600.0
    
    if end_dt > de_dt:
        late_overtime = (end_dt - de_dt).total_seconds() / 3600.0
    
    return early_overtime + late_overtime


def get_employee_month_detail(employee_id, year: int | None = None, month: int | None = None):
    employee = get_employee(employee_id)
    if not employee:
        raise ValueError("Pegawai tidak ditemukan.")

    selected_year, selected_month = resolve_period(year, month)
    start_date = date(selected_year, selected_month, 1)
    end_day = calendar.monthrange(selected_year, selected_month)[1]
    end_date = date(selected_year, selected_month, end_day)

    records = (
        db.session.query(Attendance)
        .filter(
            Attendance.employee_id == employee.id,
            Attendance.tanggal_absensi.between(start_date, end_date),
        )
        .order_by(Attendance.tanggal_absensi.asc())
        .all()
    )
    record_map = {record.tanggal_absensi.day: record for record in records}

    days = []
    for day in range(1, end_day + 1):
        current_date = date(selected_year, selected_month, day)
        record = record_map.get(day)
        days.append(
            {
                "date": current_date,
                "weekday": WEEKDAY_SHORT_ID[current_date.weekday() + 1 if current_date.weekday() < 6 else 0],
                "record": record,
                "status": record.status if record else None,
                "status_label": _status_label(record.status if record else None),
                "jam_masuk": _format_time(record.jam_masuk) if record else "-",                
                "jam_izin_keluar": _format_time(record.jam_izin_keluar) if record else "-",
                "jam_izin_masuk": _format_time(record.jam_izin_masuk) if record else "-",                
                "jam_keluar": _format_time(record.jam_keluar) if record else "-",
                "lembur": calculate_hours(overtime_hours(record.jam_masuk, record.jam_keluar, current_date.weekday() == 5)) if record and record.jam_masuk and record.jam_keluar else 0.0,
                "jam_kerja": work_hours(record.jam_masuk, record.jam_keluar, current_date.weekday() == 5) if record and record.jam_masuk and record.jam_keluar else 0.0,
                "keterangan": record.keterangan if record and record.keterangan else "-",
            }
        )

    return {
        "employee": employee,
        "days": days,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "month_label": MONTH_NAMES_ID[selected_month - 1],
        "year_options": list_year_options(),
        "month_options": list_month_options(),
    }


def get_attendance_form_context(attendance: Attendance | None = None, year: int | None = None, month: int | None = None):
    selected_year, selected_month = resolve_period(year, month)
    return {
        "attendance": attendance,
        "employees": list_employees(),
        "statuses": list(AttendanceStatus),
        "selected_year": selected_year,
        "selected_month": selected_month,
        "month_label": MONTH_NAMES_ID[selected_month - 1],
        "year_options": list_year_options(),
        "month_options": list_month_options(),
    }


def create_attendance(form):
    employee_id = _parse_uuid(form.get("employee_id"), "Pegawai")
    tanggal_absensi = _parse_date(form.get("tanggal_absensi"), "Tanggal absensi")
    status = _parse_status(form.get("status"))
    jam_masuk = _parse_time(form.get("jam_masuk"), "Jam masuk")
    jam_keluar = _parse_time(form.get("jam_keluar"), "Jam keluar")
    
    #Parse waktu izin
    jam_izin_keluar = _parse_time(form.get("jam_izin_keluar"), "Jam mulai izin")
    jam_izin_masuk = _parse_time(form.get("jam_izin_masuk"), "Jam selesai izin (kembali)")
    
    keterangan = _parse_note(form.get("keterangan"))

    # VALIDASI URUTAN WAKTU
    # 1. Validasi Kehadiran Pasangan Data Izin
    if jam_izin_masuk and not jam_izin_keluar:
        raise ValueError("Jam mulai izin wajib diisi jika jam selesai izin diisi.")
    
    if jam_izin_keluar and not jam_izin_masuk and jam_keluar:
        raise ValueError("Jam selesai izin wajib diisi sebelum mengisi jam pulang (keluar final).")

    # 2. Validasi Urutan Waktu (Yang sudah kita bahas sebelumnya)
    if jam_masuk and jam_keluar and jam_keluar < jam_masuk:
        raise ValueError("Jam keluar (pulang) tidak boleh lebih awal dari jam masuk.")
    if jam_masuk and jam_izin_keluar and jam_izin_keluar < jam_masuk:
        raise ValueError("Jam mulai izin tidak boleh lebih awal dari jam masuk utama.")
    if jam_izin_keluar and jam_izin_masuk and jam_izin_masuk < jam_izin_keluar:
        raise ValueError("Jam kembali izin tidak boleh lebih awal dari jam mulai izin.")
    if jam_izin_masuk and jam_keluar and jam_keluar < jam_izin_masuk:
        raise ValueError("Jam pulang tidak boleh lebih awal dari jam kembali izin.")

    if not get_employee(employee_id):
        raise ValueError("Pegawai tidak ditemukan.")

    attendance = Attendance(
        employee_id=employee_id,
        tanggal_absensi=tanggal_absensi,
        jam_masuk=jam_masuk,
        jam_izin_keluar=jam_izin_keluar,  
        jam_izin_masuk=jam_izin_masuk,    
        jam_keluar=jam_keluar,
        status=status,
        keterangan=keterangan,
    )

    db.session.add(attendance)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ValueError("Absensi untuk pegawai dan tanggal tersebut sudah ada.") from exc

    return attendance


def update_attendance(attendance: Attendance, form):
    employee_id = _parse_uuid(form.get("employee_id"), "Pegawai")
    tanggal_absensi = _parse_date(form.get("tanggal_absensi"), "Tanggal absensi")
    status = _parse_status(form.get("status"))
    jam_masuk = _parse_time(form.get("jam_masuk"), "Jam masuk")
    jam_keluar = _parse_time(form.get("jam_keluar"), "Jam keluar")
    
    #Parse waktu izin
    jam_izin_keluar = _parse_time(form.get("jam_izin_keluar"), "Jam mulai izin")
    jam_izin_masuk = _parse_time(form.get("jam_izin_masuk"), "Jam selesai izin (kembali)")
    
    keterangan = _parse_note(form.get("keterangan"))

    # VALIDASI URUTAN WAKTU
    # 1. Validasi Kehadiran Pasangan Data Izin
    if jam_izin_masuk and not jam_izin_keluar:
        raise ValueError("Jam mulai izin wajib diisi jika jam selesai izin diisi.")
    
    if jam_izin_keluar and not jam_izin_masuk and jam_keluar:
        raise ValueError("Jam selesai izin wajib diisi sebelum mengisi jam pulang (keluar final).")

    # 2. Validasi Urutan Waktu (Yang sudah kita bahas sebelumnya)
    if jam_masuk and jam_keluar and jam_keluar < jam_masuk:
        raise ValueError("Jam keluar (pulang) tidak boleh lebih awal dari jam masuk.")
    if jam_masuk and jam_izin_keluar and jam_izin_keluar < jam_masuk:
        raise ValueError("Jam mulai izin tidak boleh lebih awal dari jam masuk utama.")
    if jam_izin_keluar and jam_izin_masuk and jam_izin_masuk < jam_izin_keluar:
        raise ValueError("Jam kembali izin tidak boleh lebih awal dari jam mulai izin.")
    if jam_izin_masuk and jam_keluar and jam_keluar < jam_izin_masuk:
        raise ValueError("Jam pulang tidak boleh lebih awal dari jam kembali izin.")

    if not get_employee(employee_id):
        raise ValueError("Pegawai tidak ditemukan.")

    attendance.employee_id = employee_id
    attendance.tanggal_absensi = tanggal_absensi
    attendance.jam_masuk = jam_masuk
    attendance.jam_izin_keluar = jam_izin_keluar  
    attendance.jam_izin_masuk = jam_izin_masuk    
    attendance.jam_keluar = jam_keluar
    attendance.status = status
    attendance.keterangan = keterangan

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ValueError("Absensi untuk pegawai dan tanggal tersebut sudah ada.") from exc

    return attendance


def delete_attendance(attendance: Attendance):
    db.session.delete(attendance)
    db.session.commit()


def process_scan_attendance(employee_id: str, scan_datetime: datetime):
    BATAS_MASUK = datetime.strptime("08:15", "%H:%M").time()
    BATAS_LEMBUR_PAGI = datetime.strptime("07:25", "%H:%M").time()
    BATAS_LEMBUR_SORE = datetime.strptime("16:25", "%H:%M").time()
    BATAS_PULANG = datetime.strptime("15:50", "%H:%M").time()
    
    employee = get_employee(employee_id)    
    if not employee:
        raise ValueError("Pegawai tidak ditemukan.")

    scan_date = scan_datetime.date()
    scan_time = scan_datetime.time()

    attendance = db.session.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.tanggal_absensi == scan_date
    ).first()

    # SKENARIO 1: Belum ada data hari ini -> Catat Jam Masuk
    if not attendance:
        keterangan = "hadir tepat waktu"
        if scan_time > BATAS_MASUK:
            keterangan = "terlambat"
        elif scan_time < BATAS_LEMBUR_PAGI:
            keterangan = "lembur pagi"

        new_attendance = Attendance(
            employee_id=employee.id,
            tanggal_absensi=scan_date,
            jam_masuk=scan_time,
            jam_keluar=None,
            jam_izin_keluar=None,
            jam_izin_masuk=None,
            status=AttendanceStatus.HADIR.value,
            keterangan=keterangan
        )
        db.session.add(new_attendance)
        db.session.commit()
        
        return {
            "action": "masuk",
            "message": f"Berhasil presensi MASUK. Keterangan: {keterangan}",
            "time": _format_time(scan_time)
        }

    # VALIDASI BLOKIR (4x Scan)
    if attendance.jam_masuk and attendance.jam_keluar and attendance.jam_izin_keluar and attendance.jam_izin_masuk:
        raise ValueError("Presensi hari ini sudah lengkap.")

    # SKENARIO 2: Scan ke-2 (Sementara dicatat sebagai PULANG)
    if attendance.jam_masuk and not attendance.jam_keluar and not attendance.jam_izin_keluar:
        waktu_terakhir = datetime.combine(scan_date, attendance.jam_masuk)
        if (scan_datetime - waktu_terakhir).total_seconds() < 3600:
            raise ValueError(f"Anda sudah presensi masuk pada {_format_time(attendance.jam_masuk)}. Tunggu minimal 1 jam.")
        
        attendance.jam_keluar = scan_time
        
        # Logika keterangan lembur sore
        if scan_time < BATAS_PULANG:
            if attendance.keterangan:
                if "pulang lebih awal" not in attendance.keterangan:
                    attendance.keterangan += ", pulang lebih awal"
            else:
                attendance.keterangan = "pulang lebih awal"

        elif scan_time > BATAS_LEMBUR_SORE:
            if attendance.keterangan:
                if "lembur sore" not in attendance.keterangan:
                    attendance.keterangan += ", lembur sore"
            else:
                attendance.keterangan = "lembur sore"

        else:
            if attendance.keterangan:
                if "pulang tepat waktu" not in attendance.keterangan:
                    attendance.keterangan += ", pulang tepat waktu"
            else:
                attendance.keterangan = "pulang tepat waktu"

        db.session.commit()
        return {
            "action": "keluar",
            "message": "Berhasil presensi KELUAR.",
            "time": _format_time(scan_time)
        }

    # SKENARIO 3: Scan ke-3 (Mengubah data Pulang menjadi Izin, lalu catat KEMBALI IZIN)
    if attendance.jam_masuk and attendance.jam_keluar and not attendance.jam_izin_keluar:
        waktu_terakhir = datetime.combine(scan_date, attendance.jam_keluar)
        if (scan_datetime - waktu_terakhir).total_seconds() < 3600:
            raise ValueError(f"Anda sudah presensi keluar pada {_format_time(attendance.jam_keluar)}. Tunggu minimal 1 jam.")
        
        # Pindahkan data jam_keluar (Scan 2) ke jam_izin_keluar
        attendance.jam_izin_keluar = attendance.jam_keluar
        attendance.jam_izin_masuk = scan_time
        
        # Kosongkan kembali jam_keluar untuk persiapan Scan ke-4
        attendance.jam_keluar = None 
        
        # Bersihkan keterangan 'pulang lebih awal' karena ternyata pegawai belum pulang
        if attendance.keterangan and "pulang lebih awal" in attendance.keterangan:
            ket_list = [k.strip() for k in attendance.keterangan.split(",") if "pulang lebih awal" not in k.strip()]
            attendance.keterangan = ", ".join(ket_list) if ket_list else None
            
        db.session.commit()
        return {
            "action": "izin_masuk",
            "message": "Berhasil presensi KEMBALI DARI IZIN.",
            "time": _format_time(scan_time)
        }

    # SKENARIO 4: Scan ke-4 (Pulang FINAL setelah izin)
    if attendance.jam_masuk and not attendance.jam_keluar and attendance.jam_izin_masuk:
        waktu_terakhir = datetime.combine(scan_date, attendance.jam_izin_masuk)
        if (scan_datetime - waktu_terakhir).total_seconds() < 3600:
            raise ValueError(f"Anda sudah presensi kembali izin pada {_format_time(attendance.jam_izin_masuk)}. Tunggu minimal 1 jam.")
        
        attendance.jam_keluar = scan_time
        
        if scan_time > BATAS_LEMBUR_SORE:
            if attendance.keterangan:
                if "lembur sore (setelah izin)" not in attendance.keterangan:
                    attendance.keterangan += ", lembur sore (setelah izin)"
            else:
                attendance.keterangan = "lembur sore (setelah izin)"
        else:
            if attendance.keterangan:
                if "pulang tepat waktu (setelah izin)" not in attendance.keterangan:
                    attendance.keterangan += ", pulang tepat waktu (setelah izin)"
            else:
                attendance.keterangan = "pulang tepat waktu (setelah izin)"

        db.session.commit()
        return {
            "action": "keluar_final",
            "message": "Berhasil presensi KELUAR (Final).",
            "time": _format_time(scan_time)
        }


def get_today_attendance_preview():
    today = date.today()
    
    employees = db.session.query(Employee).all()
    
    records = db.session.query(Attendance).filter(
        Attendance.tanggal_absensi == today
    ).all()
    
    attendance_map = {record.employee_id: record for record in records}
    
    result = []
    
    for emp in employees:
        record = attendance_map.get(emp.id)
        
        if record:
            result.append({
                "id_absensi": str(record.id),
                "nama": emp.nama,
                "jam_masuk": _format_time(record.jam_masuk),
                "jam_izin_keluar": _format_time(record.jam_izin_keluar),  
                "jam_izin_masuk": _format_time(record.jam_izin_masuk),    
                "jam_keluar": _format_time(record.jam_keluar),
                "keterangan": record.keterangan or "-",
                "status": record.status
            })
        else:
            result.append({
                "id_absensi": None,
                "nama": emp.nama,
                "jam_masuk": "--:--",
                "jam_izin_keluar": "--:--", 
                "jam_izin_masuk": "--:--",  
                "jam_keluar": "--:--",
                "keterangan": "Belum absen",
                "status": "-"
            })
            
    return result
