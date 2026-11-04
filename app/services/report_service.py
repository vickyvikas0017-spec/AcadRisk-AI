from sqlalchemy import text
from app.database.connection import db_manager
from app.utils.export_helpers import generate_excel_report, generate_pdf_report

class ReportService:
    @staticmethod
    def get_department_performance():
        session = db_manager.get_session()
        try:
            sql = """
            SELECT 
                d.department_code,
                d.department_name,
                COUNT(DISTINCT s.student_id) AS total_students,
                COUNT(DISTINCT e.enrollment_id) AS course_enrollments,
                ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS average_score,
                ROUND(MIN((m.obtained_marks / a.maximum_marks) * 100), 2) AS min_score,
                ROUND(MAX((m.obtained_marks / a.maximum_marks) * 100), 2) AS max_score
            FROM departments d
            LEFT JOIN students s ON d.department_id = s.department_id
            LEFT JOIN enrollments e ON s.student_id = e.student_id
            LEFT JOIN marks m ON e.enrollment_id = m.enrollment_id
            LEFT JOIN assessments a ON m.assessment_id = a.assessment_id
            GROUP BY d.department_code, d.department_name
            ORDER BY average_score DESC
            """
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result]
        finally:
            session.close()

    @staticmethod
    def get_below_average_students():
        session = db_manager.get_session()
        try:
            sql = """
            SELECT 
                s.registration_number,
                s.student_name,
                d.department_code,
                s.semester,
                ROUND(AVG((m.obtained_marks / a.maximum_marks) * 100), 2) AS student_avg_score
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN marks m ON e.enrollment_id = m.enrollment_id
            JOIN assessments a ON m.assessment_id = a.assessment_id
            GROUP BY s.student_id, s.registration_number, s.student_name, d.department_code, s.semester
            HAVING student_avg_score < (
                SELECT AVG((m2.obtained_marks / a2.maximum_marks) * 100)
                FROM marks m2
                JOIN assessments a2 ON m2.assessment_id = a2.assessment_id
            )
            ORDER BY student_avg_score ASC
            """
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result]
        finally:
            session.close()

    @staticmethod
    def get_chronic_absenteeism():
        session = db_manager.get_session()
        try:
            sql = """
            SELECT 
                s.registration_number,
                s.student_name,
                c.course_code,
                c.course_name,
                COUNT(ar.attendance_id) AS total_classes,
                SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) AS attended,
                ROUND((SUM(CASE WHEN ar.attendance_status = 'Present' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(ar.attendance_id), 0)), 2) AS attendance_pct
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN courses c ON e.course_id = c.course_id
            JOIN attendance_records ar ON e.enrollment_id = ar.enrollment_id
            GROUP BY s.student_id, s.registration_number, s.student_name, c.course_id, c.course_code, c.course_name
            HAVING attendance_pct < 75.00
            ORDER BY attendance_pct ASC
            """
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result]
        finally:
            session.close()

    @staticmethod
    def get_at_risk_roster():
        session = db_manager.get_session()
        try:
            sql = """
            SELECT 
                s.registration_number,
                s.student_name,
                d.department_code,
                c.course_code,
                p.risk_category,
                ROUND(p.risk_probability * 100, 1) AS risk_prob_pct,
                ROUND(p.predicted_marks, 1) AS predicted_marks_pct,
                p.prediction_date
            FROM predictions p
            JOIN students s ON p.student_id = s.student_id
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON p.course_id = c.course_id
            WHERE p.risk_category IN ('High Risk', 'Medium Risk')
            ORDER BY p.risk_probability DESC, p.prediction_date DESC
            """
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result]
        finally:
            session.close()

    @staticmethod
    def export_report(report_type, export_format='excel'):
        """
        Coordinates generating Excel or PDF report based on SQL data.
        """
        if report_type == 'department':
            data = ReportService.get_department_performance()
            title = "Department Performance Report"
            headers = ['Code', 'Department Name', 'Students', 'Enrollments', 'Average Score (%)', 'Min Score', 'Max Score']
            rows = [[r['department_code'], r['department_name'], r['total_students'], r['course_enrollments'], r['average_score'], r['min_score'], r['max_score']] for r in data]
        elif report_type == 'attendance':
            data = ReportService.get_chronic_absenteeism()
            title = "Chronic Absenteeism Report (< 75%)"
            headers = ['Reg No', 'Student Name', 'Course Code', 'Course Name', 'Total Sessions', 'Attended', 'Attendance (%)']
            rows = [[r['registration_number'], r['student_name'], r['course_code'], r['course_name'], r['total_classes'], r['attended'], r['attendance_pct']] for r in data]
        elif report_type == 'below_average':
            data = ReportService.get_below_average_students()
            title = "Students Below Average Performance"
            headers = ['Reg No', 'Student Name', 'Department', 'Semester', 'Average Score (%)']
            rows = [[r['registration_number'], r['student_name'], r['department_code'], r['semester'], r['student_avg_score']] for r in data]
        else: # at_risk
            data = ReportService.get_at_risk_roster()
            title = "At-Risk Student Roster"
            headers = ['Reg No', 'Student Name', 'Dept', 'Course', 'Risk Category', 'Risk Probability (%)', 'Predicted Score (%)', 'Date']
            rows = [[r['registration_number'], r['student_name'], r['department_code'], r['course_code'], r['risk_category'], r['risk_prob_pct'], r['predicted_marks_pct'], str(r['prediction_date'])[:10]] for r in data]

        if export_format == 'excel':
            file_stream = generate_excel_report(title, headers, rows)
            filename = f"{report_type}_report.xlsx"
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            file_stream = generate_pdf_report(title, headers, rows)
            filename = f"{report_type}_report.pdf"
            mimetype = "application/pdf"

        return file_stream, filename, mimetype

