from datetime import datetime, date
from app.database.connection import db_manager
from app.models.entities import Student, Department, Enrollment, User, AuditLog

class StudentService:
    @staticmethod
    def get_students(search_query=None, department_id=None, semester=None, course_id=None, limit=50, offset=0):
        session = db_manager.get_session()
        try:
            query = session.query(Student).join(Department)
            if search_query:
                term = f"%{search_query}%"
                query = query.filter(
                    (Student.student_name.ilike(term)) |
                    (Student.registration_number.ilike(term))
                )
            if department_id:
                query = query.filter(Student.department_id == department_id)
            if semester:
                query = query.filter(Student.semester == semester)
            if course_id:
                query = query.join(Enrollment).filter(Enrollment.course_id == course_id)

            total_count = query.count()
            students = query.order_by(Student.registration_number.asc()).offset(offset).limit(limit).all()
            return [s.to_dict() for s in students], total_count
        finally:
            session.close()

    @staticmethod
    def get_student_by_id(student_id):
        session = db_manager.get_session()
        try:
            s = session.query(Student).get(student_id)
            return s.to_dict() if s else None
        finally:
            session.close()

    @staticmethod
    def create_student(reg_no, name, dept_id, semester, admission_year, dob=None, contact=None, user_id=None):
        session = db_manager.get_session()
        try:
            # Check duplicate registration number
            existing = session.query(Student).filter_by(registration_number=reg_no.upper().strip()).first()
            if existing:
                return None, f"A student with registration number '{reg_no}' already exists."

            # Validate semester
            if int(semester) < 1 or int(semester) > 8:
                return None, "Semester must be an integer between 1 and 8."

            parsed_dob = None
            if dob:
                parsed_dob = datetime.strptime(dob, '%Y-%m-%d').date() if isinstance(dob, str) else dob

            student = Student(
                registration_number=reg_no.upper().strip(),
                student_name=name.strip(),
                department_id=dept_id,
                semester=int(semester),
                admission_year=int(admission_year),
                date_of_birth=parsed_dob,
                contact_information=contact,
                user_id=user_id
            )
            session.add(student)
            session.flush()

            # Record audit event
            audit = AuditLog(
                user_id=user_id,
                action_type='INSERT',
                table_name='students',
                record_id=student.student_id,
                old_values=None,
                new_values=f'{{"registration_number": "{student.registration_number}", "name": "{student.student_name}"}}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return student.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_student(student_id, name, dept_id, semester, contact=None, user_id=None):
        session = db_manager.get_session()
        try:
            student = session.query(Student).get(student_id)
            if not student:
                return None, "Student record not found."

            old_val = f'{{"name": "{student.student_name}", "semester": {student.semester}, "dept_id": {student.department_id}}}'
            student.student_name = name.strip()
            student.department_id = dept_id
            student.semester = int(semester)
            if contact:
                student.contact_information = contact

            new_val = f'{{"name": "{student.student_name}", "semester": {student.semester}, "dept_id": {student.department_id}}}'

            audit = AuditLog(
                user_id=user_id,
                action_type='UPDATE',
                table_name='students',
                record_id=student.student_id,
                old_values=old_val,
                new_values=new_val,
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return student.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_student(student_id, user_id=None):
        session = db_manager.get_session()
        try:
            student = session.query(Student).get(student_id)
            if not student:
                return False, "Student not found."

            audit = AuditLog(
                user_id=user_id,
                action_type='DELETE',
                table_name='students',
                record_id=student_id,
                old_values=f'{{"registration_number": "{student.registration_number}", "name": "{student.student_name}"}}',
                new_values=None,
                timestamp=datetime.now()
            )
            session.add(audit)
            session.delete(student)
            session.commit()
            return True, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

