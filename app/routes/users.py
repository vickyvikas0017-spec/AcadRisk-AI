from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager, get_db
from app.models.entities import User, Role

users_bp = Blueprint('users', __name__)

@users_bp.route('/user-management')
@login_required
@role_required(['ADMIN'])
def index():
    db = get_db()
    try:
        users = [u.to_dict() for u in db.query(User).all()]
        roles = [r.to_dict() for r in db.query(Role).all()]
    finally:
        db.close()

    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'users/index.html',
        active_page='users',
        page_title='User Management',
        users=users,
        roles=roles,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@users_bp.route('/user-management/create', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def create():
    username = request.form.get('username')
    email = request.form.get('email')
    role_id = request.form.get('role_id', type=int)
    password = request.form.get('password')

    user, err = AuthService.create_user(username, email, password, role_id)
    if err:
        flash(f"Error creating user: {err}", 'danger')
    else:
        flash(f"User '{username}' registered successfully.", 'success')
    return redirect(url_for('users.index'))

