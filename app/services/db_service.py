from sqlalchemy import text, inspect
from app.database.connection import db_manager

class DatabaseService:
    @staticmethod
    def get_database_status():
        return {
            'is_connected': db_manager.is_connected,
            'dialect': db_manager.active_dialect,
            'connection_error': db_manager.connection_error,
            'is_fallback': (db_manager.active_dialect == 'sqlite'),
            'table_stats': db_manager.get_table_statistics()
        }

    @staticmethod
    def get_views_info():
        views = [
            {'name': 'v_student_academic_summary', 'purpose': 'Aggregates student assessment scores, credits, and GPA.'},
            {'name': 'v_student_attendance_summary', 'purpose': 'Computes course-level attendance sessions, presence, and attendance percentage.'},
            {'name': 'v_course_performance', 'purpose': 'Calculates course enrollment counts, average marks, min/max marks, and fail rates.'},
            {'name': 'v_department_performance', 'purpose': 'Summarizes department-wide student counts, faculty counts, and academic standing.'},
            {'name': 'v_at_risk_students', 'purpose': 'Early warning view joining active high-risk ML predictions with live attendance metrics.'},
            {'name': 'v_semester_performance', 'purpose': 'Evaluates semester-level academic trends across all courses and active enrollments.'}
        ]
        return views

    @staticmethod
    def get_procedures_info():
        procedures = [
            {
                'name': 'sp_calculate_attendance',
                'parameters': 'IN in_student_id INT, IN in_course_id INT, OUT out_percentage DECIMAL(5,2)',
                'description': 'Calculates attendance percentage directly in the database engine using aggregate count ratios.'
            },
            {
                'name': 'sp_generate_student_summary',
                'parameters': 'IN in_student_id INT',
                'description': 'Returns multi-result set containing student demographics, course mark breakdowns, and ML risk history.'
            },
            {
                'name': 'sp_get_high_risk_students',
                'parameters': 'IN in_department_id INT, IN in_semester_id INT',
                'description': 'Retrieves prioritized high-risk student roster filtered optionally by department and semester.'
            },
            {
                'name': 'sp_generate_semester_report',
                'parameters': 'IN in_semester_id INT',
                'description': 'Aggregates course marks, attendance percentages, and high-risk student counts for a designated semester.'
            }
        ]
        return procedures

    @staticmethod
    def get_triggers_info():
        triggers = [
            {
                'name': 'trg_attendance_audit',
                'event': 'AFTER UPDATE ON attendance_records',
                'description': 'Captures status corrections and writes prior and updated statuses to audit_logs.'
            },
            {
                'name': 'trg_marks_insert_audit',
                'event': 'AFTER INSERT ON marks',
                'description': 'Logs newly awarded assessment marks into audit_logs table.'
            },
            {
                'name': 'trg_marks_update_audit',
                'event': 'AFTER UPDATE ON marks',
                'description': 'Records prior and updated marks when an evaluation score is modified.'
            },
            {
                'name': 'trg_marks_delete_audit',
                'event': 'AFTER DELETE ON marks',
                'description': 'Safeguards audit history by logging deleted marks and recording author.'
            },
            {
                'name': 'trg_high_risk_prediction_alert',
                'event': 'AFTER INSERT ON predictions',
                'description': 'Automatically fires on qualifying High-Risk prediction insertions, adding a real-time notification alert while preventing duplicates.'
            }
        ]
        return triggers

    @staticmethod
    def execute_safe_query(query_sql):
        """
        Safely executes a read-only SELECT query submitted by authorized users.
        Strictly forbids any data or schema mutation statements.
        """
        clean_sql = query_sql.strip()
        destructive_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE',
            'REPLACE', 'GRANT', 'REVOKE', 'CREATE', 'RENAME', 'EXECUTE', 'CALL'
        ]

        # Ensure query begins with SELECT or WITH
        first_token = clean_sql.split()[0].upper() if clean_sql else ''
        if first_token not in ('SELECT', 'WITH', 'EXPLAIN'):
            return {'success': False, 'error': 'Security Policy: Only read-only SELECT queries are permitted in the DBMS interface.'}

        # Check for embedded destructive commands
        upper_sql = clean_sql.upper()
        for kw in destructive_keywords:
            if f"; {kw}" in upper_sql or f";{kw}" in upper_sql:
                return {'success': False, 'error': f"Security Policy: Multiple statements or '{kw}' commands are forbidden."}

        session = db_manager.get_session()
        try:
            result = session.execute(text(clean_sql))
            if result.returns_rows:
                rows = [dict(row._mapping) for row in result.fetchmany(100)]
                columns = list(result.keys()) if result.keys() else []
                return {
                    'success': True,
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows),
                    'truncated': len(rows) == 100
                }
            return {'success': True, 'columns': [], 'rows': [], 'row_count': 0}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            session.close()

    @staticmethod
    def get_query_execution_plan(query_sql):
        try:
            plan_rows = db_manager.explain_query(query_sql)
            return {'success': True, 'plan': plan_rows}
        except Exception as e:
            return {'success': False, 'error': str(e)}

