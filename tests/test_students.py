import pytest
from app.services.student_service import StudentService

def test_student_crud():
    """Test full CRUD lifecycle for student records."""
    # 1. Create
    reg_no = "REG-TEST-999"
    student, err = StudentService.create_student(
        reg_no=reg_no,
        name="Test Candidate",
        dept_id=1,
        semester=3,
        admission_year=2024,
        contact="test@acadrisk.edu"
    )
    assert err is None
    assert student['registration_number'] == reg_no

    # 2. Read / Search
    students, count = StudentService.get_students(search_query="Test Candidate")
    assert count >= 1
    assert any(s['registration_number'] == reg_no for s in students)

    # 3. Update
    student_id = student['student_id']
    upd, err = StudentService.update_student(
        student_id=student_id,
        name="Updated Candidate Name",
        dept_id=1,
        semester=4
    )
    assert err is None
    assert upd['student_name'] == "Updated Candidate Name"
    assert upd['semester'] == 4

    # 4. Delete
    deleted, err = StudentService.delete_student(student_id)
    assert deleted is True
    assert err is None

def test_student_duplicate_prevention():
    """Verify duplicate detection prevents duplicate student registration numbers."""
    student, err = StudentService.create_student(
        reg_no="REG-2023-CS001",  # Existing seed
        name="Clashing Name",
        dept_id=1,
        semester=1,
        admission_year=2024
    )
    assert student is None
    assert "already exists" in err.lower()

def test_student_invalid_semester():
    """Verify validation boundary rejects semesters outside 1-8."""
    student, err = StudentService.create_student(
        reg_no="REG-INVALID-SEM",
        name="Invalid Sem Student",
        dept_id=1,
        semester=10,  # Invalid
        admission_year=2024
    )
    assert student is None
    assert "between 1 and 8" in err

