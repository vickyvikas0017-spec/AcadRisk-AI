from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

semesters_bp = Blueprint('semesters', __name__)

@semesters_bp.route('/semesters')
@login_required
def index():
    semesters = AcademicService.get_all_semesters()
    calendar_events = AcademicService.get_calendar_events()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'semesters/index.html',
        active_page='semesters',
        page_title='Semester Management',
        semesters=semesters,
        calendar_events=calendar_events,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@semesters_bp.route('/semesters/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create():
    name = request.form.get('semester_name')
    ay = request.form.get('academic_year')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    sem, err = AcademicService.create_semester(name, ay, start_date, end_date)
    if err:
        flash(f"Error creating semester: {err}", 'danger')
    else:
        flash(f"Semester {name} created successfully.", 'success')
    return redirect(url_for('semesters.index'))

