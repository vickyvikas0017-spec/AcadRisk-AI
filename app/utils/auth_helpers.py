from functools import wraps
from flask import session, redirect, url_for, flash, abort, request, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            user_role = session.get('role_name')
            if user_role not in allowed_roles:
                if request.is_json:
                    return jsonify({'error': 'Unauthorized: Insufficient role permissions'}), 403
                flash('Access Denied: You do not have permission to view this resource.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

