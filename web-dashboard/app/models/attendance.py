from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.enums import AttendanceStatus

if TYPE_CHECKING:
    from app.models.employee import Employee


class Attendance(BaseModel):
    __tablename__ = "attendances"

    __table_args__ = (
        UniqueConstraint("employee_id", "tanggal_absensi", name="uq_attendances_employee_date"),
        Index("ix_attendances_tanggal_absensi", "tanggal_absensi"),
    )

    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    tanggal_absensi: Mapped[date] = mapped_column(
        nullable=False,
    )

    jam_masuk: Mapped[time | None] = mapped_column(
        Time(),
        nullable=True,
    )

    # TAMBAHAN: Kolom untuk izin sementara
    jam_izin_keluar: Mapped[time | None] = mapped_column(
        Time(),
        nullable=True,
    )

    jam_izin_masuk: Mapped[time | None] = mapped_column(
        Time(),
        nullable=True,
    )

    jam_keluar: Mapped[time | None] = mapped_column(
        Time(),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(1),
        default=AttendanceStatus.HADIR.value,
        nullable=False,
    )

    keterangan: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    employee: Mapped[Employee] = relationship(
        back_populates="attendances",
        lazy="joined",
    )