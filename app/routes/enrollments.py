from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.academic_service import AcademicService
from app.services.student_service import StudentService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

enrollments_bp = Blueprint('enrollments', __name__)

@enrollments_bp.route('/enrollments')
@login_required
@role_required(['ADMIN'])
def index():
    enrollments = AcademicService.get_enrollments()
    students, _ = StudentService.get_students(limit=100)
    courses = AcademicService.get_all_courses()
    semesters = AcademicService.get_all_semesters()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'enrollments/index.html',
        active_page='enrollments',
        page_title='Enrollment Management',
        enrollments=enrollments,
        students=students,
        courses=courses,
        semesters=semesters,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@enrollments_bp.route('/enrollments/create', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def create():
    student_id = request.form.get('student_id', type=int)
    course_id = request.form.get('course_id', type=int)
    semester_id = request.form.get('semester_id', type=int)

    enr, err = AcademicService.enroll_student(student_id, course_id, semester_id)
    if err:
        flash(f"Enrollment rejected: {err}", 'danger')
    else:
        flash("Student course enrollment completed successfully.", 'success')
    return redirect(url_for('enrollments.index'))

