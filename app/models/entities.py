from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Numeric,
    ForeignKey, Boolean, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship('User', back_populates='role')

    def to_dict(self):
        return {'role_id': self.role_id, 'role_name': self.role_name, 'description': self.description}

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.role_id', ondelete='RESTRICT'), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(String(20), default='active', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    role = relationship('Role', back_populates='users')
    faculty_profile = relationship('Faculty', back_populates='user', uselist=False)
    student_profile = relationship('Student', back_populates='user', uselist=False)
    notifications = relationship('Notification', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'role_id': self.role_id,
            'role_name': self.role.role_name if self.role else None,
            'username': self.username,
            'email': self.email,
            'account_status': self.account_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Department(Base):
    __tablename__ = 'departments'
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), unique=True, nullable=False)
    department_code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    faculty_members = relationship('Faculty', back_populates='department')
    students = relationship('Student', back_populates='department')
    courses = relationship('Course', back_populates='department')

    def to_dict(self):
        return {
            'department_id': self.department_id,
            'department_name': self.department_name,
            'department_code': self.department_code,
            'description': self.description
        }

class Faculty(Base):
    __tablename__ = 'faculty'
    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='RESTRICT'), nullable=False, index=True)
    faculty_name = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    contact_information = Column(String(255), nullable=True)

    user = relationship('User', back_populates='faculty_profile')
    department = relationship('Department', back_populates='faculty_members')
    attendance_sessions = relationship('AttendanceSession', back_populates='faculty')
    interventions = relationship('Intervention', back_populates='faculty')

    def to_dict(self):
        return {
            'faculty_id': self.faculty_id,
            'user_id': self.user_id,
            'department_id': self.department_id,
            'department_name': self.department.department_name if self.department else None,
            'faculty_name': self.faculty_name,
            'designation': self.designation,
            'contact_information': self.contact_information
        }

class Student(Base):
    __tablename__ = 'students'
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=True)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='RESTRICT'), nullable=False, index=True)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    student_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    admission_year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    contact_information = Column(String(255), nullable=True)

    user = relationship('User', back_populates='student_profile')
    department = relationship('Department', back_populates='students')
    enrollments = relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    academic_histories = relationship('AcademicHistory', back_populates='student')
    predictions = relationship('Prediction', back_populates='student')
    interventions = relationship('Intervention', back_populates='student')

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'department_id': self.department_id,
            'department_name': self.department.department_name if self.department else None,
            'registration_number': self.registration_number,
            'student_name': self.student_name,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d') if self.date_of_birth else None,
            'admission_year': self.admission_year,
            'semester': self.semester,
            'contact_information': self.contact_information
        }

class Course(Base):
    __tablename__ = 'courses'
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='RESTRICT'), nullable=False, index=True)
    course_code = Column(String(30), unique=True, nullable=False, index=True)
    course_name = Column(String(150), nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    department = relationship('Department', back_populates='courses')
    enrollments = relationship('Enrollment', back_populates='course')
    assessments = relationship('Assessment', back_populates='course')
    academic_histories = relationship('AcademicHistory', back_populates='course')
    predictions = relationship('Prediction', back_populates='course')

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'department_id': self.department_id,
            'department_name': self.department.department_name if self.department else None,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'credits': self.credits,
            'description': self.description
        }

class Semester(Base):
    __tablename__ = 'semesters'
    semester_id = Column(Integer, primary_key=True, autoincrement=True)
    semester_name = Column(String(50), nullable=False)
    academic_year = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default='active', nullable=False)

    enrollments = relationship('Enrollment', back_populates='semester')
    assessments = relationship('Assessment', back_populates='semester')
    calendar_events = relationship('AcademicCalendar', back_populates='semester')
    predictions = relationship('Prediction', back_populates='semester')

    def to_dict(self):
        return {
            'semester_id': self.semester_id,
            'semester_name': self.semester_name,
            'academic_year': self.academic_year,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'status': self.status
        }

