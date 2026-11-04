from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.prediction_service import PredictionService
from app.services.student_service import StudentService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/predictions')
@login_required
def index():
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)

    predictions = PredictionService.get_predictions(limit=50)
    students, _ = StudentService.get_students(limit=100)
    courses = AcademicService.get_all_courses()
    semesters = AcademicService.get_all_semesters()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'predictions/index.html',
        active_page='predictions',
        page_title='AI Predictions',
        predictions=predictions,
        students=students,
        courses=courses,
        semesters=semesters,
        selected_student_id=student_id,
        selected_course_id=course_id,
        result=None,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@predictions_bp.route('/predictions/single', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def single_predict():
    student_id = request.form.get('student_id', type=int)
    course_id = request.form.get('course_id', type=int)
    semester_id = request.form.get('semester_id', type=int)

    res = PredictionService.run_prediction(student_id, course_id, semester_id, user_id=session.get('user_id'))
    if not res.get('success'):
        flash(f"Prediction Error: {res.get('error')}", 'danger')
        return redirect(url_for('predictions.index'))

    flash(f"ML Prediction generated: {res['student_name']} evaluated as {res['risk_category']} ({res['predicted_marks']}%)", 'success')
    
    predictions = PredictionService.get_predictions(limit=50)
    students, _ = StudentService.get_students(limit=100)
    courses = AcademicService.get_all_courses()
    semesters = AcademicService.get_all_semesters()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'predictions/index.html',
        active_page='predictions',
        page_title='AI Predictions',
        predictions=predictions,
        students=students,
        courses=courses,
        semesters=semesters,
        selected_student_id=student_id,
        selected_course_id=course_id,
        result=res,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@predictions_bp.route('/predictions/batch', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def batch_predict():
    batch_res = PredictionService.run_batch_predictions(user_id=session.get('user_id'))
    if batch_res.get('success'):
        dist = batch_res['risk_distribution']
        flash(f"Batch prediction complete: {batch_res['total_analyzed']} students evaluated. [High Risk: {dist.get('High Risk', 0)}, Medium: {dist.get('Medium Risk', 0)}, Low: {dist.get('Low Risk', 0)}]", 'success')
    else:
        flash(f"Batch evaluation error: {batch_res.get('error')}", 'danger')
    return redirect(url_for('predictions.index'))

