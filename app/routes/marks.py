from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.marks_service import MarksService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager, get_db
from app.models.entities import Assessment, Mark, Student

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks')
@login_required
def index():
    assessment_id = request.args.get('assessment_id', type=int)
    assessments = MarksService.get_assessments()
    enrollments = AcademicService.get_enrollments()

    db = get_db()
    try:
        selected_asmt = db.query(Assessment).get(assessment_id).to_dict() if assessment_id else None
        query = db.query(Mark)
        if assessment_id:
            query = query.filter_by(assessment_id=assessment_id)

        # Scope marks if logged in as student
        if session.get('role_name') == 'STUDENT':
            student = db.query(Student).filter_by(user_id=session.get('user_id')).first()
            if not student and session.get('student_id'):
                student = db.query(Student).filter_by(student_id=session.get('student_id')).first()
            if not student:
                student = db.query(Student).first()
            if student:
                enr_ids = [e.enrollment_id for e in student.enrollments]
                query = query.filter(Mark.enrollment_id.in_(enr_ids))

        marks = [m.to_dict() for m in query.all()]
    finally:
        db.close()

    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'marks/index.html',
        active_page='marks',
        page_title='Marks Management',
        assessments=assessments,
        enrollments=enrollments,
        marks=marks,
        selected_assessment=selected_asmt,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@marks_bp.route('/marks/record', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def record():
    assessment_id = request.form.get('assessment_id', type=int)
    enrollment_id = request.form.get('enrollment_id', type=int)
    obtained_marks = request.form.get('obtained_marks', type=float)

    mark, err = MarksService.record_mark(
        assessment_id=assessment_id,
        enrollment_id=enrollment_id,
        obtained_marks=obtained_marks,
        recorded_by=session.get('user_id')
    )

    if err:
        flash(f"Constraint Violation: {err}", 'danger')
    else:
        flash("Marks awarded and recorded into database successfully.", 'success')
    return redirect(url_for('marks.index', assessment_id=assessment_id))

