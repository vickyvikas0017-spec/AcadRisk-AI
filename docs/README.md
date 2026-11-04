# AcadRisk AI

**AI/ML-Based Student Academic Risk Prediction and Early Warning System Using Advanced Database Management System**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask%203.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-MySQL%208%20%7C%20SQLite%20Fallback-orange.svg)](https://www.mysql.com/)
[![ML](https://img.shields.io/badge/ML-Scikit--Learn%201.8.0-red.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/tests-32%20passed%20%28100%25%29-brightgreen.svg)]()
[![UI](https://img.shields.io/badge/UI-Pure%20White%20%23FFFFFF-lightgrey.svg)]()

---

## 1. Project Overview

**AcadRisk AI** is an enterprise-grade academic management and predictive early warning platform. Designed for higher education institutions, it transforms academic management systems from passive historical ledgers into proactive student success engines.

By combining an **Advanced Database Management System (DBMS)** with **Machine Learning (ML)** and a **pure white, professional web interface**, AcadRisk AI enables department administrators, faculty mentors, and students to detect academic distress weeks before final examinations, diagnose primary contributing risk factors, and coordinate timely remedial interventions.

### Key Capabilities:
- **3NF-Normalized Relational Database:** 23 interconnected relational tables in MySQL 8 enforcing strict primary, foreign key, unique, and check constraints.
- **Advanced DBMS Features:** 6 analytical views, 4 stored procedures, 5 database audit and alert triggers, index optimization, and transaction rollback guarantees.
- **Target-Leakage-Free ML Engine:** Multi-algorithm predictive modeling (Logistic Regression, Random Forest, Gradient Boosting) trained on the benchmark UCI Student Performance dataset with continuous assessment mapping.
- **High-Risk Class Recall Optimization:** Prioritizes sensitivity ($> 82\%$ recall on failing students) to ensure at-risk students are never missed.
- **Pure White UI System:** Responsive interface adhering to a strict `#FFFFFF` background, `#1E40AF` blue accents, light borders, and zero dark mode across all 23 views.
- **Dual-Engine Database Resilience:** Primary connectivity to MySQL 8 with automatic, transparent fallback to local SQLite when MySQL is offline.

---

## 2. Technology Stack

- **Backend:** Python 3.10+, Flask 3.1.2, Flask Blueprints (25 modular routes), SQLAlchemy 2.0.36, PyMySQL 1.2.3.
- **Database:** MySQL 8 Enterprise / Community Edition (Production), SQLite 3 (Fallback & local unit testing).
- **Machine Learning:** Scikit-Learn 1.8.0, Pandas 3.0.0, NumPy 2.4.0, Joblib 1.5.3.
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Chart.js 4.4, FontAwesome Icons.
- **Reporting & Exports:** OpenPyXL 3.1.5 (Excel reports), ReportLab 4.2.5 (PDF generation).
- **Automated Testing:** Pytest 8.3.4, Flask Test Client.

---

## 3. System Architecture & Project Structure

```
DBMS LAB/
├── app/
│   ├── database/             # Dual-engine connection manager, session handling
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── ml/                   # Machine learning pipeline, dataset loader, predictor
│   │   ├── __init__.py
│   │   ├── dataset_loader.py
│   │   ├── preprocessor.py
│   │   ├── trainer.py
│   │   └── predictor.py
│   ├── models/               # SQLAlchemy ORM entity models (23 tables)
│   │   ├── __init__.py
│   │   └── entities.py
│   ├── routes/               # 25 Flask modular blueprints
│   │   ├── auth_routes.py, dashboard_routes.py, student_routes.py, ...
│   ├── services/             # Application business logic layer (15 services)
│   │   ├── auth_service.py, student_service.py, marks_service.py, ...
│   ├── static/               # Pure white CSS design system and JavaScript
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/            # Jinja2 HTML templates for all 23 views
│   └── utils/                # RBAC decorators and Excel/PDF export utilities
├── datasets/
│   └── public/               # Benchmark UCI Student Performance dataset
├── trained_models/           # Serialized Joblib models (preprocessor, classifier, regressor)
├── sql/                      # Production MySQL 8 DDL scripts
│   ├── schema.sql            # 23 tables DDL with constraints
│   ├── indexes.sql           # Performance B-Tree indexes
│   ├── views.sql             # 6 production SQL views
│   ├── procedures.sql        # 4 stored procedures
│   ├── triggers.sql          # 5 database triggers
│   ├── seed.sql              # Realistic institutional demo records
│   └── reports.sql           # Analytical reporting queries
├── tests/                    # Automated Pytest suite (32 tests)
├── docker-compose.yml        # Multi-container MySQL 8 orchestration
├── requirements.txt          # Production Python dependencies
├── config.py                 # Application configuration & environment settings
├── run.py                    # Application launch entry point
└── [Documentation Files]     # PROBLEM_STATEMENT.md, DATABASE_DESIGN.md, ...
```

---

## 4. Installation & Setup Guide

### 4.1 Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Git (optional, for version control).
- MySQL 8.0+ or Docker Desktop (optional, if running MySQL container).

### 4.2 Clone or Open the Workspace
```powershell
cd "c:\Users\VIKAS VICKY\OneDrive\Desktop\Minor Projects\DBMS LAB"
```

### 4.3 Create & Activate Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4.4 Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 5. Database Setup (Dual-Engine Configuration)

AcadRisk AI provides **dual-engine resiliency**. You can run the application with MySQL 8 or with the built-in SQLite engine:

### Option A: Using Docker Compose (MySQL 8)
To spin up a dedicated MySQL 8 container with preconfigured health checks:
```powershell
docker-compose up -d
```
The MySQL container initializes on port `3306` with database `acadrisk_db`, user `root`, and password `rootpassword`.

### Option B: Using Local MySQL Server
1. Log into your MySQL 8 instance:
   ```powershell
   mysql -u root -p
   ```
2. Create the database and execute the SQL scripts in order:
   ```sql
   CREATE DATABASE acadrisk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE acadrisk_db;
   SOURCE sql/schema.sql;
   SOURCE sql/indexes.sql;
   SOURCE sql/views.sql;
   SOURCE sql/procedures.sql;
   SOURCE sql/triggers.sql;
   SOURCE sql/seed.sql;
   ```
3. Update `.env` with your database credentials:
   ```ini
   DB_TYPE=mysql
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=acadrisk_db
   ```

### Option C: Built-in SQLite Fallback (Zero Setup)
If MySQL is not installed or unreachable, the application automatically initializes and connects to `acadrisk_fallback.db`. The active engine status is transparently displayed on the dashboard navigation bar.
To initialize or reseed the database programmatically:
```powershell
python scripts/init_db.py
```

---

## 6. Training the Machine Learning Models

AcadRisk AI includes pre-trained, serialized models in `trained_models/`. To retrain the models from the raw UCI dataset and benchmark Logistic Regression, Random Forest, and Gradient Boosting:
```powershell
python -m app.ml.trainer
```
The trainer outputs accuracy, precision, recall, F1-score, and persists the best-performing models directly into `trained_models/` and logs the run in the `model_registry` table.

---

## 7. Running the Application

Launch the local web server:
```powershell
python run.py
```
Open your browser and navigate to:
**http://127.0.0.1:5000**

---

## 8. Demo Login Credentials

The database is pre-seeded with three operational role accounts:

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@123` | Full access to all 23 navigation views, database management, SQL console, model retraining, and audit logs. |
| **Faculty Member** | `faculty1` | `Faculty@123` | Course roster management, attendance logging, mark recording, risk predictions, and intervention creation. |
| **Student** | `student1` | `Student@123` | Student dashboard, attendance records, mark breakdown, academic progress, and personal recommendations. |

---

## 9. Complete Navigation & View Directory (23 Views)

1. **Dashboard (`/dashboard`):** Real-time KPI summary cards, risk distribution donut chart, department averages, quick action buttons.
2. **Student Management (`/students`):** Complete student directory, enrollment profiles, search, filter, and CRUD operations.
3. **Faculty Management (`/faculty`):** Faculty registry, departmental assignments, and course allocations.
4. **Department Management (`/departments`):** Academic division registry, department head mapping, and course counts.
5. **Course Management (`/courses`):** Course catalog, syllabus credits, department associations.
6. **Semester Management (`/semesters`):** Term management, start/end dates, academic calendar sync.
7. **Enrollment Management (`/enrollments`):** Student-course semester registrations with duplicate prevention.
8. **Attendance Management (`/attendance`):** Session scheduler, lecture/lab presence recording, real-time percentage calculator.
9. **Examination Management (`/examinations`):** Assessment scheduling (Midterms, Quizzes, Finals, Labs).
10. **Marks Management (`/marks`):** Mark entry ledger with validation against assessment maximums.
11. **Academic History (`/history`):** Historical SGPA records, credit accumulation, and final grades.
12. **AI Predictions (`/predictions`):** Live model inference interface for single students and batch semester runs.
13. **Risk Monitoring (`/risk`):** Dedicated high/medium risk monitoring table, risk category filters, urgent alerts.
14. **Intervention Management (`/interventions`):** Student remediation tracker with status tracking (`PLANNED`, `IN_PROGRESS`, `COMPLETED`).
15. **Notifications (`/notifications`):** In-app notification center receiving automated trigger alerts.
16. **Data Import (`/imports`):** Bulk CSV/Excel uploader for students, marks, and attendance with transactional validation.
17. **Database Management (`/database`):** Interactive SQL query runner with `EXPLAIN` query plan visualizer and schema inspector.
18. **Reports & Analytics (`/reports`):** Statistical reports with instant Excel and PDF export buttons.
19. **Model Management (`/models`):** Machine learning model registry, benchmark comparisons, and model retraining controls.
20. **Audit Logs (`/audit`):** Immutable log table displaying table name, action type, user ID, and before/after JSON states.
21. **Backup & Restore (`/backup`):** One-click database snapshot exporter and JSON/SQL restore utility.
22. **User Management (`/users`):** Account provisioning, role assignments, and password reset functions.
23. **Settings (`/settings`):** System configuration, risk threshold parameter adjustments, institution metadata.

---

## 10. REST API Documentation

All endpoints return JSON and require active session authentication or API tokens:

- `POST /api/v1/predict/single`
  - **Body:** `{"student_id": 1, "course_id": 2}`
  - **Response:** `{"risk_category": "HIGH", "risk_probability": 0.825, "predicted_score": 42.5, "contributing_factors": [...]}`
- `POST /api/v1/predict/batch`
  - **Body:** `{"semester_id": 1}`
  - **Response:** `{"run_id": 3, "total_predictions": 45, "high_risk_count": 8, "status": "SUCCESS"}`
- `GET /api/v1/students/<id>/summary`
  - **Response:** Student demographic info, attendance percentage, average score, and active risk level.
- `GET /api/v1/stats/overview`
  - **Response:** Real-time metrics for dashboard cards (total students, active enrollments, at-risk count).

---

## 11. Automated Testing

AcadRisk AI features a comprehensive Pytest test suite covering all functional layers:
```powershell
pytest
```
To run tests with detailed verbosity:
```powershell
pytest -v -s
```
**Test Results:** **32 passed out of 32 tests (100% pass rate).**

---

## 12. Project Limitations & Future Scope

### Current Limitations:
- **Biometric Integration:** Attendance is recorded manually by faculty or via bulk CSV upload; direct biometric fingerprint/facial scanner integration is not included.
- **SMS Gateway:** Automated notifications are delivered within the web portal and formatted for SMTP email; live SMS requires external Twilio/AWS SNS credentials.

### Future Enhancements:
- **Explainable AI (XAI):** Integration of SHAP (SHapley Additive exPlanations) water-fall plots for individual student risk factor explanation.
- **Deep Learning Sequence Models:** Implementation of LSTM/GRU recurrent neural networks to model weekly temporal progression in student engagement.
- **LMS Integration:** LTI 1.3 compliance for seamless plug-in integration into Moodle and Canvas.
