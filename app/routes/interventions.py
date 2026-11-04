from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.intervention_service import InterventionService
from app.services.student_service import StudentService
from app.services.faculty_service import FacultyService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

interventions_bp = Blueprint('interventions', __name__)

@interventions_bp.route('/interventions')
@login_required
def index():
    student_id = request.args.get('student_id', type=int)
    prediction_id = request.args.get('prediction_id', type=int)

    interventions = InterventionService.get_interventions()
    students, _ = StudentService.get_students(limit=100)
    faculty = FacultyService.get_all_faculty()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'interventions/index.html',
        active_page='interventions',
        page_title='Intervention Management',
        interventions=interventions,
        students=students,
        faculty=faculty,
        selected_student_id=student_id,
        selected_prediction_id=prediction_id,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@interventions_bp.route('/interventions/create', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def create():
    student_id = request.form.get('student_id', type=int)
    faculty_id = request.form.get('faculty_id', type=int)
    itype = request.form.get('intervention_type')
    desc = request.form.get('description')
    follow_up = request.form.get('follow_up_date')
    prediction_id = request.form.get('prediction_id', type=int)

    interv, err = InterventionService.create_intervention(
        student_id=student_id,
        faculty_id=faculty_id,
        intervention_type=itype,
        description=desc,
        follow_up_date=follow_up,
        prediction_id=prediction_id,
        user_id=session.get('user_id')
    )

    if err:
        flash(f"Error recording intervention: {err}", 'danger')
    else:
        flash("Academic intervention logged and assigned to faculty.", 'success')
    return redirect(url_for('interventions.index'))

@interventions_bp.route('/interventions/update/<int:intervention_id>', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def update(intervention_id):
    status = request.form.get('status')
    outcome = request.form.get('outcome')

    interv, err = InterventionService.update_intervention(
        intervention_id=intervention_id,
        status=status,
        outcome=outcome,
        user_id=session.get('user_id')
    )

    if err:
        flash(f"Error updating intervention: {err}", 'danger')
    else:
        flash("Intervention status and outcome updated.", 'success')
    return redirect(url_for('interventions.index'))

