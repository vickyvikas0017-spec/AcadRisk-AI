-- ====================================================================
-- AcadRisk AI: Index Definitions for Query Optimization
-- Optimizes frequently filtered, joined, and aggregated columns
-- ====================================================================

USE acadrisk_db;

-- Indexes on students
CREATE INDEX IF NOT EXISTS idx_student_reg ON students (registration_number);
CREATE INDEX IF NOT EXISTS idx_student_dept ON students (department_id);
CREATE INDEX IF NOT EXISTS idx_student_sem ON students (semester);

-- Indexes on courses & faculty
CREATE INDEX IF NOT EXISTS idx_course_dept ON courses (department_id);
CREATE INDEX IF NOT EXISTS idx_faculty_dept ON faculty (department_id);

-- Indexes on enrollments
CREATE INDEX IF NOT EXISTS idx_enrollment_student ON enrollments (student_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_course ON enrollments (course_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_semester ON enrollments (semester_id);

-- Indexes on attendance
CREATE INDEX IF NOT EXISTS idx_att_session_date ON attendance_sessions (session_date);
CREATE INDEX IF NOT EXISTS idx_att_session_course ON attendance_sessions (course_id);
CREATE INDEX IF NOT EXISTS idx_att_rec_status ON attendance_records (attendance_status);

-- Indexes on marks & assessments
CREATE INDEX IF NOT EXISTS idx_assessments_course_sem ON assessments (course_id, semester_id);
CREATE INDEX IF NOT EXISTS idx_marks_enrollment ON marks (enrollment_id);

-- Indexes on predictions & risk monitoring
CREATE INDEX IF NOT EXISTS idx_pred_student ON predictions (student_id);
CREATE INDEX IF NOT EXISTS idx_pred_course ON predictions (course_id);
CREATE INDEX IF NOT EXISTS idx_pred_risk ON predictions (risk_category);
CREATE INDEX IF NOT EXISTS idx_pred_date ON predictions (prediction_date);

-- Indexes on notifications & audit
CREATE INDEX IF NOT EXISTS idx_notif_user_read ON notifications (user_id, read_status);
CREATE INDEX IF NOT EXISTS idx_audit_table_date ON audit_logs (table_name, timestamp);

