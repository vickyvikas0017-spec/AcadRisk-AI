from flask import Blueprint, render_template, request, session, flash
from app.utils.auth_helpers import login_required, role_required
from app.services.db_service import DatabaseService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

database_bp = Blueprint('database', __name__)

@database_bp.route('/database-management')
@login_required
@role_required(['ADMIN'])
def index():
    db_status = DatabaseService.get_database_status()
    views_info = DatabaseService.get_views_info()
    procedures_info = DatabaseService.get_procedures_info()
    triggers_info = DatabaseService.get_triggers_info()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'database/index.html',
        active_page='database',
        page_title='Database Management',
        db_status=db_status,
        views_info=views_info,
        procedures_info=procedures_info,
        triggers_info=triggers_info,
        query_result=None,
        explain_result=None,
        submitted_sql=None,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@database_bp.route('/database-management/run-sql', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def run_sql():
    sql = request.form.get('sql', '').strip()
    action = request.form.get('action', 'execute')

    query_result = None
    explain_result = None

    if action == 'explain':
        plan = DatabaseService.get_query_execution_plan(sql)
        if plan.get('success'):
            explain_result = plan['plan']
        else:
            flash(f"EXPLAIN Error: {plan.get('error')}", 'danger')
    else:
        res = DatabaseService.execute_safe_query(sql)
        if res.get('success'):
            query_result = res
        else:
            flash(f"Query Execution Error: {res.get('error')}", 'danger')

    db_status = DatabaseService.get_database_status()
    views_info = DatabaseService.get_views_info()
    procedures_info = DatabaseService.get_procedures_info()
    triggers_info = DatabaseService.get_triggers_info()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'database/index.html',
        active_page='database',
        page_title='Database Management',
        db_status=db_status,
        views_info=views_info,
        procedures_info=procedures_info,
        triggers_info=triggers_info,
        query_result=query_result,
        explain_result=explain_result,
        submitted_sql=sql,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

