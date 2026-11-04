import pytest

def test_frontend_routes_accessible(auth_admin):
    """Verify that all major web views return HTTP 200 and render pure white dashboard layout."""
    client = auth_admin

    endpoints = [
        ('/', b'Institutional Academic Dashboard'),
        ('/students', b'Student Management'),
        ('/faculty', b'Faculty Management'),
        ('/departments', b'Department Management'),
        ('/courses', b'Course Management'),
        ('/semesters', b'Semester Management'),
        ('/enrollments', b'Enrollment Management'),
        ('/attendance', b'Attendance Management'),
        ('/examinations', b'Assessment Management'),
        ('/marks', b'Marks Management'),
        ('/academic-history', b'Academic History'),
        ('/predictions', b'AI Academic Risk Predictions'),
        ('/risk-monitoring', b'Risk Monitoring'),
        ('/interventions', b'Intervention Management'),
        ('/notifications', b'Notification'),
        ('/data-import', b'Batch Data Import'),
        ('/database-management', b'Advanced DBMS Management'),
        ('/reports', b'Institutional Reports'),
        ('/model-management', b'Machine Learning Model Management'),
        ('/audit-logs', b'Institutional Audit Logs'),
        ('/backup-restore', b'Database Backup'),
        ('/user-management', b'User'),
        ('/settings', b'Institutional Settings')
    ]

    for path, expected_text in endpoints:
        res = client.get(path)
        assert res.status_code == 200, f"Endpoint {path} failed with status {res.status_code}"
        assert expected_text in res.data, f"Expected text missing on {path}"

def test_reports_excel_and_pdf_exports(auth_admin):
    """Verify that Excel (.xlsx) and PDF (.pdf) reports download with valid binary headers."""
    client = auth_admin

    # Excel export
    res_excel = client.get('/reports/export/department/excel')
    assert res_excel.status_code == 200
    assert "spreadsheetml" in res_excel.content_type
    assert len(res_excel.data) > 1000

    # PDF export
    res_pdf = client.get('/reports/export/department/pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.content_type == "application/pdf"
    assert res_pdf.data.startswith(b'%PDF')

def test_api_health_endpoint(client):
    """Verify REST API health check endpoint."""
    res = client.get('/api/health')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['status'] == 'healthy'
    assert json_data['database_connected'] is True
