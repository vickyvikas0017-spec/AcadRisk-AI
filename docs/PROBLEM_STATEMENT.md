# AcadRisk AI: Problem Statement & Context

## 1. Executive Summary

Higher educational institutions face significant challenges regarding student academic attrition, late-stage course failure, and delayed graduation. Traditional academic information systems operate primarily as retrospective recording mechanisms: they log attendance, record examination scores, and compute semester grade point averages (SGPA) only after assessments are graded and official transcripts are published. By the time faculty advisers or department chairs identify that a student is in severe academic distress, the semester has typically concluded, resulting in mandatory course repeats, financial burdens, reduced graduation rates, and emotional distress for students.

**AcadRisk AI** addresses this systemic gap by transforming the institutional Academic Information System from a passive ledger into an active, intelligent early warning and risk mitigation platform. By combining a 3NF-normalized Advanced Database Management System (DBMS) on MySQL 8 with machine learning classification and regression pipelines, AcadRisk AI identifies at-risk students during weeks 4–8 of a semester, analyzes contributing risk factors, generates actionable early alerts, and tracks faculty interventions to resolution.

---

## 2. Background & Context in Higher Education

### 2.1 The Global and National Retention Challenge
Academic retention is a premier Key Performance Indicator (KPI) for accreditation bodies (e.g., NAAC, NBA, ABET) and educational ministries worldwide. Empirical studies in engineering and technical education indicate:
- **15% to 25%** of undergraduate engineering students experience academic probation or fail one or more foundational courses within their first two years.
- **Over 60%** of eventual college dropouts show identifiable warning indicators (attendance degradation below 75%, poor continuous assessment performance, or prerequisite knowledge gaps) within the first 6 weeks of instruction.
- Remedial counseling or tutorial programs implemented after midterm examinations yield a **40% higher recovery rate** than post-semester interventions.

### 2.2 Shortcomings of Conventional Academic ERPs
Most commercial and bespoke Campus Management Systems (CMS) and Enterprise Resource Planning (ERP) solutions suffer from architectural and operational limitations:
1. **Siloed Data Architecture:** Attendance records, internal assessment scores, and counseling notes reside in disparate tables or disconnected spreadsheets without cohesive integration.
2. **Absence of Predictive Analytics:** Conventional queries are strictly historical (e.g., `SELECT * FROM marks WHERE final_score < 40`). They fail to forecast impending failure based on attendance trajectory, past academic trajectory, and midterm trends.
3. **Target Leakage and Naive Heuristics:** Where predictive logic is attempted in legacy tools, developers often rely on static heuristic rules (e.g., "if attendance < 65% then risk") or suffer from *target leakage* by including end-semester grades in the predictive feature vector.
4. **Lack of Auditable Intervention Workflows:** When warnings are issued, conventional systems lack closed-loop tracking to record counseling sessions, peer tutoring assignments, parent notifications, and subsequent academic recovery.

---

## 3. Project Objectives

AcadRisk AI was designed to fulfill four primary academic and engineering objectives:

### Objective 1: Advanced Relational Database Architecture
- Design and implement a robust, 3NF-normalized relational database schema comprising **23 relational tables** in MySQL 8.
- Enforce institutional integrity constraints: strict Primary/Foreign Keys with cascading semantics, table-level `CHECK` constraints (e.g., marks bounded within $[0, \text{maximum\_marks}]$, attendance bounded within $[0, 100\%]$), `UNIQUE` constraints (preventing duplicate enrollments or session attendance).
- Develop advanced database abstractions:
  - 6 Production Views for real-time reporting without costly table scans.
  - 4 Stored Procedures encapsulating complex business logic (automated attendance calculation, student academic profiling, risk candidate identification, and semester performance auditing).
  - 5 MySQL Database Triggers enforcing transparent audit logging and automatic notification dispatching upon high-risk prediction generation.
  - Performance optimization via composite B-tree indexing and query plan analysis using `EXPLAIN`.

### Objective 2: Target-Leakage-Free Machine Learning Pipeline
- Ingest and preprocess real-world educational data based on the benchmark **UCI Student Performance Dataset** (Cortez & Silva, 2008) and continuous assessment frameworks aligned with the **IITR-APE Dataset** (Bachchas et al., 2021).
- Implement a strict feature boundary: **strictly exclude end-semester grades ($G3$)** from all training and inference feature sets.
- Train, cross-validate, and evaluate multiple algorithms: **Logistic Regression** (with class-weight balancing), **Random Forest Classifier**, and **Gradient Boosting Classifier**.
- Maximize **High-Risk Class Recall ($\ge 80\%$)** to ensure virtually no failing student goes undetected by the early warning system.
- Provide continuous final percentage regression alongside discrete 3-tier risk classification:
  - **High Risk:** Predicted score $< 50\%$ or High Risk class probability $> 0.50$.
  - **Medium Risk:** Predicted score $50\% - 69\%$.
  - **Low Risk:** Predicted score $\ge 70\%$.

### Objective 3: Full-Stack Web Application with Pure White UI
- Build a responsive, accessible, enterprise-grade web application using **Python / Flask** with modular Flask Blueprints.
- Implement a **pure white design system** (`#FFFFFF` background throughout, `#1E40AF` primary blue accents, `#E5E7EB` clean structural borders, zero dark mode).
- Provide **23 dedicated functional views** corresponding directly to all administrative, pedagogical, predictive, and database operations.
- Integrate interactive visualization dashboards using **Chart.js** displaying risk distributions, departmental comparisons, and longitudinal attendance tracking.

### Objective 4: Closed-Loop Intervention & Audit System
- Bridge prediction and action: allow faculty and advisers to log tailored interventions (peer tutoring, mentor counseling, remedial labs, parent conferences).
- Track intervention status through four phases: `Planned`, `In Progress`, `Completed`, `Follow-up Required`.
- Maintain complete accountability via immutable application and trigger-level audit trails recording user identity, action type, affected table, before/after values, and timestamps.

---

## 4. Target Stakeholders & User Roles

| Role | Operational Scope & Value Proposition |
| :--- | :--- |
| **Administrator** | Full system governance: user provisioning, department/course catalog management, semester lifecycle control, database backup/restore, custom SQL console with `EXPLAIN` analysis, and ML model retraining. |
| **Faculty / Mentor** | Course and student management: daily session attendance logging, continuous assessment grading, single-student and batch ML risk prediction, intervention logging, and departmental report generation. |
| **Student** | Self-monitoring portal: transparent access to attendance percentages with low-attendance warnings, continuous assessment marks, academic trajectory, and personalized recommendations for improvement. |

---

## 5. Scope & Boundary Conditions

### Included in Scope:
- Complete relational database schema (23 tables, 6 views, 4 stored procedures, 5 triggers, 8 indexing strategies).
- Machine learning pipeline with multi-model comparison, hyperparameter configuration, model persistence (`joblib`), and runtime inference.
- Dual-engine database resilience: primary connectivity to MySQL 8 with automated fallback to SQLite for local development.
- Secure role-based access control (RBAC), password hashing via PBKDF2/SHA-256, CSRF session protection, and SQL injection prevention via SQLAlchemy parameterized ORM queries.
- Bulk data import via CSV/Excel with transactional rollback upon validation failure.
- Report generation with PDF and Excel export capabilities.

### Excluded from Current Scope:
- Automated biometric facial recognition or RFID hardware for attendance capture (manual or CSV batch upload is supported).
- Direct external SMS gateway integration (in-app notifications and email-ready notification dispatch are fully implemented).
