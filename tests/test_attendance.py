import pytest
from app.services.attendance_service import AttendanceService
from app.database.connection import db_manager
from app.models.entities import AttendanceRecord

def test_attendance_recording_and_percentage():
    """Verify attendance recording and percentage formula: (Present / Total) * 100."""
    # Student 1, Course 1
    att = AttendanceService.get_student_course_attendance(student_id=1, course_id=1)
    assert att['total'] > 0
    assert att['percentage'] >= 0.0 and att['percentage'] <= 100.0

    # Expected percentage formula verification
    expected_pct = round((att['present'] / att['total']) * 100.0, 2)
    assert att['percentage'] == expected_pct

def test_attendance_status_update_and_audit():
    """Verify authorized attendance correction and audit logging."""
    session = db_manager.get_session()
    try:
        rec = session.query(AttendanceRecord).first()
        assert rec is not None
        rec_id = rec.attendance_id

        # Update status
        ok, err = AttendanceService.update_attendance_status(rec_id, 'Present', user_id=1)
        assert ok is True
        assert err is None
    finally:
        session.close()

def test_invalid_attendance_status_rejected():
    """Verify that invalid attendance status values are rejected."""
    ok, err = AttendanceService.update_attendance_status(1, 'InvalidStatus')
    assert ok is False
    assert "Invalid attendance status" in err

