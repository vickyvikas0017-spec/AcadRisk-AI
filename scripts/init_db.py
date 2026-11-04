import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import db_manager, Base
from app.models.entities import (
    Role, User, Department, Faculty, Student, Course, Semester, AcademicCalendar,
    Enrollment, AttendanceSession, AttendanceRecord, Assessment, Mark, AcademicHistory,
    RiskThreshold
)
from sqlalchemy import text
from datetime import datetime, date
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    logger.info(f"Connecting to database. Dialect: {db_manager.active_dialect}")
    engine = db_manager.engine

    # Step 1: Create all tables via SQLAlchemy declarative models
    logger.info("Creating all 23 relational database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")

    # Step 2: Create Views
    logger.info("Creating database views...")
    views_sql_path = Path(__file__).resolve().parent.parent / 'sql' / 'views.sql'
    if views_sql_path.exists():
        with open(views_sql_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split views
            commands = [cmd.strip() for cmd in content.split(';') if cmd.strip() and not cmd.strip().startswith('--') and not cmd.strip().upper().startswith('USE')]
            with engine.connect() as conn:
                for cmd in commands:
                    try:
                        # SQLite uses CREATE VIEW IF NOT EXISTS or DROP VIEW IF EXISTS
                        if db_manager.active_dialect == 'sqlite':
                            cmd_sqlite = cmd.replace('CREATE OR REPLACE VIEW', 'CREATE VIEW IF NOT EXISTS')
                            cmd_sqlite = cmd_sqlite.replace('CONCAT(', 'COALESCE(')
                            conn.execute(text(cmd_sqlite))
                        else:
                            conn.execute(text(cmd))
                        conn.commit()
                    except Exception as ve:
                        logger.warning(f"Note on view creation: {ve}")

    # Step 3: Seed initial institutional data if empty
    session = db_manager.get_session()
    try:
        user_count = session.query(User).count()
        if user_count == 0:
            logger.info("Seeding initial institutional roles, users, departments, courses and students...")
            
            # Roles
            r_admin = Role(role_id=1, role_name='ADMIN', description='Institutional Administrator')
            r_faculty = Role(role_id=2, role_name='FACULTY', description='Teaching Faculty')
            r_student = Role(role_id=3, role_name='STUDENT', description='Enrolled Student')
            session.add_all([r_admin, r_faculty, r_student])
            session.flush()

            # Users
            # Admin@123, Faculty@123, Student@123 hashes
            admin_hash = 'scrypt:32768:8:1$xkCHza26FYaW92fs$5ce797162bff9e10c4552b9fbb68516cf87ecdb57fd3bdcd66a4003418ba6bf7b8e662e73df090bcfc443d4505789e2d544313763a8d636c73796ec26cdb59b9'
            fac_hash = 'scrypt:32768:8:1$zUHkzgwrP02NvHla$ecdc32afb257c0d0929f9c2ef15cd78678fbb9934ed779a3a27b7ec927c5264ed153a4df2a9b0afbab845e2a9174685fc241b13486a89073170dc98adba604be'
            stu_hash = 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc'

            u_admin = User(user_id=1, role_id=1, username='admin', email='admin@acadrisk.edu', password_hash=admin_hash, account_status='active')
            u_smith = User(user_id=2, role_id=2, username='prof_smith', email='smith@acadrisk.edu', password_hash=fac_hash, account_status='active')
            u_johnson = User(user_id=3, role_id=2, username='prof_johnson', email='johnson@acadrisk.edu', password_hash=fac_hash, account_status='active')
            u_patel = User(user_id=4, role_id=2, username='prof_patel', email='patel@acadrisk.edu', password_hash=fac_hash, account_status='active')
            u_doe = User(user_id=5, role_id=3, username='john_doe', email='john.doe@acadrisk.edu', password_hash=stu_hash, account_status='active')
            u_watson = User(user_id=6, role_id=3, username='emma_watson', email='emma.watson@acadrisk.edu', password_hash=stu_hash, account_status='active')
            u_sharma = User(user_id=7, role_id=3, username='raj_sharma', email='raj.sharma@acadrisk.edu', password_hash=stu_hash, account_status='active')
            session.add_all([u_admin, u_smith, u_johnson, u_patel, u_doe, u_watson, u_sharma])
            session.flush()

            # Departments
            d_cse = Department(department_id=1, department_name='Computer Science and Engineering', department_code='CSE', description='Computing, algorithms, and AI systems.')
            d_it = Department(department_id=2, department_name='Information Technology', department_code='IT', description='Web systems, cloud, and enterprise architecture.')
            d_ece = Department(department_id=3, department_name='Electronics and Communication', department_code='ECE', description='Embedded systems and signal processing.')
            d_me = Department(department_id=4, department_name='Mechanical Engineering', department_code='ME', description='Mechanics, robotics, and thermodynamics.')
            session.add_all([d_cse, d_it, d_ece, d_me])
            session.flush()

            # Faculty
            f1 = Faculty(faculty_id=1, user_id=2, department_id=1, faculty_name='Dr. Alan Smith', designation='Professor & Head', contact_information='+1-555-0101 | asmith@acadrisk.edu')
            f2 = Faculty(faculty_id=2, user_id=3, department_id=1, faculty_name='Dr. Sarah Johnson', designation='Associate Professor', contact_information='+1-555-0102 | sjohnson@acadrisk.edu')
            f3 = Faculty(faculty_id=3, user_id=4, department_id=2, faculty_name='Prof. Rajesh Patel', designation='Assistant Professor', contact_information='+1-555-0103 | rpatel@acadrisk.edu')
            session.add_all([f1, f2, f3])
            session.flush()

            # Students
            s1 = Student(student_id=1, user_id=5, department_id=1, registration_number='REG-2023-CS001', student_name='John Doe', date_of_birth=date(2004, 5, 14), admission_year=2023, semester=6, contact_information='+1-555-0201 | Campus Dorm A')
            s2 = Student(student_id=2, user_id=6, department_id=1, registration_number='REG-2023-CS002', student_name='Emma Watson', date_of_birth=date(2004, 9, 21), admission_year=2023, semester=6, contact_information='+1-555-0202 | Campus Dorm B')
            s3 = Student(student_id=3, user_id=7, department_id=1, registration_number='REG-2023-CS003', student_name='Raj Sharma', date_of_birth=date(2003, 12, 5), admission_year=2023, semester=6, contact_information='+1-555-0203 | Off-campus Apt 3')
            s4 = Student(student_id=4, user_id=None, department_id=2, registration_number='REG-2023-IT001', student_name='Priya Verma', date_of_birth=date(2004, 2, 18), admission_year=2023, semester=6, contact_information='+1-555-0204 | Campus Dorm C')
            s5 = Student(student_id=5, user_id=None, department_id=1, registration_number='REG-2024-CS010', student_name='Vikram Rao', date_of_birth=date(2002, 4, 10), admission_year=2022, semester=8, contact_information='+1-555-0205 | Off-campus')
            session.add_all([s1, s2, s3, s4, s5])
            session.flush()

            # Courses
            c1 = Course(course_id=1, department_id=1, course_code='CS-301', course_name='Database Management Systems', credits=4, description='Relational model, normalization, indexing, transactions.')
            c2 = Course(course_id=2, department_id=1, course_code='CS-302', course_name='Artificial Intelligence & Machine Learning', credits=4, description='Supervised learning, deep architectures, predictive analytics.')
            c3 = Course(course_id=3, department_id=1, course_code='CS-303', course_name='Design and Analysis of Algorithms', credits=4, description='Divide and conquer, dynamic programming, graph algorithms.')
            c4 = Course(course_id=4, department_id=2, course_code='IT-301', course_name='Web Application Engineering', credits=3, description='Full stack web development and REST APIs.')
            session.add_all([c1, c2, c3, c4])
            session.flush()

            # Semesters
            sem1 = Semester(semester_id=1, semester_name='Spring 2026', academic_year='2025-2026', start_date=date(2026, 1, 5), end_date=date(2026, 5, 20), status='active')
            sem2 = Semester(semester_id=2, semester_name='Fall 2025', academic_year='2025-2026', start_date=date(2025, 8, 1), end_date=date(2025, 12, 18), status='completed')
            session.add_all([sem1, sem2])
            session.flush()

            # Academic Calendar
            cal1 = AcademicCalendar(calendar_id=1, semester_id=1, event_name='Course Add/Drop Deadline', event_date=date(2026, 1, 15), description='Last date to adjust course registrations.')
            cal2 = AcademicCalendar(calendar_id=2, semester_id=1, event_name='Mid-Term Assessments', event_date=date(2026, 3, 20), description='Internal Assessment 2 period.')
            cal3 = AcademicCalendar(calendar_id=3, semester_id=1, event_name='Final Examinations', event_date=date(2026, 5, 10), description='Comprehensive final exams.')
            session.add_all([cal1, cal2, cal3])
            session.flush()

            # Enrollments
            e1 = Enrollment(enrollment_id=1, student_id=1, course_id=1, semester_id=1, enrollment_date=date(2026, 1, 6), enrollment_status='enrolled')
            e2 = Enrollment(enrollment_id=2, student_id=1, course_id=2, semester_id=1, enrollment_date=date(2026, 1, 6), enrollment_status='enrolled')
            e3 = Enrollment(enrollment_id=3, student_id=2, course_id=1, semester_id=1, enrollment_date=date(2026, 1, 6), enrollment_status='enrolled')
            e4 = Enrollment(enrollment_id=4, student_id=3, course_id=1, semester_id=1, enrollment_date=date(2026, 1, 6), enrollment_status='enrolled')
            e5 = Enrollment(enrollment_id=5, student_id=5, course_id=1, semester_id=1, enrollment_date=date(2026, 1, 6), enrollment_status='enrolled')
            session.add_all([e1, e2, e3, e4, e5])
            session.flush()

            # Attendance Sessions & Records
            att_sess1 = AttendanceSession(session_id=1, course_id=1, semester_id=1, faculty_id=1, session_date=date(2026, 1, 12), session_type='Lecture')
            att_sess2 = AttendanceSession(session_id=2, course_id=1, semester_id=1, faculty_id=1, session_date=date(2026, 1, 19), session_type='Lecture')
            att_sess3 = AttendanceSession(session_id=3, course_id=1, semester_id=1, faculty_id=1, session_date=date(2026, 1, 26), session_type='Lab Session')
            att_sess4 = AttendanceSession(session_id=4, course_id=1, semester_id=1, faculty_id=1, session_date=date(2026, 2, 2), session_type='Lecture')
            att_sess5 = AttendanceSession(session_id=5, course_id=1, semester_id=1, faculty_id=1, session_date=date(2026, 2, 9), session_type='Lecture')
            session.add_all([att_sess1, att_sess2, att_sess3, att_sess4, att_sess5])
            session.flush()

            # Records: Emma & John present; Raj and Vikram have multiple absences
            att_records = [
                AttendanceRecord(session_id=1, enrollment_id=1, attendance_status='Present'),
                AttendanceRecord(session_id=2, enrollment_id=1, attendance_status='Present'),
                AttendanceRecord(session_id=3, enrollment_id=1, attendance_status='Present'),
                AttendanceRecord(session_id=4, enrollment_id=1, attendance_status='Late'),
                AttendanceRecord(session_id=5, enrollment_id=1, attendance_status='Present'),

                AttendanceRecord(session_id=1, enrollment_id=3, attendance_status='Present'),
                AttendanceRecord(session_id=2, enrollment_id=3, attendance_status='Present'),
                AttendanceRecord(session_id=3, enrollment_id=3, attendance_status='Present'),
                AttendanceRecord(session_id=4, enrollment_id=3, attendance_status='Present'),
                AttendanceRecord(session_id=5, enrollment_id=3, attendance_status='Present'),

                AttendanceRecord(session_id=1, enrollment_id=4, attendance_status='Absent'),
                AttendanceRecord(session_id=2, enrollment_id=4, attendance_status='Absent'),
                AttendanceRecord(session_id=3, enrollment_id=4, attendance_status='Present'),
                AttendanceRecord(session_id=4, enrollment_id=4, attendance_status='Absent'),
                AttendanceRecord(session_id=5, enrollment_id=4, attendance_status='Absent'),

                AttendanceRecord(session_id=1, enrollment_id=5, attendance_status='Absent'),
                AttendanceRecord(session_id=2, enrollment_id=5, attendance_status='Absent'),
                AttendanceRecord(session_id=3, enrollment_id=5, attendance_status='Absent'),
                AttendanceRecord(session_id=4, enrollment_id=5, attendance_status='Present'),
                AttendanceRecord(session_id=5, enrollment_id=5, attendance_status='Absent'),
            ]
            session.add_all(att_records)
            session.flush()

            # Assessments
            a1 = Assessment(assessment_id=1, course_id=1, semester_id=1, assessment_name='Internal Assessment 1', assessment_type='Internal 1', maximum_marks=Decimal('25.00'), assessment_date=date(2026, 2, 15))
            a2 = Assessment(assessment_id=2, course_id=1, semester_id=1, assessment_name='Internal Assessment 2 (Mid-Term)', assessment_type='Internal 2', maximum_marks=Decimal('25.00'), assessment_date=date(2026, 3, 25))
            a3 = Assessment(assessment_id=3, course_id=1, semester_id=1, assessment_name='Database Practical Exam', assessment_type='Practical', maximum_marks=Decimal('20.00'), assessment_date=date(2026, 4, 10))
            session.add_all([a1, a2, a3])
            session.flush()

            # Marks: Emma high (24, 23.5, 19.5), John good (21.5, 20, 18), Raj low (8.5, 7.0, 9.0), Vikram very low (5.0, 6.0, 7.5)
            marks_list = [
                Mark(assessment_id=1, enrollment_id=1, obtained_marks=Decimal('21.50'), recorded_by=2),
                Mark(assessment_id=2, enrollment_id=1, obtained_marks=Decimal('20.00'), recorded_by=2),
                Mark(assessment_id=3, enrollment_id=1, obtained_marks=Decimal('18.00'), recorded_by=2),

                Mark(assessment_id=1, enrollment_id=3, obtained_marks=Decimal('24.00'), recorded_by=2),
                Mark(assessment_id=2, enrollment_id=3, obtained_marks=Decimal('23.50'), recorded_by=2),
                Mark(assessment_id=3, enrollment_id=3, obtained_marks=Decimal('19.50'), recorded_by=2),

                Mark(assessment_id=1, enrollment_id=4, obtained_marks=Decimal('8.50'), recorded_by=2),
                Mark(assessment_id=2, enrollment_id=4, obtained_marks=Decimal('7.00'), recorded_by=2),
                Mark(assessment_id=3, enrollment_id=4, obtained_marks=Decimal('9.00'), recorded_by=2),

                Mark(assessment_id=1, enrollment_id=5, obtained_marks=Decimal('5.00'), recorded_by=2),
                Mark(assessment_id=2, enrollment_id=5, obtained_marks=Decimal('6.00'), recorded_by=2),
                Mark(assessment_id=3, enrollment_id=5, obtained_marks=Decimal('7.50'), recorded_by=2),
            ]
            session.add_all(marks_list)
            session.flush()

            # Academic History
            hist_records = [
                AcademicHistory(student_id=1, semester_id=2, course_id=1, final_grade='A', grade_point=Decimal('8.50'), credits=4, result_status='Pass'),
                AcademicHistory(student_id=2, semester_id=2, course_id=1, final_grade='A+', grade_point=Decimal('9.80'), credits=4, result_status='Pass'),
                AcademicHistory(student_id=3, semester_id=2, course_id=1, final_grade='D', grade_point=Decimal('4.50'), credits=4, result_status='Pass'),
                AcademicHistory(student_id=5, semester_id=2, course_id=3, final_grade='F', grade_point=Decimal('0.00'), credits=4, result_status='Fail'),
            ]
            session.add_all(hist_records)
            session.flush()

            # Risk Thresholds
            thresh1 = RiskThreshold(department_id=None, course_id=None, high_risk_threshold=Decimal('40.00'), medium_risk_threshold=Decimal('60.00'), low_risk_threshold=Decimal('80.00'))
            thresh2 = RiskThreshold(department_id=1, course_id=1, high_risk_threshold=Decimal('45.00'), medium_risk_threshold=Decimal('65.00'), low_risk_threshold=Decimal('80.00'))
            session.add_all([thresh1, thresh2])
            session.flush()

            session.commit()
            logger.info("Institutional seed data successfully committed!")
        else:
            logger.info(f"Database already contains {user_count} users. Skipping seed insertion.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error during database initialization: {e}")
        raise
    finally:
        session.close()

    # Step 4: Verify and print summary
    stats = db_manager.get_table_statistics()
    logger.info("=== Database Initialization Summary ===")
    for s in stats:
        logger.info(f"Table: {s['name']:<25} Rows: {s['row_count']:<6} Columns: {s['column_count']:<4}")
    logger.info("========================================")

if __name__ == '__main__':
    initialize_database()

