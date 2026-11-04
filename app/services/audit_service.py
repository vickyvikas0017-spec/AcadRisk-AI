from app.database.connection import db_manager
from app.models.entities import AuditLog, User

class AuditService:
    @staticmethod
    def get_audit_logs(table_name=None, action_type=None, limit=100):
        session = db_manager.get_session()
        try:
            query = session.query(AuditLog)
            if table_name:
                query = query.filter(AuditLog.table_name == table_name)
            if action_type:
                query = query.filter(AuditLog.action_type == action_type)
            logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return [l.to_dict() for l in logs]
        finally:
            session.close()

