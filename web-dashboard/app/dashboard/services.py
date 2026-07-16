from app.core.extensions import db
from app.models.department import Department
from app.models.employee import Employee
from app.models.position import Position
from app.models.user import User


def get_dashboard_summary():
	return {
		"employees": db.session.query(Employee).count(),
		"departments": db.session.query(Department).count(),
		"positions": db.session.query(Position).count(),
		"users": db.session.query(User).count(),
	}
