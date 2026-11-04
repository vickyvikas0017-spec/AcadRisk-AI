import os
import io
import csv
import pandas as pd
from datetime import datetime
from decimal import Decimal
from app.database.connection import db_manager
from app.models.entities import (
    ImportBatch, ImportError, Student, Department, Enrollment,
    AttendanceRecord, AttendanceSession, Assessment, Mark, AuditLog
)

class ImportService:
    SAMPLE_TEMPLATES = {
        'students': [
            ['registration_number', 'student_name', 'department_code', 'semester', 'admission_year', 'contact_information'],
            ['REG-2024-CS050', 'Alice Smith', 'CSE', '4', '2024', '+1-555-0301'],
            ['REG-2024-IT051', 'Bob Jones', 'IT', '4', '2024', '+1-555-0302']
        ],
        'attendance': [
            ['session_id', 'registration_number', 'attendance_status'],
            ['1', 'REG-2023-CS001', 'Present'],
            ['1', 'REG-2023-CS002', 'Absent']
        ],
        'marks': [
            ['assessment_id', 'registration_number', 'obtained_marks'],
            ['1', 'REG-2023-CS001', '22.5'],
            ['1', 'REG-2023-CS002', '24.0']
        ]
    }

    @classmethod
    def get_sample_csv(cls, import_type):
        rows = cls.SAMPLE_TEMPLATES.get(import_type, [])
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output.getvalue()

    @classmethod
    def process_file_import(cls, file_storage, import_type, user_id=None, atomic=True):
        """
        Parses CSV or Excel file, validates records, detects duplicates/missing values,
        and executes an atomic transaction import.
        """
        filename = file_storage.filename
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ('csv', 'xlsx', 'xls'):
            return {'success': False, 'error': 'Invalid file format. Only CSV and Excel (.xlsx, .xls) are supported.'}

        # Read into pandas dataframe
        try:
            if ext == 'csv':
                df = pd.read_csv(file_storage)
            else:
                df = pd.read_excel(file_storage)
        except Exception as e:
            return {'success': False, 'error': f"Failed to parse uploaded file: {str(e)}"}

        total_rows = len(df)
        if total_rows == 0:
            return {'success': False, 'error': 'Uploaded file contains no data rows.'}

        session = db_manager.get_session()
        batch = ImportBatch(
            imported_by=user_id,
            file_name=filename,
            file_type=ext,
            import_type=import_type,
            total_records=total_rows,
            successful_records=0,
            failed_records=0,
            import_status='processing',
            imported_at=datetime.now()
        )
        session.add(batch)
        session.flush()

        errors = []
        success_count = 0

        try:
            if import_type == 'students':
                required_cols = {'registration_number', 'student_name', 'department_code', 'semester', 'admission_year'}
                if not required_cols.issubset(set(df.columns)):
                    missing = required_cols - set(df.columns)
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")

                # Preload department codes
                dept_map = {d.department_code.upper(): d.department_id for d in session.query(Department).all()}

                for idx, row in df.iterrows():
                    row_num = idx + 2  # Excel row numbering (header is row 1)
                    reg_no = str(row['registration_number']).strip().upper()
                    name = str(row['student_name']).strip()
                    dept_code = str(row['department_code']).strip().upper()

                    if pd.isna(reg_no) or not reg_no or pd.isna(name) or not name:
                        errors.append((row_num, "Registration number and student name cannot be empty."))
                        continue

                    if dept_code not in dept_map:
                        errors.append((row_num, f"Department code '{dept_code}' does not exist."))
                        continue

                    # Check duplicate
                    if session.query(Student).filter_by(registration_number=reg_no).first():
                        errors.append((row_num, f"Duplicate registration number '{reg_no}' already exists in database."))
                        continue

                    try:
                        sem = int(row['semester'])
                        adm_yr = int(row['admission_year'])
                        if sem < 1 or sem > 8:
                            raise ValueError()
                    except Exception:
                        errors.append((row_num, "Semester must be between 1 and 8, and admission year must be a valid year."))
                        continue

                    contact = str(row['contact_information']) if 'contact_information' in row and not pd.isna(row['contact_information']) else None
                    new_student = Student(
                        registration_number=reg_no,
                        student_name=name,
                        department_id=dept_map[dept_code],
                        semester=sem,
                        admission_year=adm_yr,
                        contact_information=contact
                    )
                    session.add(new_student)
                    success_count += 1

            elif import_type == 'attendance':
                required_cols = {'session_id', 'registration_number', 'attendance_status'}
                if not required_cols.issubset(set(df.columns)):
                    missing = required_cols - set(df.columns)
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")

                for idx, row in df.iterrows():
                    row_num = idx + 2
                    sess_id = int(row['session_id']) if not pd.isna(row['session_id']) else None
                    reg_no = str(row['registration_number']).strip().upper()
                    status = str(row['attendance_status']).strip()

                    if status not in ('Present', 'Absent', 'Late', 'Excused'):
                        errors.append((row_num, f"Invalid attendance status '{status}'. Must be Present, Absent, Late, or Excused."))
                        continue

                    sess = session.query(AttendanceSession).get(sess_id)
                    if not sess:
                        errors.append((row_num, f"Attendance Session #{sess_id} not found."))
                        continue

                    student = session.query(Student).filter_by(registration_number=reg_no).first()
                    if not student:
                        errors.append((row_num, f"Student '{reg_no}' not found."))
                        continue

                    enrollment = session.query(Enrollment).filter_by(
                        student_id=student.student_id,
                        course_id=sess.course_id,
                        semester_id=sess.semester_id
                    ).first()
                    if not enrollment:
                        errors.append((row_num, f"Student '{reg_no}' is not enrolled in course #{sess.course_id}."))
                        continue

                    existing = session.query(AttendanceRecord).filter_by(
                        session_id=sess_id,
                        enrollment_id=enrollment.enrollment_id
                    ).first()
                    if existing:
                        errors.append((row_num, f"Attendance record already exists for student '{reg_no}' in session #{sess_id}."))
                        continue

                    rec = AttendanceRecord(
                        session_id=sess_id,
                        enrollment_id=enrollment.enrollment_id,
                        attendance_status=status,
                        recorded_at=datetime.now()
                    )
                    session.add(rec)
                    success_count += 1

            elif import_type == 'marks':
                required_cols = {'assessment_id', 'registration_number', 'obtained_marks'}
                if not required_cols.issubset(set(df.columns)):
                    missing = required_cols - set(df.columns)
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")

                for idx, row in df.iterrows():
                    row_num = idx + 2
                    asmt_id = int(row['assessment_id']) if not pd.isna(row['assessment_id']) else None
                    reg_no = str(row['registration_number']).strip().upper()

                    asmt = session.query(Assessment).get(asmt_id)
                    if not asmt:
                        errors.append((row_num, f"Assessment #{asmt_id} not found."))
                        continue

                    try:
                        obt = Decimal(str(row['obtained_marks']))
                        if obt < Decimal('0') or obt > asmt.maximum_marks:
                            errors.append((row_num, f"Marks ({obt}) must be between 0 and maximum ({asmt.maximum_marks})."))
                            continue
                    except Exception:
                        errors.append((row_num, "Invalid marks value."))
                        continue

                    student = session.query(Student).filter_by(registration_number=reg_no).first()
                    if not student:
                        errors.append((row_num, f"Student '{reg_no}' not found."))
                        continue

                    enrollment = session.query(Enrollment).filter_by(
                        student_id=student.student_id,
                        course_id=asmt.course_id,
                        semester_id=asmt.semester_id
                    ).first()
                    if not enrollment:
                        errors.append((row_num, f"Student '{reg_no}' is not enrolled in course #{asmt.course_id}."))
                        continue

                    existing = session.query(Mark).filter_by(
                        assessment_id=asmt_id,
                        enrollment_id=enrollment.enrollment_id
                    ).first()
                    if existing:
                        errors.append((row_num, f"Marks already recorded for student '{reg_no}' in assessment #{asmt_id}."))
                        continue

                    mark_entry = Mark(
                        assessment_id=asmt_id,
                        enrollment_id=enrollment.enrollment_id,
                        obtained_marks=obt,
                        recorded_by=user_id,
                        recorded_at=datetime.now()
                    )
                    session.add(mark_entry)
                    success_count += 1

            # Check atomic import requirement
            if atomic and errors:
                session.rollback()
                # Record error batch separately
                err_batch = ImportBatch(
                    imported_by=user_id,
                    file_name=filename,
                    file_type=ext,
                    import_type=import_type,
                    total_records=total_rows,
                    successful_records=0,
                    failed_records=len(errors),
                    import_status='failed',
                    imported_at=datetime.now()
                )
                session.add(err_batch)
                session.flush()
                for r_num, desc in errors:
                    err_obj = ImportError(batch_id=err_batch.batch_id, row_number=r_num, error_description=desc)
                    session.add(err_obj)
                session.commit()
                return {
                    'success': False,
                    'atomic_rollback': True,
                    'total_rows': total_rows,
                    'errors_count': len(errors),
                    'errors': [{'row': r, 'description': d} for r, d in errors[:20]],
                    'error': f"Atomic Import Aborted: {len(errors)} error(s) detected. All changes rolled back to preserve database integrity."
                }

            # If successful or non-atomic
            batch.successful_records = success_count
            batch.failed_records = len(errors)
            batch.import_status = 'completed' if not errors else 'completed_with_errors'

            for r_num, desc in errors:
                err_obj = ImportError(batch_id=batch.batch_id, row_number=r_num, error_description=desc)
                session.add(err_obj)

            session.commit()
            return {
                'success': True,
                'batch_id': batch.batch_id,
                'total_rows': total_rows,
                'successful_records': success_count,
                'failed_records': len(errors),
                'errors': [{'row': r, 'description': d} for r, d in errors[:20]]
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f"Import transaction failed: {str(e)}"}
        finally:
            session.close()

    @classmethod
    def get_import_history(cls, limit=20):
        session = db_manager.get_session()
        try:
            batches = session.query(ImportBatch).order_by(ImportBatch.imported_at.desc()).limit(limit).all()
            return [b.to_dict() for b in batches]
        finally:
            session.close()

