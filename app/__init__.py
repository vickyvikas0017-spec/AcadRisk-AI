import os
from flask import Flask, render_template, session
from config import config_by_name, Config
from app.database.connection import db_manager
from app.services.notification_service import NotificationService

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))

    # Ensure required runtime folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)

    # Register all Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.students import students_bp
    from app.routes.faculty import faculty_bp
    from app.routes.departments import departments_bp
    from app.routes.courses import courses_bp
    from app.routes.semesters import semesters_bp
    from app.routes.enrollments import enrollments_bp
    from app.routes.attendance import attendance_bp
    from app.routes.examinations import examinations_bp
    from app.routes.marks import marks_bp
    from app.routes.history import history_bp
    from app.routes.predictions import predictions_bp
    from app.routes.risk import risk_bp
    from app.routes.interventions import interventions_bp
    from app.routes.notifications import notifications_bp
    from app.routes.imports import imports_bp
    from app.routes.database import database_bp
    from app.routes.reports import reports_bp
    from app.routes.models import models_bp
    from app.routes.audit import audit_bp
    from app.routes.backup import backup_bp
    from app.routes.users import users_bp
    from app.routes.settings import settings_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(semesters_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(examinations_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(interventions_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(database_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)

    # Global Template Context
    @app.context_processor
    def inject_global_data():
        user_id = session.get('user_id')
        unread = NotificationService.get_unread_count(user_id) if user_id else 0
        return {
            'db_dialect': db_manager.active_dialect,
            'is_db_connected': db_manager.is_connected,
            'unread_count': unread
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', page_title='Page Not Found', content='<div class="acad-card text-center py-5"><h3>404 - Page Not Found</h3><p class="text-muted">The requested URL could not be located on this academic server.</p><a href="/" class="btn btn-primary mt-2">Return to Dashboard</a></div>'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', page_title='System Error', content='<div class="acad-card text-center py-5"><h3>500 - Internal Server Error</h3><p class="text-muted">A server-side exception was encountered.</p><a href="/" class="btn btn-primary mt-2">Return to Dashboard</a></div>'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', page_title='Access Denied', content='<div class="acad-card text-center py-5"><h3>403 - Access Forbidden</h3><p class="text-muted">Your user role does not possess permissions for this resource.</p><a href="/" class="btn btn-primary mt-2">Return to Dashboard</a></div>'), 403

    return app

