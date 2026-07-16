from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RESIGNED = "RESIGNED"


class EmploymentType(str, Enum):
    PERMANENT = "PERMANENT"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"


class AttendanceStatus(str, Enum):
    HADIR = "H"
    IZIN = "I"
    ALPA = "A"

    @property
    def label(self) -> str:
        labels = {
            AttendanceStatus.HADIR: "Hadir",
            AttendanceStatus.IZIN: "Izin",
            AttendanceStatus.ALPA: "Alpa",
        }
        return labels[self]