from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def index():
    user_id = session.get('user_id')
    notifications = NotificationService.get_user_notifications(user_id)
    unread_count = NotificationService.get_unread_count(user_id)

    return render_template(
        'notifications/index.html',
        active_page='notifications',
        page_title='Notifications',
        notifications=notifications,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@notifications_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    user_id = session.get('user_id')
    NotificationService.mark_as_read(notification_id, user_id)
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    user_id = session.get('user_id')
    NotificationService.mark_all_as_read(user_id)
    flash('All notifications marked as read.', 'info')
    return redirect(url_for('notifications.index'))

