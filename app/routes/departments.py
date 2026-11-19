from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/departments')
@login_required
@role_required(['ADMIN'])
def index():
    departments = AcademicService.get_all_departments()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'departments/index.html',
        active_page='departments',
        page_title='Department Management',
        departments=departments,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@departments_bp.route('/departments/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create():
    code = request.form.get('department_code')
    name = request.form.get('department_name')
    desc = request.form.get('description')

    dept, err = AcademicService.create_department(name, code, desc)
    if err:
        flash(f"Error creating department: {err}", 'danger')
    else:
        flash(f"Department {name} ({code}) created successfully.", 'success')
    return redirect(url_for('departments.index'))

