from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import date
from sqlalchemy import text
from app.utils.auth_helpers import login_required, role_required
from app.services.attendance_service import AttendanceService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
@login_required
def index():
    sessions = AttendanceService.get_sessions()
    courses = AcademicService.get_all_courses()
    semesters = AcademicService.get_all_semesters()
    enrollments = AcademicService.get_enrollments()
    
    # Query student attendance summary view or fallback
    session_db = db_manager.get_session()
    try:
        res = session_db.execute(text("""
            SELECT 
                s.registration_number,
                s.student_name,
                c.course_code,
                c.course_name,
                COUNT(ar.attendance_id) AS total_sessions,
                SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN ar.attendance_status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
                SUM(CASE WHEN ar.attendance_status = 'Late' THEN 1 ELSE 0 END) AS late_count,
                ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(ar.attendance_id), 0)), 1) AS attendance_percentage
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN courses c ON e.course_id = c.course_id
            LEFT JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
            GROUP BY s.registration_number, s.student_name, c.course_code, c.course_name
        """))
        student_attendance = [dict(row._mapping) for row in res]
    finally:
        session_db.close()

    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'attendance/index.html',
        active_page='attendance',
        page_title='Attendance Management',
        sessions=sessions,
        courses=courses,
        semesters=semesters,
        enrollments=enrollments,
        student_attendance=student_attendance,
        today=date.today().strftime('%Y-%m-%d'),
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@attendance_bp.route('/attendance/session/create', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def create_session():
    course_id = request.form.get('course_id', type=int)
    semester_id = request.form.get('semester_id', type=int)
    session_date = request.form.get('session_date')
    session_type = request.form.get('session_type', 'Lecture')
    
    # Determine faculty id
    faculty_id = 1
    enrollment_ids = request.form.getlist('enrollment_id')
    records_data = []
    for eid in enrollment_ids:
        status = request.form.get(f'status_{eid}', 'Present')
        records_data.append({'enrollment_id': int(eid), 'status': status})

    sess, err = AttendanceService.create_session_and_record(
        course_id=course_id,
        semester_id=semester_id,
        faculty_id=faculty_id,
        session_date=session_date,
        session_type=session_type,
        records_data=records_data,
        user_id=session.get('user_id')
    )

    if err:
        flash(f"Error logging attendance: {err}", 'danger')
    else:
        flash(f"Attendance session recorded successfully ({len(records_data)} students).", 'success')
    return redirect(url_for('attendance.index'))

