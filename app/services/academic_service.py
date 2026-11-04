from datetime import datetime, date
from decimal import Decimal
from app.database.connection import db_manager
from app.models.entities import Department, Course, Semester, Enrollment, AcademicCalendar, AcademicHistory, Student, AuditLog

class AcademicService:
    # --- DEPARTMENTS ---
    @staticmethod
    def get_all_departments():
        session = db_manager.get_session()
        try:
            depts = session.query(Department).all()
            return [d.to_dict() for d in depts]
        finally:
            session.close()

    @staticmethod
    def create_department(name, code, description):
        session = db_manager.get_session()
        try:
            existing = session.query(Department).filter(
                (Department.department_code == code.upper()) | (Department.department_name == name)
            ).first()
            if existing:
                return None, "Department name or code already exists."
            dept = Department(department_name=name, department_code=code.upper(), description=description)
            session.add(dept)
            session.commit()
            return dept.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    # --- COURSES ---
    @staticmethod
    def get_all_courses(department_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(Course)
            if department_id:
                query = query.filter_by(department_id=department_id)
            return [c.to_dict() for c in query.all()]
        finally:
            session.close()

    @staticmethod
    def create_course(dept_id, code, name, credits, description):
        session = db_manager.get_session()
        try:
            if int(credits) <= 0:
                return None, "Course credits must be greater than zero."
            existing = session.query(Course).filter_by(course_code=code.upper()).first()
            if existing:
                return None, f"Course code '{code}' already exists."
            course = Course(
                department_id=dept_id,
                course_code=code.upper(),
                course_name=name,
                credits=int(credits),
                description=description
            )
            session.add(course)
            session.commit()
            return course.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    # --- SEMESTERS ---
    @staticmethod
    def get_all_semesters():
        session = db_manager.get_session()
        try:
            return [s.to_dict() for s in session.query(Semester).order_by(Semester.start_date.desc()).all()]
        finally:
            session.close()

    @staticmethod
    def create_semester(name, academic_year, start_date, end_date, status='active'):
        session = db_manager.get_session()
        try:
            sem = Semester(
                semester_name=name,
                academic_year=academic_year,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date,
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date,
                status=status
            )
            session.add(sem)
            session.commit()
            return sem.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    # --- ENROLLMENTS ---
    @staticmethod
    def get_enrollments(student_id=None, course_id=None, semester_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(Enrollment)
            if student_id:
                query = query.filter_by(student_id=student_id)
            if course_id:
                query = query.filter_by(course_id=course_id)
            if semester_id:
                query = query.filter_by(semester_id=semester_id)
            return [e.to_dict() for e in query.all()]
        finally:
            session.close()

    @staticmethod
    def enroll_student(student_id, course_id, semester_id):
        session = db_manager.get_session()
        try:
            # Check unique constraint to prevent duplicate enrollments
            existing = session.query(Enrollment).filter_by(
                student_id=student_id,
                course_id=course_id,
                semester_id=semester_id
            ).first()
            if existing:
                return None, "Student is already enrolled in this course for the selected semester."

            enr = Enrollment(
                student_id=student_id,
                course_id=course_id,
                semester_id=semester_id,
                enrollment_date=date.today(),
                enrollment_status='enrolled'
            )
            session.add(enr)
            session.commit()
            return enr.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    # --- CALENDAR ---
    @staticmethod
    def get_calendar_events(semester_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(AcademicCalendar)
            if semester_id:
                query = query.filter_by(semester_id=semester_id)
            return [e.to_dict() for e in query.order_by(AcademicCalendar.event_date.asc()).all()]
        finally:
            session.close()

    # --- ACADEMIC HISTORY ---
    @staticmethod
    def get_academic_history(student_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(AcademicHistory)
            if student_id:
                query = query.filter_by(student_id=student_id)
            return [h.to_dict() for h in query.all()]
        finally:
            session.close()

