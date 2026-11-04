from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.marks_service import MarksService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

examinations_bp = Blueprint('examinations', __name__)

@examinations_bp.route('/examinations')
@login_required
def index():
    assessments = MarksService.get_assessments()
    courses = AcademicService.get_all_courses()
    semesters = AcademicService.get_all_semesters()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'examinations/index.html',
        active_page='examinations',
        page_title='Examination Management',
        assessments=assessments,
        courses=courses,
        semesters=semesters,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@examinations_bp.route('/examinations/create', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def create():
    course_id = request.form.get('course_id', type=int)
    semester_id = request.form.get('semester_id', type=int)
    name = request.form.get('assessment_name')
    atype = request.form.get('assessment_type')
    max_marks = request.form.get('maximum_marks', type=float)
    date_str = request.form.get('assessment_date')

    asmt, err = MarksService.create_assessment(course_id, semester_id, name, atype, max_marks, date_str)
    if err:
        flash(f"Error creating assessment: {err}", 'danger')
    else:
        flash(f"Assessment '{name}' created successfully.", 'success')
    return redirect(url_for('examinations.index'))

