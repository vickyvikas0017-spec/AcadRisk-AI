from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app.utils.auth_helpers import login_required, role_required
from app.services.import_service import ImportService
from app.services.notification_service import NotificationService
from app.database.connection import db_manager

imports_bp = Blueprint('imports', __name__)

@imports_bp.route('/data-import')
@login_required
@role_required(['ADMIN', 'FACULTY'])
def index():
    batches = ImportService.get_import_history()
    unread_count = NotificationService.get_unread_count(session.get('user_id'))
    return render_template(
        'imports/index.html',
        active_page='imports',
        page_title='Data Import',
        batches=batches,
        unread_count=unread_count,
        db_dialect=db_manager.active_dialect
    )

@imports_bp.route('/data-import/upload', methods=['POST'])
@login_required
@role_required(['ADMIN', 'FACULTY'])
def upload():
    if 'file' not in request.files:
        flash('No file selected for upload.', 'danger')
        return redirect(url_for('imports.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('imports.index'))

    import_type = request.form.get('import_type', 'students')
    atomic = (request.form.get('atomic') == 'true')

    res = ImportService.process_file_import(
        file_storage=file,
        import_type=import_type,
        user_id=session.get('user_id'),
        atomic=atomic
    )

    if res.get('success'):
        flash(f"Import Succeeded: {res['successful_records']} rows inserted into database.", 'success')
    else:
        err_msg = res.get('error', 'Import failed.')
        if res.get('atomic_rollback'):
            flash(f"{err_msg} ({res.get('errors_count')} errors detected)", 'danger')
        else:
            flash(f"Import failed: {err_msg}", 'danger')

    return redirect(url_for('imports.index'))

@imports_bp.route('/data-import/template/<type>')
@login_required
def download_template(type):
    csv_data = ImportService.get_sample_csv(type)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=sample_{type}_template.csv"}
    )

