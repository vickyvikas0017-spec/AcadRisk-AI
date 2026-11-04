import pytest
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import text, inspect
from app.database.connection import db_manager
from app.models.entities import (
    Role, User, Department, Faculty, Student, Course, Semester,
    Enrollment, AttendanceSession, AttendanceRecord, Assessment, Mark,
    AcademicHistory, AuditLog, Prediction
)

def test_database_table_existence():
    """Verify that all 23 relational database tables are created in the database schema."""
    insp = inspect(db_manager.engine)
    tables = insp.get_table_names()
    expected_tables = [
        'roles', 'users', 'departments', 'faculty', 'students', 'courses',
        'semesters', 'academic_calendar', 'enrollments', 'attendance_sessions',
        'attendance_records', 'assessments', 'marks', 'academic_history',
        'import_batches', 'import_errors', 'model_registry', 'prediction_runs',
        'predictions', 'interventions', 'notifications', 'audit_logs', 'risk_thresholds'
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' missing from database schema."

def test_student_unique_constraint():
    """Verify unique constraint on student registration number."""
    session = db_manager.get_session()
    try:
        # Registration number 'REG-2023-CS001' already exists from seed
        dup_student = Student(
            registration_number='REG-2023-CS001',
            student_name='Duplicate Tester',
            department_id=1,
            semester=2,
            admission_year=2024
        )
        session.add(dup_student)
        with pytest.raises(Exception):
            session.commit()
    finally:
        session.rollback()
        session.close()

def test_enrollment_unique_constraint():
    """Verify unique constraint on (student_id, course_id, semester_id) to prevent duplicate enrollments."""
    session = db_manager.get_session()
    try:
        # Enrollment (student_id=1, course_id=1, semester_id=1) already seeded
        dup_enr = Enrollment(
            student_id=1,
            course_id=1,
            semester_id=1,
            enrollment_date=date.today()
        )
        session.add(dup_enr)
        with pytest.raises(Exception):
            session.commit()
    finally:
        session.rollback()
        session.close()

def test_sql_joins_and_aggregates():
    """Verify SQL multi-table joins and aggregate functions (COUNT, AVG, MIN, MAX)."""
    session = db_manager.get_session()
    try:
        sql = text("""
            SELECT 
                d.department_code,
                COUNT(DISTINCT s.student_id) AS student_count,
                ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS avg_score,
                ROUND(MIN(m.obtained_marks), 2) AS min_mark,
                ROUND(MAX(m.obtained_marks), 2) AS max_mark
            FROM departments d
            JOIN students s ON d.department_id = s.department_id
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN marks m ON e.enrollment_id = m.enrollment_id
            JOIN assessments a ON m.assessment_id = a.assessment_id
            GROUP BY d.department_code
        """)
        results = session.execute(sql).fetchall()
        assert len(results) > 0, "SQL Join & Aggregate query returned no results."
        first_row = results[0]
        assert first_row[1] >= 1  # At least 1 student
        assert first_row[2] is not None  # Average score is computed
    finally:
        session.close()

def test_transaction_rollback():
    """Demonstrate database transaction atomicity with COMMIT and ROLLBACK."""
    session = db_manager.get_session()
    try:
        initial_dept_count = session.query(Department).count()

        # Start transactional block with invalid operation
        try:
            d1 = Department(department_name='Valid Temp Dept', department_code='TMP1')
            session.add(d1)
            session.flush()

            # Trigger deliberate constraint violation (duplicate code)
            d2 = Department(department_name='Colliding Dept', department_code='TMP1')
            session.add(d2)
            session.commit()
        except Exception:
            session.rollback()

        # Verify that atomic rollback restored state: Valid Temp Dept must not exist
        final_dept_count = session.query(Department).count()
        assert final_dept_count == initial_dept_count, "Rollback failed: partial insert was committed."
    finally:
        session.close()

def test_audit_log_recording():
    """Verify that important actions are captured in the audit_logs table."""
    session = db_manager.get_session()
    try:
        audit = AuditLog(
            user_id=1,
            action_type='TEST_ACTION',
            table_name='students',
            record_id=1,
            old_values='{"status": "test_old"}',
            new_values='{"status": "test_new"}',
            timestamp=datetime.now()
        )
        session.add(audit)
        session.commit()

        logged = session.query(AuditLog).filter_by(action_type='TEST_ACTION').first()
        assert logged is not None
        assert logged.table_name == 'students'
    finally:
        session.close()

