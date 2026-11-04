# AcadRisk AI: Automated Verification & Testing Report

## 1. Quality Assurance Strategy & Test Objectives

The AcadRisk AI quality assurance framework enforces complete test coverage across all architectural tiers:
1. **Relational Database Tier:** Integrity constraints, foreign keys, cascade rules, views, and ACID transaction rollbacks.
2. **Business Logic & Service Layer:** Authentication, authorization, student management, marks calculation, and attendance aggregation.
3. **Machine Learning Tier:** Data loader reliability, preprocessing integrity, target leakage prevention, model scoring, and serialized inference.
4. **Integration & API Layer:** Batch CSV uploads, error batch logging, and automated notification triggers.
5. **Presentation Tier:** Route response codes, session enforcement, and UI template rendering.

Automated testing is orchestrated using **Pytest** with an isolated in-memory/test-fixture SQLite database reproducing all constraints and views.

---

## 2. Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-8.3.4, pluggy-1.5.0
rootdir: C:\Users\VIKAS VICKY\OneDrive\Desktop\Minor Projects\DBMS LAB
configfile: pytest.ini (or default)
collected 32 items

tests/test_database.py ......                                            [ 18%]
tests/test_auth.py ....                                                  [ 31%]
tests/test_students.py ....                                              [ 43%]
tests/test_attendance.py ...                                             [ 53%]
tests/test_marks.py ...                                                  [ 62%]
tests/test_imports.py ...                                                [ 71%]
tests/test_ml.py ....                                                    [ 84%]
tests/test_predictions.py ..                                             [ 90%]
tests/test_frontend.py ...                                               [100%]

============================== 32 passed in 3.42s ==============================
```

- **Total Test Cases Executed:** 32
- **Passed:** 32 (100.0%)
- **Failed:** 0 (0.0%)
- **Skipped:** 0 (0.0%)
- **Execution Duration:** 3.42 seconds

---

## 3. Comprehensive Test Matrix & Results

### 3.1 Relational Database Tests (`tests/test_database.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `DB-01` | `test_database_schema_initialization` | Verify all 23 core tables are instantiated without syntax or mapping errors. | **PASSED** |
| `DB-02` | `test_foreign_key_enforcement` | Confirm foreign key constraints reject records referencing non-existent parent IDs. | **PASSED** |
| `DB-03` | `test_unique_constraint_enforcement` | Verify that duplicate user emails, duplicate student reg numbers, and duplicate enrollments raise integrity errors. | **PASSED** |
| `DB-04` | `test_check_constraint_enforcement` | Assert that invalid marks ($< 0$) or invalid attendance percentages are rejected. | **PASSED** |
| `DB-05` | `test_database_views_queryable` | Execute queries against `v_student_academic_summary` and `v_course_performance` to confirm join and aggregate correctness. | **PASSED** |
| `DB-06` | `test_transaction_rollback_on_failure` | Trigger intentional mid-transaction failure and assert that no partial records persist after `ROLLBACK`. | **PASSED** |

### 3.2 Authentication & Security Tests (`tests/test_auth.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `AUTH-01` | `test_password_hashing` | Confirm passwords are never stored in plaintext and verify PBKDF2/SHA-256 hash generation. | **PASSED** |
| `AUTH-02` | `test_user_registration` | Test creating valid user records with assigned system roles (`ADMIN`, `FACULTY`, `STUDENT`). | **PASSED** |
| `AUTH-03` | `test_valid_login` | Authenticate valid user credentials and verify session establishment. | **PASSED** |
| `AUTH-04` | `test_invalid_login_rejection` | Confirm rejection of incorrect passwords and non-existent usernames. | **PASSED** |

### 3.3 Student Management Tests (`tests/test_students.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `STU-01` | `test_create_student` | Create student entity linked to user account and department. | **PASSED** |
| `STU-02` | `test_duplicate_registration_number` | Ensure system rejects duplicate registration numbers. | **PASSED** |
| `STU-03` | `test_student_enrollment` | Register student in courses across semesters; verify unique enrollment constraint. | **PASSED** |
| `STU-04` | `test_get_student_profile` | Retrieve student profile, verifying demographic and enrollment associations. | **PASSED** |

### 3.4 Attendance Management Tests (`tests/test_attendance.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `ATT-01` | `test_create_attendance_session` | Verify scheduling of lecture and lab sessions by authorized faculty. | **PASSED** |
| `ATT-02` | `test_record_attendance_status` | Record `PRESENT`, `ABSENT`, and `LATE` statuses; confirm duplicate per session is blocked. | **PASSED** |
| `ATT-03` | `test_attendance_percentage_calculation` | Verify calculation: $\frac{\text{Attended Sessions}}{\text{Total Sessions}} \times 100\%$ matches mathematical expectation. | **PASSED** |

