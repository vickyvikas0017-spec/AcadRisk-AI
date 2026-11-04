from datetime import datetime
from app.database.connection import db_manager
from app.models.entities import Faculty, Department, User, AuditLog

class FacultyService:
    @staticmethod
    def get_all_faculty(department_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(Faculty).join(Department)
            if department_id:
                query = query.filter(Faculty.department_id == department_id)
            return [f.to_dict() for f in query.all()]
        finally:
            session.close()

    @staticmethod
    def get_faculty_by_id(faculty_id):
        session = db_manager.get_session()
        try:
            f = session.query(Faculty).get(faculty_id)
            return f.to_dict() if f else None
        finally:
            session.close()

    @staticmethod
    def create_faculty(user_id, department_id, name, designation, contact=None):
        session = db_manager.get_session()
        try:
            existing = session.query(Faculty).filter_by(user_id=user_id).first()
            if existing:
                return None, "User is already associated with a faculty profile."

            faculty = Faculty(
                user_id=user_id,
                department_id=department_id,
                faculty_name=name.strip(),
                designation=designation.strip(),
                contact_information=contact
            )
            session.add(faculty)
            session.commit()
            return faculty.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_faculty(faculty_id, department_id, name, designation, contact=None):
        session = db_manager.get_session()
        try:
            faculty = session.query(Faculty).get(faculty_id)
            if not faculty:
                return None, "Faculty record not found."
            faculty.department_id = department_id
            faculty.faculty_name = name.strip()
            faculty.designation = designation.strip()
            if contact:
                faculty.contact_information = contact
            session.commit()
            return faculty.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

