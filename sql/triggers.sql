-- ====================================================================
-- AcadRisk AI: MySQL Triggers
-- Automates Audit Logging and Real-Time Early Warning Alerts
-- ====================================================================

USE acadrisk_db;

DROP TRIGGER IF EXISTS trg_attendance_audit;
DROP TRIGGER IF EXISTS trg_marks_insert_audit;
DROP TRIGGER IF EXISTS trg_marks_update_audit;
DROP TRIGGER IF EXISTS trg_marks_delete_audit;
DROP TRIGGER IF EXISTS trg_high_risk_prediction_alert;

DELIMITER //

-- TRIGGER 1: Attendance Modification Audit Trigger
-- Fires when an attendance record is updated to track status corrections
CREATE TRIGGER trg_attendance_audit
AFTER UPDATE ON attendance_records
FOR EACH ROW
BEGIN
    IF OLD.attendance_status <> NEW.attendance_status THEN
        INSERT INTO audit_logs (
            user_id,
            action_type,
            table_name,
            record_id,
            old_values,
            new_values,
            timestamp
        ) VALUES (
            NULL,
            'UPDATE',
            'attendance_records',
            NEW.attendance_id,
            CONCAT('{"status": "', OLD.attendance_status, '"}'),
            CONCAT('{"status": "', NEW.attendance_status, '"}'),
            NOW()
        );
    END IF;
END //

-- TRIGGER 2: Marks Insertion Audit Trigger
-- Fires on new marks insertion to log newly awarded marks
CREATE TRIGGER trg_marks_insert_audit
AFTER INSERT ON marks
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action_type,
        table_name,
        record_id,
        old_values,
        new_values,
        timestamp
    ) VALUES (
        NEW.recorded_by,
        'INSERT',
        'marks',
        NEW.mark_id,
        NULL,
        CONCAT('{"assessment_id": ', NEW.assessment_id, ', "enrollment_id": ', NEW.enrollment_id, ', "obtained_marks": ', NEW.obtained_marks, '}'),
        NOW()
    );
END //

-- TRIGGER 3: Marks Update Audit Trigger
-- Fires when marks are modified, logging the previous and updated scores
CREATE TRIGGER trg_marks_update_audit
AFTER UPDATE ON marks
FOR EACH ROW
BEGIN
    IF OLD.obtained_marks <> NEW.obtained_marks THEN
        INSERT INTO audit_logs (
            user_id,
            action_type,
            table_name,
            record_id,
            old_values,
            new_values,
            timestamp
        ) VALUES (
            NEW.recorded_by,
            'UPDATE',
            'marks',
            NEW.mark_id,
            CONCAT('{"obtained_marks": ', OLD.obtained_marks, '}'),
            CONCAT('{"obtained_marks": ', NEW.obtained_marks, '}'),
            NOW()
        );
    END IF;
END //

-- TRIGGER 4: Marks Deletion Audit Trigger
-- Fires when a marks record is deleted
CREATE TRIGGER trg_marks_delete_audit
AFTER DELETE ON marks
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action_type,
        table_name,
        record_id,
        old_values,
        new_values,
        timestamp
    ) VALUES (
        NULL,
        'DELETE',
        'marks',
        OLD.mark_id,
        CONCAT('{"assessment_id": ', OLD.assessment_id, ', "enrollment_id": ', OLD.enrollment_id, ', "obtained_marks": ', OLD.obtained_marks, '}'),
        NULL,
        NOW()
    );
END //

-- TRIGGER 5: Prediction High-Risk Early Warning Notification Trigger
-- Automatically creates an alert when a qualifying high-risk prediction is inserted,
-- preventing duplicate unread notifications for the same student and course.
CREATE TRIGGER trg_high_risk_prediction_alert
AFTER INSERT ON predictions
FOR EACH ROW
BEGIN
    DECLARE student_user_id INT;
    DECLARE existing_unread_count INT DEFAULT 0;
    DECLARE student_reg_no VARCHAR(50);
    DECLARE course_name_str VARCHAR(150);

    IF NEW.risk_category = 'High Risk' THEN
        -- Locate the user_id corresponding to the at-risk student
        SELECT s.user_id, s.registration_number, c.course_name 
        INTO student_user_id, student_reg_no, course_name_str
        FROM students s
        JOIN courses c ON c.course_id = NEW.course_id
        WHERE s.student_id = NEW.student_id;

        IF student_user_id IS NOT NULL THEN
            -- Check for existing unread high-risk alerts for this student to prevent duplicate alerts
            SELECT COUNT(*) INTO existing_unread_count
            FROM notifications
            WHERE user_id = student_user_id 
              AND notification_type = 'High Risk Alert'
              AND read_status = FALSE;

            IF existing_unread_count = 0 THEN
                INSERT INTO notifications (
                    user_id,
                    notification_type,
                    message,
                    read_status,
                    created_at
                ) VALUES (
                    student_user_id,
                    'High Risk Alert',
                    CONCAT('Early Warning Alert: Student ', student_reg_no, ' is predicted High Academic Risk in course ', course_name_str, ' with probability ', ROUND(NEW.risk_probability * 100, 1), '%. Immediate academic intervention recommended.'),
                    FALSE,
                    NOW()
                );
            END IF;
        END IF;
    END IF;
END //

DELIMITER ;