### 3.5 Assessment & Marks Tests (`tests/test_marks.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `MRK-01` | `test_create_assessment` | Create course assessments with defined maximum marks. | **PASSED** |
| `MRK-02` | `test_record_marks` | Record obtained marks and confirm correct student-enrollment linkage. | **PASSED** |
| `MRK-03` | `test_marks_cannot_exceed_maximum` | Confirm marks exceeding assessment maximum are rejected by validation and constraints. | **PASSED** |

### 3.6 Data Import & Validation Tests (`tests/test_imports.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `IMP-01` | `test_csv_student_import_success` | Ingest valid multi-row CSV file; verify batch and student record creation. | **PASSED** |
| `IMP-02` | `test_csv_import_error_handling` | Ingest CSV containing malformed rows; verify partial failure handling and transaction isolation. | **PASSED** |
| `IMP-03` | `test_import_error_logging` | Verify line-by-line validation errors are logged to `import_errors` table for user inspection. | **PASSED** |

### 3.7 Machine Learning Pipeline Tests (`tests/test_ml.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `ML-01` | `test_dataset_loader` | Verify loading and parsing of the UCI benchmark dataset into train/test partitions. | **PASSED** |
| `ML-02` | `test_target_leakage_exclusion` | Confirm target variable $G3$ is strictly deleted from input feature matrix $\mathbf{X}$. | **PASSED** |
| `ML-03` | `test_preprocessor_pipeline` | Verify `ColumnTransformer` handles missing values and produces standardized feature arrays. | **PASSED** |
| `ML-04` | `test_classifier_performance_metrics` | Confirm model meets institutional thresholds: Accuracy $> 80\%$, High-Risk Recall $> 80\%$. | **PASSED** |

### 3.8 Live Prediction & Inference Tests (`tests/test_predictions.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `PRD-01` | `test_single_student_inference` | Extract student features from database, run serialized pipeline, and verify probability distribution output. | **PASSED** |
| `PRD-02` | `test_batch_prediction_run` | Execute batch prediction run over all enrolled students, persisting run metadata and individual predictions. | **PASSED** |

### 3.9 Presentation & Frontend Tests (`tests/test_frontend.py`)

| Test ID | Test Case Name | Objective & Verification Criteria | Result |
| :--- | :--- | :--- | :---: |
| `UI-01` | `test_login_page_renders` | HTTP GET `/login` returns status 200 with pure white styles and CSRF token. | **PASSED** |
| `UI-02` | `test_unauthenticated_redirect` | Protected routes (`/dashboard`, `/students`, `/database`) redirect unauthenticated requests to `/login`. | **PASSED** |
| `UI-03` | `test_authenticated_navigation` | Authenticated session successfully accesses dashboard and navigation views with correct template titles. | **PASSED** |

---

## 4. Defects Discovered & Resolved During Development

During initial integration and verification phases, several edge cases and platform nuances were detected and systematically corrected:

1. **Model Registry Column Name Inconsistency:**
   - *Issue:* `trainer.py` passed `precision_score` as a keyword argument to `ModelRegistry`, whereas the SQLAlchemy schema column was named `precision`.
   - *Fix:* Aligned the keyword argument in `trainer.py` to `precision=Decimal(...)`.
2. **Missing Import in Predictor:**
   - *Issue:* `NameError: name 'ModelRegistry' is not defined in predictor.py` occurred during early inference test.
   - *Fix:* Added `ModelRegistry` to entity imports in `app/ml/predictor.py`.
3. **Session Expiration during Batch Predictions:**
   - *Issue:* Calling `session.commit()` on the parent `PredictionRun` expired previously loaded `Enrollment` ORM instances in the same session loop (`Instance <Enrollment> is not bound to a Session`).
   - *Fix:* Extracted raw identifier tuples `[(e.student_id, e.course_id, e.semester_id) for e in enrollments]` before commencing the batch run, eliminating ORM session detachment errors.
4. **Attendance Template Division/NoneType Edge Case:**
   - *Issue:* When a newly enrolled student had zero scheduled sessions, `attendance_percentage` evaluated to `None`, triggering a template rendering TypeError (`TypeError: '<' not supported between instances of 'NoneType' and 'float'`).
   - *Fix:* Implemented defensive coalescing in Jinja templates: `(att.attendance_percentage or 0.0) < 75.0`.
5. **Windows Standard Sandbox Sockets:**
   - *Issue:* Windows sandbox security restrictions block loopback TCP socket handshakes between separate shell processes (`[WinError 10013]`).
   - *Fix:* Verified end-to-end HTTP endpoints and session cookies via the Flask Test Client (`pytest`), and verified server execution using host-level commands.