class AcademicCalendar(Base):
    __tablename__ = 'academic_calendar'
    calendar_id = Column(Integer, primary_key=True, autoincrement=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    event_name = Column(String(100), nullable=False)
    event_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    semester = relationship('Semester', back_populates='calendar_events')

    def to_dict(self):
        return {
            'calendar_id': self.calendar_id,
            'semester_id': self.semester_id,
            'event_name': self.event_name,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'description': self.description
        }

class Enrollment(Base):
    __tablename__ = 'enrollments'
    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    enrollment_date = Column(Date, default=date.today, nullable=False)
    enrollment_status = Column(String(20), default='enrolled', nullable=False)

    student = relationship('Student', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    semester = relationship('Semester', back_populates='enrollments')
    attendance_records = relationship('AttendanceRecord', back_populates='enrollment', cascade='all, delete-orphan')
    marks = relationship('Mark', back_populates='enrollment', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', 'semester_id', name='uq_student_course_semester'),
        Index('idx_enrollment_lookup', 'student_id', 'course_id', 'semester_id')
    )

    def to_dict(self):
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else None,
            'registration_number': self.student.registration_number if self.student else None,
            'course_id': self.course_id,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.course_name if self.course else None,
            'semester_id': self.semester_id,
            'semester_name': self.semester.semester_name if self.semester else None,
            'enrollment_date': self.enrollment_date.strftime('%Y-%m-%d') if self.enrollment_date else None,
            'enrollment_status': self.enrollment_status
        }

class AttendanceSession(Base):
    __tablename__ = 'attendance_sessions'
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollments.enrollment_id', ondelete='SET NULL'), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='RESTRICT'), nullable=False, index=True)
    session_date = Column(Date, default=date.today, nullable=False, index=True)
    session_type = Column(String(50), default='Lecture', nullable=False)

    faculty = relationship('Faculty', back_populates='attendance_sessions')
    course = relationship('Course')
    semester = relationship('Semester')
    records = relationship('AttendanceRecord', back_populates='session', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.faculty_name if self.faculty else None,
            'session_date': self.session_date.strftime('%Y-%m-%d') if self.session_date else None,
            'session_type': self.session_type
        }

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('attendance_sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    enrollment_id = Column(Integer, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False, index=True)
    attendance_status = Column(String(20), nullable=False)  # 'Present', 'Absent', 'Late', 'Excused'
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship('AttendanceSession', back_populates='records')
    enrollment = relationship('Enrollment', back_populates='attendance_records')

    __table_args__ = (
        UniqueConstraint('session_id', 'enrollment_id', name='uq_session_enrollment'),
        CheckConstraint("attendance_status IN ('Present', 'Absent', 'Late', 'Excused')", name='chk_attendance_status'),
        Index('idx_att_record_status', 'attendance_status')
    )

    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'session_id': self.session_id,
            'enrollment_id': self.enrollment_id,
            'student_name': self.enrollment.student.student_name if self.enrollment and self.enrollment.student else None,
            'registration_number': self.enrollment.student.registration_number if self.enrollment and self.enrollment.student else None,
            'attendance_status': self.attendance_status,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if self.recorded_at else None
        }

class Assessment(Base):
    __tablename__ = 'assessments'
    assessment_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_name = Column(String(100), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # 'Internal 1', 'Internal 2', 'Assignment', 'Practical', 'Final Exam'
    maximum_marks = Column(Numeric(5, 2), nullable=False)
    assessment_date = Column(Date, nullable=False)

    course = relationship('Course', back_populates='assessments')
    semester = relationship('Semester', back_populates='assessments')
    marks = relationship('Mark', back_populates='assessment', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('maximum_marks > 0', name='chk_max_marks_positive'),
    )

    def to_dict(self):
        return {
            'assessment_id': self.assessment_id,
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else None,
            'semester_id': self.semester_id,
            'semester_name': self.semester.semester_name if self.semester else None,
            'assessment_name': self.assessment_name,
            'assessment_type': self.assessment_type,
            'maximum_marks': float(self.maximum_marks) if self.maximum_marks else 0.0,
            'assessment_date': self.assessment_date.strftime('%Y-%m-%d') if self.assessment_date else None
        }

class Mark(Base):
    __tablename__ = 'marks'
    mark_id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey('assessments.assessment_id', ondelete='CASCADE'), nullable=False, index=True)
    enrollment_id = Column(Integer, ForeignKey('enrollments.enrollment_id', ondelete='CASCADE'), nullable=False, index=True)
    obtained_marks = Column(Numeric(5, 2), nullable=False)
    recorded_by = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assessment = relationship('Assessment', back_populates='marks')
    enrollment = relationship('Enrollment', back_populates='marks')
    recorded_by_user = relationship('User')

    __table_args__ = (
        UniqueConstraint('assessment_id', 'enrollment_id', name='uq_assessment_enrollment'),
        CheckConstraint('obtained_marks >= 0', name='chk_obtained_marks_non_negative'),
        Index('idx_marks_enrollment', 'enrollment_id')
    )

    def to_dict(self):
        return {
            'mark_id': self.mark_id,
            'assessment_id': self.assessment_id,
            'assessment_name': self.assessment.assessment_name if self.assessment else None,
            'maximum_marks': float(self.assessment.maximum_marks) if self.assessment else None,
            'enrollment_id': self.enrollment_id,
            'student_name': self.enrollment.student.student_name if self.enrollment and self.enrollment.student else None,
            'registration_number': self.enrollment.student.registration_number if self.enrollment and self.enrollment.student else None,
            'obtained_marks': float(self.obtained_marks) if self.obtained_marks is not None else 0.0,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if self.recorded_at else None
        }

class AcademicHistory(Base):
    __tablename__ = 'academic_history'
    history_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    final_grade = Column(String(5), nullable=False)
    grade_point = Column(Numeric(4, 2), nullable=False)
    credits = Column(Integer, nullable=False)
    result_status = Column(String(20), nullable=False)  # 'Pass', 'Fail'

    student = relationship('Student', back_populates='academic_histories')
    semester = relationship('Semester')
    course = relationship('Course', back_populates='academic_histories')

    def to_dict(self):
        return {
            'history_id': self.history_id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else None,
            'course_id': self.course_id,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.course_name if self.course else None,
            'semester_id': self.semester_id,
            'final_grade': self.final_grade,
            'grade_point': float(self.grade_point) if self.grade_point else 0.0,
            'credits': self.credits,
            'result_status': self.result_status
        }

class ImportBatch(Base):
    __tablename__ = 'import_batches'
    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    imported_by = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    import_type = Column(String(50), nullable=False)  # 'students', 'attendance', 'marks'
    total_records = Column(Integer, default=0, nullable=False)
    successful_records = Column(Integer, default=0, nullable=False)
    failed_records = Column(Integer, default=0, nullable=False)
    import_status = Column(String(30), default='completed', nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship('User')
    errors = relationship('ImportError', back_populates='batch', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'batch_id': self.batch_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'import_type': self.import_type,
            'total_records': self.total_records,
            'successful_records': self.successful_records,
            'failed_records': self.failed_records,
            'import_status': self.import_status,
            'imported_at': self.imported_at.strftime('%Y-%m-%d %H:%M:%S') if self.imported_at else None
        }

class ImportError(Base):
    __tablename__ = 'import_errors'
    error_id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey('import_batches.batch_id', ondelete='CASCADE'), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    error_description = Column(Text, nullable=False)

    batch = relationship('ImportBatch', back_populates='errors')

    def to_dict(self):
        return {
            'error_id': self.error_id,
            'batch_id': self.batch_id,
            'row_number': self.row_number,
            'error_description': self.error_description
        }

class ModelRegistry(Base):
    __tablename__ = 'model_registry'
    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    algorithm = Column(String(100), nullable=False)
    model_version = Column(String(30), nullable=False)
    dataset_source = Column(String(100), nullable=False)
    accuracy = Column(Numeric(6, 4), nullable=False)
    precision = Column(Numeric(6, 4), nullable=False)
    recall = Column(Numeric(6, 4), nullable=False)
    f1_score = Column(Numeric(6, 4), nullable=False)
    model_path = Column(String(255), nullable=False)
    training_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_status = Column(String(20), default='active', nullable=False)

    runs = relationship('PredictionRun', back_populates='model')

    def to_dict(self):
        return {
            'model_id': self.model_id,
            'model_name': self.model_name,
            'algorithm': self.algorithm,
            'model_version': self.model_version,
            'dataset_source': self.dataset_source,
            'accuracy': float(self.accuracy) if self.accuracy is not None else 0.0,
            'precision': float(self.precision) if self.precision is not None else 0.0,
            'recall': float(self.recall) if self.recall is not None else 0.0,
            'f1_score': float(self.f1_score) if self.f1_score is not None else 0.0,
            'model_path': self.model_path,
            'training_date': self.training_date.strftime('%Y-%m-%d %H:%M:%S') if self.training_date else None,
            'model_status': self.model_status
        }

class PredictionRun(Base):
    __tablename__ = 'prediction_runs'
    run_id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('model_registry.model_id', ondelete='RESTRICT'), nullable=False, index=True)
    initiated_by = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    completion_time = Column(DateTime, nullable=True)
    total_predictions = Column(Integer, default=0, nullable=False)
    run_status = Column(String(30), default='completed', nullable=False)

    model = relationship('ModelRegistry', back_populates='runs')
    predictions = relationship('Prediction', back_populates='run', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'run_id': self.run_id,
            'model_id': self.model_id,
            'model_name': self.model.model_name if self.model else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'completion_time': self.completion_time.strftime('%Y-%m-%d %H:%M:%S') if self.completion_time else None,
            'total_predictions': self.total_predictions,
            'run_status': self.run_status
        }

class Prediction(Base):
    __tablename__ = 'predictions'
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey('prediction_runs.run_id', ondelete='CASCADE'), nullable=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='CASCADE'), nullable=False, index=True)
    predicted_marks = Column(Numeric(5, 2), nullable=True)
    risk_category = Column(String(20), nullable=False)  # 'Low Risk', 'Medium Risk', 'High Risk'
    risk_probability = Column(Numeric(5, 4), nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    run = relationship('PredictionRun', back_populates='predictions')
    student = relationship('Student', back_populates='predictions')
    course = relationship('Course', back_populates='predictions')
    semester = relationship('Semester', back_populates='predictions')
    interventions = relationship('Intervention', back_populates='prediction')

    __table_args__ = (
        CheckConstraint("risk_category IN ('Low Risk', 'Medium Risk', 'High Risk')", name='chk_risk_category'),
        Index('idx_pred_student_risk', 'student_id', 'risk_category')
    )

    def to_dict(self):
        return {
            'prediction_id': self.prediction_id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else None,
            'registration_number': self.student.registration_number if self.student else None,
            'course_id': self.course_id,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.course_name if self.course else None,
            'semester_id': self.semester_id,
            'predicted_marks': float(self.predicted_marks) if self.predicted_marks is not None else 0.0,
            'risk_category': self.risk_category,
            'risk_probability': float(self.risk_probability) if self.risk_probability is not None else 0.0,
            'prediction_date': self.prediction_date.strftime('%Y-%m-%d %H:%M:%S') if self.prediction_date else None
        }

class Intervention(Base):
    __tablename__ = 'interventions'
    intervention_id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey('predictions.prediction_id', ondelete='SET NULL'), nullable=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, index=True)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='RESTRICT'), nullable=False, index=True)
    intervention_type = Column(String(100), nullable=False)  # 'Academic Counselling', 'Extra Classes', 'Assignment Support', 'Attendance Follow-up', 'Mentoring'
    intervention_description = Column(Text, nullable=False)
    follow_up_date = Column(Date, nullable=True)
    intervention_status = Column(String(30), default='Pending', nullable=False)  # 'Pending', 'In Progress', 'Completed', 'Escalated'
    outcome = Column(Text, nullable=True)

    prediction = relationship('Prediction', back_populates='interventions')
    student = relationship('Student', back_populates='interventions')
    faculty = relationship('Faculty', back_populates='interventions')

    def to_dict(self):
        return {
            'intervention_id': self.intervention_id,
            'prediction_id': self.prediction_id,
            'student_id': self.student_id,
            'student_name': self.student.student_name if self.student else None,
            'registration_number': self.student.registration_number if self.student else None,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.faculty_name if self.faculty else None,
            'intervention_type': self.intervention_type,
            'intervention_description': self.intervention_description,
            'follow_up_date': self.follow_up_date.strftime('%Y-%m-%d') if self.follow_up_date else None,
            'intervention_status': self.intervention_status,
            'outcome': self.outcome
        }

