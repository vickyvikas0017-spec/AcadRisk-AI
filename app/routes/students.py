from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth_helpers import login_required, role_required
from app.services.student_service import StudentService
from app.services.academic_service import AcademicService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
@login_required
def index():
    search_query = request.args.get('q', '').strip()
    dept_id = request.args.get('dept', type=int)
    semester = request.args.get('sem', type=int)

    students, total_count = StudentService.get_students(
        search_query=search_query,
        department_id=dept_id,
        semester=semester
    )
    departments = AcademicService.get_all_departments()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))

    return render_template(
        'students/index.html',
        active_page='students',
        page_title='Student Management',
        students=students,
        total_count=total_count,
        departments=departments,
        search_query=search_query,
        selected_dept=dept_id,
        selected_sem=semester,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@students_bp.route('/students/create', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def create():
    reg_no = request.form.get('registration_number')
    name = request.form.get('student_name')
    dept_id = request.form.get('department_id', type=int)
    semester = request.form.get('semester', type=int)
    adm_year = request.form.get('admission_year', type=int)
    dob = request.form.get('date_of_birth')
    contact = request.form.get('contact_information')

    student, err = StudentService.create_student(
        reg_no=reg_no,
        name=name,
        dept_id=dept_id,
        semester=semester,
        admission_year=adm_year,
        dob=dob,
        contact=contact,
        user_id=session.get('user_id')
    )

    if err:
        flash(f"Error registering student: {err}", 'danger')
    else:
        flash(f"Student {name} ({reg_no}) registered successfully!", 'success')

    return redirect(url_for('students.index'))

@students_bp.route('/students/update/<int:student_id>', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def update(student_id):
    name = request.form.get('student_name')
    dept_id = request.form.get('department_id', type=int)
    semester = request.form.get('semester', type=int)
    contact = request.form.get('contact_information')

    student, err = StudentService.update_student(
        student_id=student_id,
        name=name,
        dept_id=dept_id,
        semester=semester,
        contact=contact,
        user_id=session.get('user_id')
    )

    if err:
        flash(f"Error updating student: {err}", 'danger')
    else:
        flash("Student details updated successfully.", 'success')

    return redirect(url_for('students.index'))

@students_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@role_required(['ADMIN'])
def delete(student_id):
    ok, err = StudentService.delete_student(student_id, user_id=session.get('user_id'))
    if err:
        flash(f"Error deleting student: {err}", 'danger')
    else:
        flash("Student record safely deleted.", 'info')
    return redirect(url_for('students.index'))

