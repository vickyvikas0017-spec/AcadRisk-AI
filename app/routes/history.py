from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

history_bp = Blueprint('history', __name__)

@history_bp.route('/academic-history')
@login_required
def index():
    histories = AcademicService.get_academic_history()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'history/index.html',
        active_page='history',
        page_title='Academic History',
        histories=histories,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

