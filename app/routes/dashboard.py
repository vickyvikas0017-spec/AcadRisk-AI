from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required
from app.services.dashboard_service import DashboardService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    role_name = session.get('role_name', 'ADMIN')

    if role_name == 'STUDENT':
        summary = DashboardService.get_student_dashboard_summary(
            user_id=user_id, student_id=session.get('student_id')
        )
        page_title = 'Student Academic Portal'
    elif role_name == 'FACULTY':
        summary = DashboardService.get_faculty_dashboard_summary(
            user_id=user_id, faculty_id=session.get('faculty_id')
        )
        page_title = 'Faculty Course Dashboard'
    else:
        summary = DashboardService.get_admin_dashboard_summary()
        page_title = 'Institutional Academic Dashboard'

    unread_count = NotificationService.get_unread_count(user_id)

    return render_template(
        'dashboard/index.html',
        active_page='dashboard',
        page_title=page_title,
        summary=summary,
        user_role=role_name,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )
