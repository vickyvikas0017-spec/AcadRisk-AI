from datetime import datetime, date
from decimal import Decimal
from app.database.connection import db_manager
from app.models.entities import Assessment, Mark, Enrollment, Student, Course, AuditLog

class MarksService:
    @staticmethod
    def calculate_letter_grade(percentage):
        """Standard 10-point academic grading scale."""
        if percentage >= 90.0:
            return 'A+', 10.0
        elif percentage >= 80.0:
            return 'A', 9.0
        elif percentage >= 70.0:
            return 'B', 8.0
        elif percentage >= 60.0:
            return 'C', 7.0
        elif percentage >= 50.0:
            return 'D', 6.0
        elif percentage >= 40.0:
            return 'E', 5.0
        else:
            return 'F', 0.0

    @staticmethod
    def get_assessments(course_id=None, semester_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(Assessment)
            if course_id:
                query = query.filter_by(course_id=course_id)
            if semester_id:
                query = query.filter_by(semester_id=semester_id)
            return [a.to_dict() for a in query.order_by(Assessment.assessment_date.desc()).all()]
        finally:
            session.close()

    @staticmethod
    def create_assessment(course_id, semester_id, name, assessment_type, max_marks, date_str):
        session = db_manager.get_session()
        try:
            max_m = Decimal(str(max_marks))
            if max_m <= Decimal('0'):
                return None, "Maximum marks must be strictly greater than zero."

            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date() if isinstance(date_str, str) else date_str
            assessment = Assessment(
                course_id=course_id,
                semester_id=semester_id,
                assessment_name=name.strip(),
                assessment_type=assessment_type,
                maximum_marks=max_m,
                assessment_date=parsed_date
            )
            session.add(assessment)
            session.commit()
            return assessment.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def record_mark(assessment_id, enrollment_id, obtained_marks, recorded_by=None):
        session = db_manager.get_session()
        try:
            assessment = session.query(Assessment).get(assessment_id)
            if not assessment:
                return None, "Assessment not found."

            obt = Decimal(str(obtained_marks))
            # Validate constraints
            if obt < Decimal('0'):
                return None, "Obtained marks cannot fall below zero."
            if obt > assessment.maximum_marks:
                return None, f"Obtained marks ({obt}) cannot exceed maximum assessment marks ({assessment.maximum_marks})."

            existing = session.query(Mark).filter_by(
                assessment_id=assessment_id,
                enrollment_id=enrollment_id
            ).first()

            if existing:
                old_val = f'{{"obtained_marks": {float(existing.obtained_marks)}}}'
                existing.obtained_marks = obt
                existing.recorded_by = recorded_by
                existing.recorded_at = datetime.now()
                new_val = f'{{"obtained_marks": {float(obt)}}}'
                action = 'UPDATE'
                mark_obj = existing
            else:
                mark_obj = Mark(
                    assessment_id=assessment_id,
                    enrollment_id=enrollment_id,
                    obtained_marks=obt,
                    recorded_by=recorded_by,
                    recorded_at=datetime.now()
                )
                session.add(mark_obj)
                session.flush()
                old_val = None
                new_val = f'{{"obtained_marks": {float(obt)}, "assessment_id": {assessment_id}}}'
                action = 'INSERT'

            audit = AuditLog(
                user_id=recorded_by,
                action_type=action,
                table_name='marks',
                record_id=mark_obj.mark_id,
                old_values=old_val,
                new_values=new_val,
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return mark_obj.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_course_marks(assessment_id):
        session = db_manager.get_session()
        try:
            marks = session.query(Mark).filter_by(assessment_id=assessment_id).all()
            return [m.to_dict() for m in marks]
        finally:
            session.close()

