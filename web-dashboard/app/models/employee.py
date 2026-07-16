from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel
from app.models.enums import EmployeeStatus

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.department import Department
    from app.models.position import Position


class Employee(BaseModel):
    __tablename__ = "employees"

    __table_args__ = (
        Index("ix_employee_nama", "nama"),
    )

    # =====================
    # Basic Information
    # =====================

    nip: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    nama: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    nomor_hp: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        unique=True,
        nullable=True,
    )

    # =====================
    # Foreign Keys
    # =====================

    department_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    position_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("positions.id"),
        nullable=True,
    )

    # =====================
    # Relationships
    # =====================

    department: Mapped[Department | None] = relationship(
        "Department",
        back_populates="employees",
        lazy="joined",
    )

    position: Mapped[Position | None] = relationship(
        "Position",
        back_populates="employees",
        lazy="joined",
    )

    attendances: Mapped[list[Attendance]] = relationship(
        "Attendance",
        back_populates="employee",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # =====================
    # Employment Information
    # =====================

    employment_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=EmployeeStatus.ACTIVE.value,
        nullable=False,
    )

    tanggal_masuk: Mapped[date | None] = mapped_column(
        nullable=True,
    )

    foto: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Employee {self.nip} - {self.nama}>"