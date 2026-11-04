from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user, err = AuthService.authenticate(username, password)
        if err:
            flash(err, 'danger')
            return render_template('auth/login.html')

        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role_name'] = user['role_name']
        session['role_id'] = user['role_id']

        flash(f"Welcome back, {user['username']}! Logged in as {user['role_name']}.", 'success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('dashboard.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

