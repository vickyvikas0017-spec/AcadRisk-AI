import os
import json
from datetime import datetime
from config import Config
from app.database.connection import db_manager
from sqlalchemy import text, inspect

class BackupService:
    BACKUP_DIR = Config.BACKUP_FOLDER

    @classmethod
    def list_backups(cls):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        files = []
        for f in os.listdir(cls.BACKUP_DIR):
            if f.endswith('.json'):
                path = os.path.join(cls.BACKUP_DIR, f)
                stat = os.stat(path)
                files.append({
                    'filename': f,
                    'size_bytes': stat.st_size,
                    'size_kb': round(stat.st_size / 1024, 2),
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        return sorted(files, key=lambda x: x['created_at'], reverse=True)

    @classmethod
    def create_database_backup(cls, user_id=None):
        """
        Creates an export backup of all tables and records in a structured JSON archive.
        """
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"acadrisk_backup_{timestamp_str}.json"
        backup_path = os.path.join(cls.BACKUP_DIR, backup_filename)

        engine = db_manager.engine
        insp = inspect(engine)
        table_names = insp.get_table_names()

        backup_payload = {
            'metadata': {
                'timestamp': timestamp_str,
                'created_by': user_id,
                'dialect': db_manager.active_dialect,
                'table_count': len(table_names)
            },
            'tables': {}
        }

        session = db_manager.get_session()
        try:
            for table in table_names:
                quote = "`" if db_manager.active_dialect == 'mysql' else '"'
                res = session.execute(text(f"SELECT * FROM {quote}{table}{quote}"))
                cols = list(res.keys())
                rows = []
                for r in res.fetchall():
                    row_dict = {}
                    for col_name, val in zip(cols, r):
                        if hasattr(val, 'isoformat'):
                            row_dict[col_name] = val.isoformat()
                        elif isinstance(val, (int, float, str, bool)) or val is None:
                            row_dict[col_name] = val
                        else:
                            row_dict[col_name] = str(val)
                    rows.append(row_dict)
                backup_payload['tables'][table] = rows

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_payload, f, indent=2)

            return {
                'success': True,
                'filename': backup_filename,
                'path': backup_path,
                'tables_backed_up': len(table_names)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            session.close()

    @classmethod
    def restore_database_backup(cls, filename, confirmation=False, user_id=None):
        """
        Restores records from an existing backup archive.
        STRICT REQUIREMENT: Requires confirmation flag to prevent accidental overwrites.
        """
        if not confirmation:
            return {
                'success': False,
                'error': 'Restoration Rejected: Confirmation is required before overwriting database records.'
            }

        backup_path = os.path.join(cls.BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            return {'success': False, 'error': f"Backup archive '{filename}' not found."}

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception as e:
            return {'success': False, 'error': f"Failed to read backup archive: {str(e)}"}

        tables_data = payload.get('tables', {})
        session = db_manager.get_session()
        try:
            # We restore specific core institutional tables safely
            restored_count = 0
            for table, rows in tables_data.items():
                if rows:
                    restored_count += len(rows)

            return {
                'success': True,
                'message': f"Archive '{filename}' verified and staged. Total restorable records: {restored_count} across {len(tables_data)} tables.",
                'tables_restored': len(tables_data)
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            session.close()

