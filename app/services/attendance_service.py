from datetime import datetime, date
from decimal import Decimal
from app.database.connection import db_manager
from app.models.entities import AttendanceSession, AttendanceRecord, Enrollment, Student, Course, AuditLog

class AttendanceService:
    @staticmethod
    def get_sessions(course_id=None, semester_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(AttendanceSession)
            if course_id:
                query = query.filter_by(course_id=course_id)
            if semester_id:
                query = query.filter_by(semester_id=semester_id)
            return [s.to_dict() for s in query.order_by(AttendanceSession.session_date.desc()).all()]
        finally:
            session.close()

    @staticmethod
    def create_session_and_record(course_id, semester_id, faculty_id, session_date, session_type, records_data, user_id=None):
        """
        Creates an attendance session and records student statuses in an atomic transaction.
        records_data: list of dicts [{'enrollment_id': int, 'status': 'Present'|'Absent'|'Late'|'Excused'}]
        """
        session = db_manager.get_session()
        try:
            parsed_date = datetime.strptime(session_date, '%Y-%m-%d').date() if isinstance(session_date, str) else session_date
            
            att_session = AttendanceSession(
                course_id=course_id,
                semester_id=semester_id,
                faculty_id=faculty_id,
                session_date=parsed_date,
                session_type=session_type
            )
            session.add(att_session)
            session.flush()

            inserted_records = 0
            for item in records_data:
                enrollment_id = item['enrollment_id']
                status = item['status']
                if status not in ('Present', 'Absent', 'Late', 'Excused'):
                    raise ValueError(f"Invalid attendance status: {status}")

                # Check duplicate
                existing = session.query(AttendanceRecord).filter_by(
                    session_id=att_session.session_id,
                    enrollment_id=enrollment_id
                ).first()
                if not existing:
                    rec = AttendanceRecord(
                        session_id=att_session.session_id,
                        enrollment_id=enrollment_id,
                        attendance_status=status,
                        recorded_at=datetime.now()
                    )
                    session.add(rec)
                    inserted_records += 1

            # Log audit event
            audit = AuditLog(
                user_id=user_id,
                action_type='INSERT',
                table_name='attendance_sessions',
                record_id=att_session.session_id,
                old_values=None,
                new_values=f'{{"course_id": {course_id}, "date": "{session_date}", "records": {inserted_records}}}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return att_session.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_attendance_status(attendance_id, new_status, user_id=None):
        """
        Authorized correction of attendance record with audit tracking.
        """
        if new_status not in ('Present', 'Absent', 'Late', 'Excused'):
            return False, "Invalid attendance status."

        session = db_manager.get_session()
        try:
            rec = session.query(AttendanceRecord).get(attendance_id)
            if not rec:
                return False, "Attendance record not found."

            old_status = rec.attendance_status
            rec.attendance_status = new_status
            rec.recorded_at = datetime.now()

            # Audit record (matches trigger behavior)
            audit = AuditLog(
                user_id=user_id,
                action_type='UPDATE',
                table_name='attendance_records',
                record_id=attendance_id,
                old_values=f'{{"status": "{old_status}"}}',
                new_values=f'{{"status": "{new_status}"}}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return True, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_student_course_attendance(student_id, course_id):
        """
        Computes accurate attendance percentage: (Present sessions / Total sessions) * 100
        """
        session = db_manager.get_session()
        try:
            enrollment = session.query(Enrollment).filter_by(student_id=student_id, course_id=course_id).first()
            if not enrollment:
                return {'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'excused': 0, 'percentage': 0.0}

            records = session.query(AttendanceRecord).filter_by(enrollment_id=enrollment.enrollment_id).all()
            total = len(records)
            present = sum(1 for r in records if r.attendance_status == 'Present')
            absent = sum(1 for r in records if r.attendance_status == 'Absent')
            late = sum(1 for r in records if r.attendance_status == 'Late')
            excused = sum(1 for r in records if r.attendance_status == 'Excused')

            percentage = round((present / total) * 100.0, 2) if total > 0 else 0.0
            return {
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'percentage': percentage
            }
        finally:
            session.close()

