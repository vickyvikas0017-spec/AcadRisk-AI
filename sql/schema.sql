-- ====================================================================
-- AcadRisk AI: Relational Database Schema (MySQL 8.0)
-- 23 Normalized Tables up to 3NF with Referential Integrity & Constraints
-- ====================================================================

CREATE DATABASE IF NOT EXISTS acadrisk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE acadrisk_db;

-- TABLE 1: roles
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 2: users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    account_status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 3: departments
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 4: faculty
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department_id INT NOT NULL,
    faculty_name VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    contact_information VARCHAR(255),
    CONSTRAINT fk_faculty_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_faculty_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 5: students
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NULL,
    department_id INT NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    student_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NULL,
    admission_year INT NOT NULL,
    semester INT NOT NULL,
    contact_information VARCHAR(255),
    CONSTRAINT fk_students_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
    CONSTRAINT fk_students_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE RESTRICT,
    CONSTRAINT chk_semester_range CHECK (semester BETWEEN 1 AND 8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 6: courses
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    course_code VARCHAR(30) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    credits INT NOT NULL,
    description TEXT,
    CONSTRAINT fk_courses_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE RESTRICT,
    CONSTRAINT chk_course_credits CHECK (credits > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 7: semesters
CREATE TABLE IF NOT EXISTS semesters (
    semester_id INT AUTO_INCREMENT PRIMARY KEY,
    semester_name VARCHAR(50) NOT NULL,
    academic_year VARCHAR(30) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 8: academic_calendar
CREATE TABLE IF NOT EXISTS academic_calendar (
    calendar_id INT AUTO_INCREMENT PRIMARY KEY,
    semester_id INT NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    description TEXT,
    CONSTRAINT fk_calendar_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 9: enrollments
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    enrollment_status VARCHAR(20) NOT NULL DEFAULT 'enrolled',
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_course_semester UNIQUE (student_id, course_id, semester_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 10: attendance_sessions
CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NULL,
    course_id INT NOT NULL,
    semester_id INT NOT NULL,
    faculty_id INT NOT NULL,
    session_date DATE NOT NULL,
    session_type VARCHAR(50) NOT NULL DEFAULT 'Lecture',
    CONSTRAINT fk_session_faculty FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id) ON DELETE RESTRICT,
    CONSTRAINT fk_session_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
    CONSTRAINT fk_session_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 11: attendance_records
CREATE TABLE IF NOT EXISTS attendance_records (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    enrollment_id INT NOT NULL,
    attendance_status VARCHAR(20) NOT NULL,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_att_records_session FOREIGN KEY (session_id) REFERENCES attendance_sessions (session_id) ON DELETE CASCADE,
    CONSTRAINT fk_att_records_enrollment FOREIGN KEY (enrollment_id) REFERENCES enrollments (enrollment_id) ON DELETE CASCADE,
    CONSTRAINT uq_session_enrollment UNIQUE (session_id, enrollment_id),
    CONSTRAINT chk_att_status CHECK (attendance_status IN ('Present', 'Absent', 'Late', 'Excused'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 12: assessments
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    semester_id INT NOT NULL,
    assessment_name VARCHAR(100) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    maximum_marks DECIMAL(5,2) NOT NULL,
    assessment_date DATE NOT NULL,
    CONSTRAINT fk_assessments_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
    CONSTRAINT fk_assessments_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE,
    CONSTRAINT chk_assessment_max_marks CHECK (maximum_marks > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 13: marks
CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    enrollment_id INT NOT NULL,
    obtained_marks DECIMAL(5,2) NOT NULL,
    recorded_by INT NULL,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_marks_assessment FOREIGN KEY (assessment_id) REFERENCES assessments (assessment_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_enrollment FOREIGN KEY (enrollment_id) REFERENCES enrollments (enrollment_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_recorded_by FOREIGN KEY (recorded_by) REFERENCES users (user_id) ON DELETE SET NULL,
    CONSTRAINT uq_marks_assessment_enrollment UNIQUE (assessment_id, enrollment_id),
    CONSTRAINT chk_marks_non_negative CHECK (obtained_marks >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 14: academic_history
CREATE TABLE IF NOT EXISTS academic_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    semester_id INT NOT NULL,
    course_id INT NOT NULL,
    final_grade VARCHAR(5) NOT NULL,
    grade_point DECIMAL(4,2) NOT NULL,
    credits INT NOT NULL,
    result_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_history_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
    CONSTRAINT fk_history_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE,
    CONSTRAINT fk_history_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 15: import_batches
CREATE TABLE IF NOT EXISTS import_batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    imported_by INT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    import_type VARCHAR(50) NOT NULL,
    total_records INT NOT NULL DEFAULT 0,
    successful_records INT NOT NULL DEFAULT 0,
    failed_records INT NOT NULL DEFAULT 0,
    import_status VARCHAR(30) NOT NULL DEFAULT 'completed',
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_import_user FOREIGN KEY (imported_by) REFERENCES users (user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 16: import_errors
CREATE TABLE IF NOT EXISTS import_errors (
    error_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    row_number INT NOT NULL,
    error_description TEXT NOT NULL,
    CONSTRAINT fk_errors_batch FOREIGN KEY (batch_id) REFERENCES import_batches (batch_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 17: model_registry
CREATE TABLE IF NOT EXISTS model_registry (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    model_version VARCHAR(30) NOT NULL,
    dataset_source VARCHAR(100) NOT NULL,
    accuracy DECIMAL(6,4) NOT NULL,
    precision_score DECIMAL(6,4) NOT NULL,
    recall DECIMAL(6,4) NOT NULL,
    f1_score DECIMAL(6,4) NOT NULL,
    model_path VARCHAR(255) NOT NULL,
    training_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_status VARCHAR(20) NOT NULL DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 18: prediction_runs
CREATE TABLE IF NOT EXISTS prediction_runs (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    initiated_by INT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completion_time DATETIME NULL,
    total_predictions INT NOT NULL DEFAULT 0,
    run_status VARCHAR(30) NOT NULL DEFAULT 'completed',
    CONSTRAINT fk_runs_model FOREIGN KEY (model_id) REFERENCES model_registry (model_id) ON DELETE RESTRICT,
    CONSTRAINT fk_runs_user FOREIGN KEY (initiated_by) REFERENCES users (user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 19: predictions
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NULL,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester_id INT NOT NULL,
    predicted_marks DECIMAL(5,2) NULL,
    risk_category VARCHAR(20) NOT NULL,
    risk_probability DECIMAL(5,4) NOT NULL,
    prediction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_preds_run FOREIGN KEY (run_id) REFERENCES prediction_runs (run_id) ON DELETE CASCADE,
    CONSTRAINT fk_preds_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
    CONSTRAINT fk_preds_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
    CONSTRAINT fk_preds_semester FOREIGN KEY (semester_id) REFERENCES semesters (semester_id) ON DELETE CASCADE,
    CONSTRAINT chk_pred_risk_category CHECK (risk_category IN ('Low Risk', 'Medium Risk', 'High Risk'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 20: interventions
CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NULL,
    student_id INT NOT NULL,
    faculty_id INT NOT NULL,
    intervention_type VARCHAR(100) NOT NULL,
    intervention_description TEXT NOT NULL,
    follow_up_date DATE NULL,
    intervention_status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    outcome TEXT NULL,
    CONSTRAINT fk_interv_prediction FOREIGN KEY (prediction_id) REFERENCES predictions (prediction_id) ON DELETE SET NULL,
    CONSTRAINT fk_interv_student FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
    CONSTRAINT fk_interv_faculty FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 21: notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    read_status BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 22: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NULL,
    old_values TEXT NULL,
    new_values TEXT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- TABLE 23: risk_thresholds
CREATE TABLE IF NOT EXISTS risk_thresholds (
    threshold_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NULL,
    course_id INT NULL,
    high_risk_threshold DECIMAL(5,2) NOT NULL DEFAULT 40.0,
    medium_risk_threshold DECIMAL(5,2) NOT NULL DEFAULT 60.0,
    low_risk_threshold DECIMAL(5,2) NOT NULL DEFAULT 80.0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_thresh_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE SET NULL,
    CONSTRAINT fk_thresh_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

