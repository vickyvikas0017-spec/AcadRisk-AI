from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required, role_required
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit-logs')
@login_required
@role_required(['ADMIN'])
def index():
    logs = AuditService.get_audit_logs(limit=100)
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'audit/index.html',
        active_page='audit',
        page_title='Audit Logs',
        logs=logs,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

