from flask import Blueprint, render_template, request, session, send_file
from app.utils.auth_helpers import login_required, role_required
from app.services.report_service import ReportService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
@role_required(['ADMIN', 'FACULTY'])
def index():
    preview_data = ReportService.get_department_performance()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'reports/index.html',
        active_page='reports',
        page_title='Reports and Analytics',
        preview_data=preview_data,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@reports_bp.route('/reports/export/<type>/<fmt>')
@login_required
@role_required(['ADMIN', 'FACULTY'])
def export(type, fmt):
    stream, filename, mimetype = ReportService.export_report(type, export_format=fmt)
    return send_file(
        stream,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

