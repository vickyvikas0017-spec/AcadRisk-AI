-- ====================================================================
-- AcadRisk AI: Advanced SQL Reports
-- Comprehensive Queries Demonstrating JOINS, AGGREGATES & SUBQUERIES
-- ====================================================================

USE acadrisk_db;

-- 1. DEPARTMENT-WISE STUDENT ACADEMIC PERFORMANCE (Joins + Aggregates)
SELECT 
    d.department_code,
    d.department_name,
    COUNT(DISTINCT s.student_id) AS total_enrolled_students,
    COUNT(DISTINCT e.enrollment_id) AS total_course_registrations,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS dept_average_score,
    ROUND(MIN((m.obtained_marks / a.maximum_marks) * 100), 2) AS lowest_assessment_score,
    ROUND(MAX((m.obtained_marks / a.maximum_marks) * 100), 2) AS highest_assessment_score
FROM departments d
JOIN students s ON d.department_id = s.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN marks m ON e.enrollment_id = m.enrollment_id
JOIN assessments a ON m.assessment_id = a.assessment_id
GROUP BY d.department_code, d.department_name
ORDER BY dept_average_score DESC;

-- 2. STUDENTS PERFORMING BELOW INSTITUTIONAL AVERAGE (Correlated Subquery)
SELECT 
    s.registration_number,
    s.student_name,
    d.department_code,
    ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS student_avg_score
FROM students s
JOIN departments d ON s.department_id = d.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN marks m ON e.enrollment_id = m.enrollment_id
JOIN assessments a ON m.assessment_id = a.assessment_id
GROUP BY s.student_id, s.registration_number, s.student_name, d.department_code
HAVING student_avg_score < (
    -- Subquery: Overall institutional average score
    SELECT AVG((m2.obtained_marks / a2.maximum_marks) * 100)
    FROM marks m2
    JOIN assessments a2 ON m2.assessment_id = a2.assessment_id
)
ORDER BY student_avg_score ASC;

-- 3. STUDENTS WITH CHRONIC ATTENDANCE DEFICIT (< 75%) (Aggregates + Having)
SELECT 
    s.registration_number,
    s.student_name,
    c.course_code,
    c.course_name,
    COUNT(ar.attendance_id) AS total_classes_held,
    SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) AS attended_classes,
    ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) / COUNT(ar.attendance_id)) * 100, 2) AS attendance_pct
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
GROUP BY s.student_id, s.registration_number, s.student_name, c.course_id, c.course_code, c.course_name
HAVING attendance_pct < 75.00
ORDER BY attendance_pct ASC;

-- 4. REPEATED COURSE FAILURES DETECTION (Nested Subquery Analysis)
SELECT 
    s.registration_number,
    s.student_name,
    c.course_code,
    c.course_name,
    COUNT(h.history_id) AS failed_attempt_count
FROM students s
JOIN academic_history h ON s.student_id = h.student_id
JOIN courses c ON h.course_id = c.course_id
WHERE h.result_status = 'Fail'
GROUP BY s.student_id, s.registration_number, s.student_name, c.course_id, c.course_code, c.course_name
HAVING failed_attempt_count >= 1
ORDER BY failed_attempt_count DESC;

-- 5. EARLY WARNING INTERVENTION OUTCOME ANALYSIS (Multi-Table Joins)
SELECT 
    i.intervention_type,
    COUNT(i.intervention_id) AS total_interventions_logged,
    SUM(CASE WHEN i.intervention_status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN i.intervention_status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
    ROUND(AVG(p.risk_probability) * 100, 2) AS average_initial_risk_probability
FROM interventions i
JOIN predictions p ON i.prediction_id = p.prediction_id
GROUP BY i.intervention_type;

