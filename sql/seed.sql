-- ====================================================================
-- AcadRisk AI: Comprehensive Seed Data
-- Realistic Academic Institution Demo Data
-- ====================================================================

USE acadrisk_db;

-- 1. ROLES
INSERT INTO roles (role_id, role_name, description) VALUES
(1, 'ADMIN', 'Institutional Administrator with full privileges over system, models, database and users.'),
(2, 'FACULTY', 'Teaching faculty with access to courses, student attendance, marks, and interventions.'),
(3, 'STUDENT', 'Enrolled student with read-only access to personal grades, attendance, and risk standing.')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- 2. USERS
-- Admin: Admin@123 | Faculty: Faculty@123 | Student: Student@123
INSERT INTO users (user_id, role_id, username, email, password_hash, account_status, created_at) VALUES
(1, 1, 'admin', 'admin@acadrisk.edu', 'scrypt:32768:8:1$xkCHza26FYaW92fs$5ce797162bff9e10c4552b9fbb68516cf87ecdb57fd3bdcd66a4003418ba6bf7b8e662e73df090bcfc443d4505789e2d544313763a8d636c73796ec26cdb59b9', 'active', NOW()),
(2, 2, 'prof_smith', 'smith@acadrisk.edu', 'scrypt:32768:8:1$zUHkzgwrP02NvHla$ecdc32afb257c0d0929f9c2ef15cd78678fbb9934ed779a3a27b7ec927c5264ed153a4df2a9b0afbab845e2a9174685fc241b13486a89073170dc98adba604be', 'active', NOW()),
(3, 2, 'prof_johnson', 'johnson@acadrisk.edu', 'scrypt:32768:8:1$zUHkzgwrP02NvHla$ecdc32afb257c0d0929f9c2ef15cd78678fbb9934ed779a3a27b7ec927c5264ed153a4df2a9b0afbab845e2a9174685fc241b13486a89073170dc98adba604be', 'active', NOW()),
(4, 2, 'prof_patel', 'patel@acadrisk.edu', 'scrypt:32768:8:1$zUHkzgwrP02NvHla$ecdc32afb257c0d0929f9c2ef15cd78678fbb9934ed779a3a27b7ec927c5264ed153a4df2a9b0afbab845e2a9174685fc241b13486a89073170dc98adba604be', 'active', NOW()),
(5, 3, 'john_doe', 'john.doe@acadrisk.edu', 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc', 'active', NOW()),
(6, 3, 'emma_watson', 'emma.watson@acadrisk.edu', 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc', 'active', NOW()),
(7, 3, 'raj_sharma', 'raj.sharma@acadrisk.edu', 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc', 'active', NOW()),
(8, 3, 'priya_verma', 'priya.verma@acadrisk.edu', 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc', 'active', NOW()),
(9, 3, 'alex_miller', 'alex.miller@acadrisk.edu', 'scrypt:32768:8:1$qIrCy5slMNcw1NV3$8adc46352ba5662d9e5088212989c2e8e26d64c97cde9ceee9b58a3b53d47912026430a88e37ef1b2077a075f95f9f8dd44a3b90e6d030a0070267e0dacafebc', 'active', NOW())
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- 3. DEPARTMENTS
INSERT INTO departments (department_id, department_name, department_code, description) VALUES
(1, 'Computer Science and Engineering', 'CSE', 'Focuses on computing theory, algorithms, databases, and AI systems.'),
(2, 'Information Technology', 'IT', 'Specializes in web systems, cloud computing, networks and application engineering.'),
(3, 'Electronics and Communication', 'ECE', 'Covers embedded systems, digital signal processing, and communication networks.'),
(4, 'Mechanical Engineering', 'ME', 'Covers thermodynamics, robotics, mechanics and fluid dynamics.')
ON DUPLICATE KEY UPDATE department_name=VALUES(department_name);

-- 4. FACULTY
INSERT INTO faculty (faculty_id, user_id, department_id, faculty_name, designation, contact_information) VALUES
(1, 2, 1, 'Dr. Alan Smith', 'Professor & Head', '+1-555-0101 | asmith@acadrisk.edu'),
(2, 3, 1, 'Dr. Sarah Johnson', 'Associate Professor', '+1-555-0102 | sjohnson@acadrisk.edu'),
(3, 4, 2, 'Prof. Rajesh Patel', 'Assistant Professor', '+1-555-0103 | rpatel@acadrisk.edu')
ON DUPLICATE KEY UPDATE faculty_name=VALUES(faculty_name);

-- 5. STUDENTS
INSERT INTO students (student_id, user_id, department_id, registration_number, student_name, date_of_birth, admission_year, semester, contact_information) VALUES
(1, 5, 1, 'REG-2023-CS001', 'John Doe', '2004-05-14', 2023, 6, '+1-555-0201 | Block A, Campus Dorms'),
(2, 6, 1, 'REG-2023-CS002', 'Emma Watson', '2004-09-21', 2023, 6, '+1-555-0202 | Block B, Room 204'),
(3, 7, 1, 'REG-2023-CS003', 'Raj Sharma', '2003-12-05', 2023, 6, '+1-555-0203 | Off-campus Apartment 3'),
(4, 8, 2, 'REG-2023-IT001', 'Priya Verma', '2004-02-18', 2023, 6, '+1-555-0204 | Block C, Room 108'),
(5, 9, 2, 'REG-2023-IT002', 'Alex Miller', '2003-08-30', 2023, 6, '+1-555-0205 | Off-campus Residence 12'),
(6, NULL, 1, 'REG-2024-CS010', 'Carlos Santana', '2005-01-15', 2024, 4, '+1-555-0210 | Dorm 4'),
(7, NULL, 1, 'REG-2024-CS011', 'David Kim', '2005-03-22', 2024, 4, '+1-555-0211 | Dorm 4'),
(8, NULL, 3, 'REG-2023-EC001', 'Ananya Gupta', '2004-07-11', 2023, 6, '+1-555-0212 | Dorm 2'),
(9, NULL, 4, 'REG-2024-ME001', 'Liam O Connor', '2005-11-09', 2024, 4, '+1-555-0213 | Dorm 1'),
(10, NULL, 1, 'REG-2022-CS099', 'Vikram Rao', '2002-04-10', 2022, 8, '+1-555-0214 | Off-campus')
ON DUPLICATE KEY UPDATE student_name=VALUES(student_name);

-- 6. COURSES
INSERT INTO courses (course_id, department_id, course_code, course_name, credits, description) VALUES
(1, 1, 'CS-301', 'Database Management Systems', 4, 'Advanced relational DBMS, normalization, indexing, query optimization and transactions.'),
(2, 1, 'CS-302', 'Artificial Intelligence & Machine Learning', 4, 'Supervised learning, deep neural architectures, evaluation metrics, and predictive modeling.'),
(3, 1, 'CS-303', 'Design and Analysis of Algorithms', 4, 'Asymptotic notation, divide-and-conquer, dynamic programming, and greedy algorithms.'),
(4, 2, 'IT-301', 'Web Application Engineering', 3, 'Full-stack client-server architecture, RESTful API design, authentication and security.'),
(5, 3, 'EC-201', 'Digital Signals and Systems', 4, 'Fourier transforms, digital filters, and signal processing hardware architectures.'),
(6, 4, 'ME-101', 'Engineering Mechanics & Dynamics', 3, 'Statics, kinematics, kinetics, and mechanical energy conservation.')
ON DUPLICATE KEY UPDATE course_name=VALUES(course_name);

-- 7. SEMESTERS
INSERT INTO semesters (semester_id, semester_name, academic_year, start_date, end_date, status) VALUES
(1, 'Spring 2026', '2025-2026', '2026-01-05', '2026-05-20', 'active'),
(2, 'Fall 2025', '2025-2026', '2025-08-01', '2025-12-18', 'completed'),
(3, 'Spring 2025', '2024-2025', '2025-01-06', '2025-05-22', 'completed')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- 8. ACADEMIC CALENDAR
INSERT INTO academic_calendar (calendar_id, semester_id, event_name, event_date, description) VALUES
(1, 1, 'Semester Course Enrollment Closes', '2026-01-15', 'Deadline for add/drop course selections.'),
(2, 1, 'Internal Assessment 1 Examination', '2026-02-20', 'First continuous assessment examination period.'),
(3, 1, 'Internal Assessment 2 Examination', '2026-04-05', 'Mid-semester major examination.'),
(4, 1, 'End-Semester Final Examinations', '2026-05-10', 'Comprehensive final university exam.'),
(5, 2, 'Fall 2025 Grade Publication', '2025-12-28', 'Official release of semester grade cards.')
ON DUPLICATE KEY UPDATE event_name=VALUES(event_name);

-- 9. ENROLLMENTS
INSERT INTO enrollments (enrollment_id, student_id, course_id, semester_id, enrollment_date, enrollment_status) VALUES
(1, 1, 1, 1, '2026-01-06', 'enrolled'),
(2, 1, 2, 1, '2026-01-06', 'enrolled'),
(3, 1, 3, 1, '2026-01-06', 'enrolled'),
(4, 2, 1, 1, '2026-01-06', 'enrolled'),
(5, 2, 2, 1, '2026-01-06', 'enrolled'),
(6, 3, 1, 1, '2026-01-06', 'enrolled'),
(7, 3, 2, 1, '2026-01-06', 'enrolled'),
(8, 4, 4, 1, '2026-01-06', 'enrolled'),
(9, 5, 4, 1, '2026-01-06', 'enrolled'),
(10, 6, 1, 1, '2026-01-06', 'enrolled'),
(11, 7, 1, 1, '2026-01-06', 'enrolled'),
(12, 10, 1, 1, '2026-01-06', 'enrolled')
ON DUPLICATE KEY UPDATE enrollment_status=VALUES(enrollment_status);

-- 10. ATTENDANCE SESSIONS
INSERT INTO attendance_sessions (session_id, course_id, semester_id, faculty_id, session_date, session_type) VALUES
(1, 1, 1, 1, '2026-01-10', 'Lecture'),
(2, 1, 1, 1, '2026-01-17', 'Lecture'),
(3, 1, 1, 1, '2026-01-24', 'Lab Session'),
(4, 1, 1, 1, '2026-01-31', 'Lecture'),
(5, 1, 1, 1, '2026-02-07', 'Lecture'),
(6, 2, 1, 2, '2026-01-12', 'Lecture'),
(7, 2, 1, 2, '2026-01-19', 'Lab Session'),
(8, 2, 1, 2, '2026-01-26', 'Lecture'),
(9, 4, 1, 3, '2026-01-14', 'Lecture'),
(10, 4, 1, 3, '2026-01-21', 'Lab Session')
ON DUPLICATE KEY UPDATE session_type=VALUES(session_type);

-- 11. ATTENDANCE RECORDS (High attendance for Emma/John, Low attendance for Raj/Vikram)
INSERT INTO attendance_records (attendance_id, session_id, enrollment_id, attendance_status, recorded_at) VALUES
(1, 1, 1, 'Present', NOW()),
(2, 2, 1, 'Present', NOW()),
(3, 3, 1, 'Present', NOW()),
(4, 4, 1, 'Present', NOW()),
(5, 5, 1, 'Late', NOW()),
(6, 1, 4, 'Present', NOW()),
(7, 2, 4, 'Present', NOW()),
(8, 3, 4, 'Present', NOW()),
(9, 4, 4, 'Present', NOW()),
(10, 5, 4, 'Present', NOW()),
(11, 1, 6, 'Absent', NOW()),
(12, 2, 6, 'Absent', NOW()),
(13, 3, 6, 'Present', NOW()),
(14, 4, 6, 'Absent', NOW()),
(15, 5, 6, 'Absent', NOW()),
(16, 1, 12, 'Absent', NOW()),
(17, 2, 12, 'Absent', NOW()),
(18, 3, 12, 'Absent', NOW()),
(19, 4, 12, 'Present', NOW()),
(20, 5, 12, 'Absent', NOW())
ON DUPLICATE KEY UPDATE attendance_status=VALUES(attendance_status);

-- 12. ASSESSMENTS
INSERT INTO assessments (assessment_id, course_id, semester_id, assessment_name, assessment_type, maximum_marks, assessment_date) VALUES
(1, 1, 1, 'Internal Assessment 1', 'Internal 1', 25.00, '2026-02-15'),
(2, 1, 1, 'Internal Assessment 2 (Mid-Term)', 'Internal 2', 25.00, '2026-03-25'),
(3, 1, 1, 'SQL Practical Lab Examination', 'Practical', 20.00, '2026-04-10'),
(4, 2, 1, 'Machine Learning Quiz & Assignment', 'Assignment', 20.00, '2026-02-18'),
(5, 2, 1, 'Mid-Semester Examination', 'Internal 2', 30.00, '2026-03-28'),
(6, 4, 1, 'Web Tech Mid-Semester Project', 'Internal 2', 30.00, '2026-03-20')
ON DUPLICATE KEY UPDATE assessment_name=VALUES(assessment_name);

-- 13. MARKS
INSERT INTO marks (mark_id, assessment_id, enrollment_id, obtained_marks, recorded_by, recorded_at) VALUES
(1, 1, 1, 21.50, 2, NOW()),
(2, 2, 1, 20.00, 2, NOW()),
(3, 3, 1, 18.00, 2, NOW()),
(4, 1, 4, 24.00, 2, NOW()),
(5, 2, 4, 23.50, 2, NOW()),
(6, 3, 4, 19.50, 2, NOW()),
(7, 1, 6, 8.50, 2, NOW()),
(8, 2, 6, 7.00, 2, NOW()),
(9, 3, 6, 9.00, 2, NOW()),
(10, 1, 12, 5.00, 2, NOW()),
(11, 2, 12, 6.00, 2, NOW()),
(12, 3, 12, 7.50, 2, NOW())
ON DUPLICATE KEY UPDATE obtained_marks=VALUES(obtained_marks);

-- 14. ACADEMIC HISTORY
INSERT INTO academic_history (history_id, student_id, semester_id, course_id, final_grade, grade_point, credits, result_status) VALUES
(1, 1, 2, 1, 'A', 8.50, 4, 'Pass'),
(2, 1, 2, 3, 'A+', 9.00, 4, 'Pass'),
(3, 2, 2, 1, 'A+', 9.80, 4, 'Pass'),
(4, 2, 2, 3, 'A+', 9.50, 4, 'Pass'),
(5, 3, 2, 1, 'D', 4.50, 4, 'Pass'),
(6, 3, 2, 3, 'F', 0.00, 4, 'Fail'),
(7, 10, 2, 3, 'F', 0.00, 4, 'Fail'),
(8, 10, 3, 3, 'F', 0.00, 4, 'Fail')
ON DUPLICATE KEY UPDATE grade_point=VALUES(grade_point);

-- 15. RISK THRESHOLDS
INSERT INTO risk_thresholds (threshold_id, department_id, course_id, high_risk_threshold, medium_risk_threshold, low_risk_threshold, updated_at) VALUES
(1, NULL, NULL, 40.00, 60.00, 80.00, NOW()),
(2, 1, 1, 45.00, 65.00, 80.00, NOW()),
(3, 1, 2, 40.00, 60.00, 80.00, NOW()),
(4, 2, 4, 40.00, 60.00, 80.00, NOW())
ON DUPLICATE KEY UPDATE high_risk_threshold=VALUES(high_risk_threshold);

