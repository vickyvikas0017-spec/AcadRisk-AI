from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required
from app.services.dashboard_service import DashboardService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    summary = DashboardService.get_dashboard_summary()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'dashboard/index.html',
        active_page='dashboard',
        page_title='Dashboard',
        summary=summary,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

