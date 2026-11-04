-- ====================================================================
-- AcadRisk AI: MySQL Database Views
-- 6 Views for Real-Time Academic Intelligence and Reporting
-- ====================================================================

USE acadrisk_db;

-- VIEW 1: v_student_academic_summary
-- Summarizes overall assessment performance, average marks, and credits earned per student
CREATE OR REPLACE VIEW v_student_academic_summary AS
SELECT 
    s.student_id,
    s.registration_number,
    s.student_name,
    d.department_name,
    s.semester,
    COUNT(DISTINCT e.course_id) AS total_enrolled_courses,
    COUNT(DISTINCT m.mark_id) AS total_assessments_taken,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS overall_marks_percentage,
    COALESCE(SUM(h.credits), 0) AS total_credits_completed,
    ROUND(AVG(h.grade_point), 2) AS cumulative_gpa
FROM students s
JOIN departments d ON s.department_id = d.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN marks m ON e.enrollment_id = m.enrollment_id
LEFT JOIN assessments a ON m.assessment_id = a.assessment_id
LEFT JOIN academic_history h ON s.student_id = h.student_id
GROUP BY s.student_id, s.registration_number, s.student_name, d.department_name, s.semester;

-- VIEW 2: v_student_attendance_summary
-- Calculates attendance sessions, presents, absents, and percentage per student & course
CREATE OR REPLACE VIEW v_student_attendance_summary AS
SELECT 
    s.student_id,
    s.registration_number,
    s.student_name,
    c.course_id,
    c.course_code,
    c.course_name,
    sem.semester_name,
    COUNT(ar.attendance_id) AS total_sessions,
    SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN ar.attendance_status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN ar.attendance_status = 'Late' THEN 1 ELSE 0 END) AS late_count,
    SUM(CASE WHEN ar.attendance_status = 'Excused' THEN 1 ELSE 0 END) AS excused_count,
    ROUND(
        (SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(ar.attendance_id), 0)) * 100, 
        2
    ) AS attendance_percentage
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN semesters sem ON e.semester_id = sem.semester_id
LEFT JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
GROUP BY s.student_id, s.registration_number, s.student_name, c.course_id, c.course_code, c.course_name, sem.semester_name;

-- VIEW 3: v_course_performance
-- Analyzes course-level statistics: enrollments, average marks, min/max marks, pass rate
CREATE OR REPLACE VIEW v_course_performance AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    d.department_name,
    c.credits,
    COUNT(DISTINCT e.student_id) AS total_students_enrolled,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS average_course_score,
    ROUND(MIN((m.obtained_marks / a.maximum_marks) * 100), 2) AS min_course_score,
    ROUND(MAX((m.obtained_marks / a.maximum_marks) * 100), 2) AS max_course_score,
    COUNT(CASE WHEN (m.obtained_marks / a.maximum_marks) * 100 < 40 THEN 1 END) AS total_failing_marks_count
FROM courses c
JOIN departments d ON c.department_id = d.department_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
LEFT JOIN assessments a ON c.course_id = a.course_id
LEFT JOIN marks m ON a.assessment_id = m.assessment_id AND e.enrollment_id = m.enrollment_id
GROUP BY c.course_id, c.course_code, c.course_name, d.department_name, c.credits;

-- VIEW 4: v_department_performance
-- Department-wide aggregation of students, faculty, courses, and overall average performance
CREATE OR REPLACE VIEW v_department_performance AS
SELECT 
    d.department_id,
    d.department_code,
    d.department_name,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT f.faculty_id) AS total_faculty,
    COUNT(DISTINCT c.course_id) AS total_courses,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS department_average_score,
    COUNT(DISTINCT CASE WHEN p.risk_category = 'High Risk' THEN p.student_id END) AS high_risk_students_count
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
LEFT JOIN faculty f ON d.department_id = f.department_id
LEFT JOIN courses c ON d.department_id = c.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN marks m ON e.enrollment_id = m.enrollment_id
LEFT JOIN assessments a ON m.assessment_id = a.assessment_id
LEFT JOIN predictions p ON s.student_id = p.student_id
GROUP BY d.department_id, d.department_code, d.department_name;

-- VIEW 5: v_at_risk_students
-- Identifies students with recent High or Medium Risk predictions, low attendance, and failing grades
CREATE OR REPLACE VIEW v_at_risk_students AS
SELECT 
    p.prediction_id,
    s.student_id,
    s.registration_number,
    s.student_name,
    d.department_name,
    c.course_code,
    c.course_name,
    p.risk_category,
    p.risk_probability,
    p.predicted_marks,
    p.prediction_date,
    COALESCE(att.attendance_percentage, 0.0) AS current_attendance_pct,
    COUNT(DISTINCT i.intervention_id) AS intervention_count
FROM predictions p
JOIN students s ON p.student_id = s.student_id
JOIN departments d ON s.department_id = d.department_id
JOIN courses c ON p.course_id = c.course_id
LEFT JOIN (
    SELECT 
        e.student_id, 
        e.course_id,
        ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(ar.attendance_id), 0)) * 100, 2) AS attendance_percentage
    FROM enrollments e
    JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
    GROUP BY e.student_id, e.course_id
) att ON s.student_id = att.student_id AND c.course_id = att.course_id
LEFT JOIN interventions i ON p.prediction_id = i.prediction_id
WHERE p.risk_category IN ('High Risk', 'Medium Risk')
GROUP BY p.prediction_id, s.student_id, s.registration_number, s.student_name, d.department_name, c.course_code, c.course_name, p.risk_category, p.risk_probability, p.predicted_marks, p.prediction_date, att.attendance_percentage;

-- VIEW 6: v_semester_performance
-- Analyzes semester trends across all courses, students, and risk rates
CREATE OR REPLACE VIEW v_semester_performance AS
SELECT 
    sem.semester_id,
    sem.semester_name,
    sem.academic_year,
    sem.status,
    COUNT(DISTINCT e.student_id) AS active_students,
    COUNT(DISTINCT e.course_id) AS courses_offered,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS semester_average_score,
    COUNT(DISTINCT CASE WHEN p.risk_category = 'High Risk' THEN p.student_id END) AS high_risk_student_count
FROM semesters sem
LEFT JOIN enrollments e ON sem.semester_id = e.semester_id
LEFT JOIN assessments a ON sem.semester_id = a.semester_id
LEFT JOIN marks m ON a.assessment_id = m.assessment_id AND e.enrollment_id = m.enrollment_id
LEFT JOIN predictions p ON sem.semester_id = p.semester_id
GROUP BY sem.semester_id, sem.semester_name, sem.academic_year, sem.status;

