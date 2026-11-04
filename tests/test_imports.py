import io
import pytest
from app.services.import_service import ImportService
from app.database.connection import db_manager
from app.models.entities import Student

def test_atomic_rollback_on_batch_error():
    """Verify that an atomic CSV batch with an error rolls back completely without partial insertion."""
    session = db_manager.get_session()
    try:
        initial_student_count = session.query(Student).count()

        # CSV with 1 valid student and 1 invalid student (invalid department code 'NONEXISTENT')
        csv_content = """registration_number,student_name,department_code,semester,admission_year
REG-ATOMIC-1,Valid One,CSE,2,2024
REG-ATOMIC-2,Invalid One,NONEXISTENT,2,2024
"""
        file_obj = io.BytesIO(csv_content.encode('utf-8'))
        file_obj.filename = 'test_atomic.csv'

        res = ImportService.process_file_import(
            file_storage=file_obj,
            import_type='students',
            user_id=1,
            atomic=True
        )

        assert res['success'] is False
        assert res.get('atomic_rollback') is True

        # Verify no students from the batch were inserted
        final_count = session.query(Student).count()
        assert final_count == initial_student_count, "Atomic rollback failed: partial insert occurred!"
    finally:
        session.close()

def test_sample_csv_template_generation():
    """Verify downloadable CSV sample templates match expected headers."""
    for import_type in ['students', 'attendance', 'marks']:
        csv_str = ImportService.get_sample_csv(import_type)
        assert len(csv_str) > 0
        first_line = csv_str.splitlines()[0]
        if import_type == 'students':
            assert 'registration_number' in first_line
        elif import_type == 'attendance':
            assert 'session_id' in first_line
        elif import_type == 'marks':
            assert 'assessment_id' in first_line

