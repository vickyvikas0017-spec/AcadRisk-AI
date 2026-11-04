from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required
from app.services.prediction_service import PredictionService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/risk-monitoring')
@login_required
def index():
    high_risk_students = PredictionService.get_predictions(risk_category='High Risk')
    medium_risk_students = PredictionService.get_predictions(risk_category='Medium Risk')
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'risk/index.html',
        active_page='risk',
        page_title='Risk Monitoring',
        high_risk_students=high_risk_students,
        medium_risk_students=medium_risk_students,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

