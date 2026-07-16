from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.employee import Employee


class Position(BaseModel):
    __tablename__ = "positions"

    nama: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    employees: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="position",
        lazy="selectin",
    )