class Notification(Base):
    __tablename__ = 'notifications'
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    notification_type = Column(String(50), nullable=False)  # 'High Risk Alert', 'Attendance Warning', 'Marks Recorded', 'General'
    message = Column(Text, nullable=False)
    read_status = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'message': self.message,
            'read_status': self.read_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True, index=True)
    action_type = Column(String(50), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'IMPORT'
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship('User', back_populates='audit_logs')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'action_type': self.action_type,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

class RiskThreshold(Base):
    __tablename__ = 'risk_thresholds'
    threshold_id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='SET NULL'), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='SET NULL'), nullable=True)
    high_risk_threshold = Column(Numeric(5, 2), default=40.0, nullable=False)
    medium_risk_threshold = Column(Numeric(5, 2), default=60.0, nullable=False)
    low_risk_threshold = Column(Numeric(5, 2), default=80.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship('Department')
    course = relationship('Course')

    def to_dict(self):
        return {
            'threshold_id': self.threshold_id,
            'department_id': self.department_id,
            'department_name': self.department.department_name if self.department else 'Global Default',
            'course_id': self.course_id,
            'course_name': self.course.course_name if self.course else 'All Courses',
            'high_risk_threshold': float(self.high_risk_threshold),
            'medium_risk_threshold': float(self.medium_risk_threshold),
            'low_risk_threshold': float(self.low_risk_threshold),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

