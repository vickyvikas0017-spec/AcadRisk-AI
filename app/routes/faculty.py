from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.faculty_service import FacultyService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager, get_db
from app.models.entities import User

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/faculty')
@login_required
def index():
    faculty_list = FacultyService.get_all_faculty()
    departments = AcademicService.get_all_departments()
    
    # Available users with faculty role for modal assignment
    db = get_db()
    available_users = [u.to_dict() for u in db.query(User).filter_by(role_id=2).all()]
    db.close()
    
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'faculty/index.html',
        active_page='faculty',
        page_title='Faculty Management',
        faculty_list=faculty_list,
        departments=departments,
        available_users=available_users,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@faculty_bp.route('/faculty/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create():
    name = request.form.get('faculty_name')
    dept_id = request.form.get('department_id', type=int)
    designation = request.form.get('designation')
    user_id = request.form.get('user_id', type=int)
    contact = request.form.get('contact_information')

    fac, err = FacultyService.create_faculty(user_id, dept_id, name, designation, contact)
    if err:
        flash(f"Error registering faculty: {err}", 'danger')
    else:
        flash(f"Faculty member {name} registered successfully.", 'success')
    return redirect(url_for('faculty.index'))

