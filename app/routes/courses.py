from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses')
@login_required
@role_required(['ADMIN', 'FACULTY'])
def index():
    courses = AcademicService.get_all_courses()
    departments = AcademicService.get_all_departments()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'courses/index.html',
        active_page='courses',
        page_title='Course Management',
        courses=courses,
        departments=departments,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@courses_bp.route('/courses/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create():
    code = request.form.get('course_code')
    name = request.form.get('course_name')
    dept_id = request.form.get('department_id', type=int)
    credits = request.form.get('credits', type=int)
    desc = request.form.get('description')

    course, err = AcademicService.create_course(dept_id, code, name, credits, desc)
    if err:
        flash(f"Error creating course: {err}", 'danger')
    else:
        flash(f"Course {name} ({code}) created successfully.", 'success')
    return redirect(url_for('courses.index'))

