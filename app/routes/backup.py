from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.backup_service import BackupService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/backup-restore')
@login_required
@role_required(['ADMIN'])
def index():
    backups = BackupService.list_backups()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'backup/index.html',
        active_page='backup',
        page_title='Backup and Restore',
        backups=backups,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@backup_bp.route('/backup-restore/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create_backup():
    res = BackupService.create_database_backup(user_id=session.get('user_id'))
    if res.get('success'):
        flash(f"Database snapshot '{res['filename']}' created successfully ({res['tables_backed_up']} tables).", 'success')
    else:
        flash(f"Backup failed: {res.get('error')}", 'danger')
    return redirect(url_for('backup.index'))

@backup_bp.route('/backup-restore/restore', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def restore_backup():
    filename = request.form.get('filename')
    confirmed = (request.form.get('confirmed') == 'true')

    res = BackupService.restore_database_backup(filename, confirmation=confirmed, user_id=session.get('user_id'))
    if res.get('success'):
        flash(res['message'], 'success')
    else:
        flash(f"Restoration Rejected: {res.get('error')}", 'danger')
    return redirect(url_for('backup.index'))

