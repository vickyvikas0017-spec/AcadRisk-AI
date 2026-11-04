from flask import Blueprint, jsonify, request
from app.services.student_service import StudentService
from app.services.prediction_service import PredictionService
from app.services.dashboard_service import DashboardService
from app.services.attendance_service import AttendanceService
from app.database.connection import db_manager

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database_connected': db_manager.is_connected,
        'dialect': db_manager.active_dialect,
        'is_fallback': (db_manager.active_dialect == 'sqlite')
    })

@api_bp.route('/dashboard/summary')
def dashboard_summary():
    data = DashboardService.get_dashboard_summary()
    return jsonify(data)

@api_bp.route('/students')
def get_students():
    q = request.args.get('q')
    dept = request.args.get('dept', type=int)
    students, count = StudentService.get_students(search_query=q, department_id=dept)
    return jsonify({'total': count, 'students': students})

@api_bp.route('/predict', methods=['POST'])
def run_prediction():
    payload = request.get_json(silent=True) or {}
    student_id = payload.get('student_id')
    course_id = payload.get('course_id')
    semester_id = payload.get('semester_id')

    if not all([student_id, course_id, semester_id]):
        return jsonify({'success': False, 'error': 'student_id, course_id, and semester_id are required fields.'}), 400

    res = PredictionService.run_prediction(int(student_id), int(course_id), int(semester_id))
    return jsonify(res)

@api_bp.route('/attendance/student/<int:student_id>/course/<int:course_id>')
def student_attendance(student_id, course_id):
    att = AttendanceService.get_student_course_attendance(student_id, course_id)
    return jsonify(att)

