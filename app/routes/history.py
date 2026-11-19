from flask import Blueprint, render_template, session
from app.utils.auth_helpers import login_required
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager, get_db
from app.models.entities import Student

history_bp = Blueprint('history', __name__)

@history_bp.route('/academic-history')
@login_required
def index():
    student_id = None
    if session.get('role_name') == 'STUDENT':
        student_id = session.get('student_id')
        if not student_id:
            db = get_db()
            stu = db.query(Student).filter_by(user_id=session.get('user_id')).first()
            if not stu:
                stu = db.query(Student).first()
            if stu:
                student_id = stu.student_id
            db.close()

    histories = AcademicService.get_academic_history(student_id=student_id)
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'history/index.html',
        active_page='history',
        page_title='Academic History',
        histories=histories,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

