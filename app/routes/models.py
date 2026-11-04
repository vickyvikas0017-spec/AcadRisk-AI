from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.database.connection import db_manager, get_db
from app.models.entities import ModelRegistry
from app.services.notification_service import NotificationService
from app.ml.trainer import ModelTrainer

models_bp = Blueprint('models', __name__)

@models_bp.route('/model-management')
@login_required
@role_required(['ADMIN'])
def index():
    db = get_db()
    try:
        models = [m.to_dict() for m in db.query(ModelRegistry).order_by(ModelRegistry.model_id.desc()).all()]
        active_model = next((m for m in models if m['model_status'] == 'active'), None)
    finally:
        db.close()

    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'models/index.html',
        active_page='models',
        page_title='Model Management',
        models=models,
        active_model=active_model,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@models_bp.route('/model-management/retrain', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def retrain():
    try:
        trainer = ModelTrainer()
        output = trainer.train_and_compare_models()
        flash(f"ML Pipeline retraining completed. Selected best model: {output['best_model']}", 'success')
    except Exception as e:
        flash(f"Model retraining failed: {str(e)}", 'danger')
    return redirect(url_for('models.index'))

