-- ====================================================================
-- AcadRisk AI: MySQL Stored Procedures
-- Encapsulates Core Business Logic in the Database Tier
-- ====================================================================

USE acadrisk_db;

DROP PROCEDURE IF EXISTS sp_calculate_attendance;
DROP PROCEDURE IF EXISTS sp_generate_student_summary;
DROP PROCEDURE IF EXISTS sp_get_high_risk_students;
DROP PROCEDURE IF EXISTS sp_generate_semester_report;

DELIMITER //

-- PROCEDURE 1: sp_calculate_attendance
-- Calculates attendance percentage for a given student and course
CREATE PROCEDURE sp_calculate_attendance(
    IN in_student_id INT,
    IN in_course_id INT,
    OUT out_percentage DECIMAL(5,2)
)
BEGIN
    DECLARE total_count INT DEFAULT 0;
    DECLARE present_count INT DEFAULT 0;

    SELECT COUNT(ar.attendance_id),
           SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END)
    INTO total_count, present_count
    FROM enrollments e
    JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
    WHERE e.student_id = in_student_id 
      AND (in_course_id IS NULL OR e.course_id = in_course_id);

    IF total_count > 0 THEN
        SET out_percentage = ROUND((present_count / total_count) * 100, 2);
    ELSE
        SET out_percentage = 0.00;
    END IF;
END //

-- PROCEDURE 2: sp_generate_student_summary
-- Generates a 360-degree comprehensive academic summary for a specific student
CREATE PROCEDURE sp_generate_student_summary(
    IN in_student_id INT
)
BEGIN
    -- Student Profile & Enrollment Details
    SELECT 
        s.student_id,
        s.registration_number,
        s.student_name,
        d.department_name,
        s.semester,
        s.admission_year,
        s.contact_information
    FROM students s
    JOIN departments d ON s.department_id = d.department_id
    WHERE s.student_id = in_student_id;

    -- Course Wise Marks & Attendance Breakdown
    SELECT 
        c.course_code,
        c.course_name,
        c.credits,
        COUNT(DISTINCT a.assessment_id) AS assessments_count,
        ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS average_score,
        ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(ar.attendance_id), 0)) * 100, 2) AS course_attendance_pct
    FROM enrollments e
    JOIN courses c ON e.course_id = c.course_id
    LEFT JOIN assessments a ON c.course_id = a.course_id
    LEFT JOIN marks m ON a.assessment_id = m.assessment_id AND e.enrollment_id = m.enrollment_id
    LEFT JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
    WHERE e.student_id = in_student_id
    GROUP BY c.course_code, c.course_name, c.credits;

    -- Predictions & Active Risk Assessment
    SELECT 
        p.prediction_id,
        c.course_code,
        p.risk_category,
        p.risk_probability,
        p.predicted_marks,
        p.prediction_date
    FROM predictions p
    JOIN courses c ON p.course_id = c.course_id
    WHERE p.student_id = in_student_id
    ORDER BY p.prediction_date DESC;
END //

-- PROCEDURE 3: sp_get_high_risk_students
-- Retrieves all students categorized as High Risk filtered optionally by Department and Semester
CREATE PROCEDURE sp_get_high_risk_students(
    IN in_department_id INT,
    IN in_semester_id INT
)
BEGIN
    SELECT 
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
        COUNT(i.intervention_id) AS total_interventions
    FROM predictions p
    JOIN students s ON p.student_id = s.student_id
    JOIN departments d ON s.department_id = d.department_id
    JOIN courses c ON p.course_id = c.course_id
    LEFT JOIN interventions i ON p.prediction_id = i.prediction_id
    WHERE p.risk_category = 'High Risk'
      AND (in_department_id IS NULL OR s.department_id = in_department_id)
      AND (in_semester_id IS NULL OR p.semester_id = in_semester_id)
    GROUP BY s.student_id, s.registration_number, s.student_name, d.department_name, c.course_code, c.course_name, p.risk_category, p.risk_probability, p.predicted_marks, p.prediction_date
    ORDER BY p.risk_probability DESC, p.prediction_date DESC;
END //

-- PROCEDURE 4: sp_generate_semester_report
-- Aggregates performance, course averages, attendance rates, and risk statistics for a semester
CREATE PROCEDURE sp_generate_semester_report(
    IN in_semester_id INT
)
BEGIN
    SELECT 
        sem.semester_name,
        sem.academic_year,
        c.course_code,
        c.course_name,
        COUNT(DISTINCT e.student_id) AS enrolled_students,
        ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS average_marks_percentage,
        ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(ar.attendance_id), 0)) * 100, 2) AS avg_attendance_pct,
        COUNT(DISTINCT CASE WHEN p.risk_category = 'High Risk' THEN p.student_id END) AS high_risk_count
    FROM semesters sem
    JOIN enrollments e ON sem.semester_id = e.semester_id
    JOIN courses c ON e.course_id = c.course_id
    LEFT JOIN assessments a ON c.course_id = a.course_id AND sem.semester_id = a.semester_id
    LEFT JOIN marks m ON a.assessment_id = m.assessment_id AND e.enrollment_id = m.enrollment_id
    LEFT JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
    LEFT JOIN predictions p ON e.student_id = p.student_id AND e.course_id = p.course_id AND sem.semester_id = p.semester_id
    WHERE sem.semester_id = in_semester_id
    GROUP BY sem.semester_name, sem.academic_year, c.course_code, c.course_name;
END //

DELIMITER ;

