from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from decimal import Decimal
from datetime import datetime
from app.utils.auth_helpers import login_required, role_required
from app.services.notification_service import NotificationService
from app.database.connection import db_manager, get_db
from app.models.entities import RiskThreshold

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def index():
    db = get_db()
    try:
        thresholds = [t.to_dict() for t in db.query(RiskThreshold).all()]
    finally:
        db.close()

    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'settings/index.html',
        active_page='settings',
        page_title='Settings',
        thresholds=thresholds,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@settings_bp.route('/settings/update-thresholds', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def update_thresholds():
    high_th = request.form.get('high_risk_threshold', type=float)
    med_th = request.form.get('medium_risk_threshold', type=float)
    low_th = request.form.get('low_risk_threshold', type=float)

    db = get_db()
    try:
        global_th = db.query(RiskThreshold).filter_by(department_id=None, course_id=None).first()
        if not global_th:
            global_th = RiskThreshold()
            db.add(global_th)

        global_th.high_risk_threshold = Decimal(str(high_th))
        global_th.medium_risk_threshold = Decimal(str(med_th))
        global_th.low_risk_threshold = Decimal(str(low_th))
        global_th.updated_at = datetime.now()
        db.commit()
        flash('Risk calculation thresholds updated successfully.', 'success')
    except Exception as e:
        db.rollback()
        flash(f"Error updating thresholds: {str(e)}", 'danger')
    finally:
        db.close()

    return redirect(url_for('settings.index'))

