from datetime import datetime
from app.database.connection import db_manager
from app.models.entities import Notification

class NotificationService:
    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        session = db_manager.get_session()
        try:
            query = session.query(Notification).filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(read_status=False)
            notifs = query.order_by(Notification.created_at.desc()).limit(50).all()
            return [n.to_dict() for n in notifs]
        finally:
            session.close()

    @staticmethod
    def get_unread_count(user_id):
        session = db_manager.get_session()
        try:
            return session.query(Notification).filter_by(user_id=user_id, read_status=False).count()
        finally:
            session.close()

    @staticmethod
    def mark_as_read(notification_id, user_id):
        session = db_manager.get_session()
        try:
            n = session.query(Notification).filter_by(notification_id=notification_id, user_id=user_id).first()
            if n:
                n.read_status = True
                session.commit()
                return True
            return False
        finally:
            session.close()

    @staticmethod
    def mark_all_as_read(user_id):
        session = db_manager.get_session()
        try:
            session.query(Notification).filter_by(user_id=user_id, read_status=False).update({'read_status': True})
            session.commit()
            return True
        finally:
            session.close()

