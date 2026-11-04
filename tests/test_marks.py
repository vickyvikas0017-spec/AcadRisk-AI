import pytest
from app.services.marks_service import MarksService

def test_grade_calculation():
    """Verify standard academic grade translation from percentage."""
    grade_95, pt_95 = MarksService.calculate_letter_grade(95.0)
    assert grade_95 == 'A+'
    assert pt_95 == 10.0

    grade_85, _ = MarksService.calculate_letter_grade(85.0)
    assert grade_85 == 'A'

    grade_55, _ = MarksService.calculate_letter_grade(55.0)
    assert grade_55 == 'D'

    grade_35, pt_35 = MarksService.calculate_letter_grade(35.0)
    assert grade_35 == 'F'
    assert pt_35 == 0.0

def test_marks_validation_exceeding_max():
    """Verify constraint check: Obtained marks cannot exceed maximum assessment marks."""
    # Assessment 1 has maximum_marks = 25.0
    mark, err = MarksService.record_mark(
        assessment_id=1,
        enrollment_id=1,
        obtained_marks=30.0  # Exceeds 25.0!
    )
    assert mark is None
    assert "cannot exceed maximum" in err.lower()

def test_marks_validation_negative():
    """Verify constraint check: Obtained marks cannot fall below zero."""
    mark, err = MarksService.record_mark(
        assessment_id=1,
        enrollment_id=1,
        obtained_marks=-5.0  # Negative!
    )
    assert mark is None
    assert "below zero" in err.lower()

def test_valid_mark_recording():
    """Verify successfully recording valid marks within bounds."""
    mark, err = MarksService.record_mark(
        assessment_id=1,
        enrollment_id=1,
        obtained_marks=22.0
    )
    assert err is None
    assert mark['obtained_marks'] == 22.0

