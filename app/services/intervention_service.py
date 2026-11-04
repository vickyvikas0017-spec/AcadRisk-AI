from datetime import datetime, date
from app.database.connection import db_manager
from app.models.entities import Intervention, Student, Faculty, Prediction, AuditLog

class InterventionService:
    @staticmethod
    def get_interventions(student_id=None, faculty_id=None, status=None):
        session = db_manager.get_session()
        try:
            query = session.query(Intervention)
            if student_id:
                query = query.filter_by(student_id=student_id)
            if faculty_id:
                query = query.filter_by(faculty_id=faculty_id)
            if status:
                query = query.filter_by(intervention_status=status)
            intervs = query.order_by(Intervention.intervention_id.desc()).all()
            return [i.to_dict() for i in intervs]
        finally:
            session.close()

    @staticmethod
    def create_intervention(student_id, faculty_id, intervention_type, description, follow_up_date=None, prediction_id=None, user_id=None):
        session = db_manager.get_session()
        try:
            parsed_date = None
            if follow_up_date:
                parsed_date = datetime.strptime(follow_up_date, '%Y-%m-%d').date() if isinstance(follow_up_date, str) else follow_up_date

            interv = Intervention(
                prediction_id=prediction_id,
                student_id=student_id,
                faculty_id=faculty_id,
                intervention_type=intervention_type,
                intervention_description=description.strip(),
                follow_up_date=parsed_date,
                intervention_status='Pending'
            )
            session.add(interv)
            session.flush()

            audit = AuditLog(
                user_id=user_id,
                action_type='INSERT',
                table_name='interventions',
                record_id=interv.intervention_id,
                old_values=None,
                new_values=f'{{"student_id": {student_id}, "type": "{intervention_type}"}}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return interv.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_intervention(intervention_id, status, outcome=None, user_id=None):
        session = db_manager.get_session()
        try:
            interv = session.query(Intervention).get(intervention_id)
            if not interv:
                return None, "Intervention not found."

            old_status = interv.intervention_status
            interv.intervention_status = status
            if outcome:
                interv.outcome = outcome.strip()

            audit = AuditLog(
                user_id=user_id,
                action_type='UPDATE',
                table_name='interventions',
                record_id=intervention_id,
                old_values=f'{{"status": "{old_status}"}}',
                new_values=f'{{"status": "{status}"}}',
                timestamp=datetime.now()
            )
            session.add(audit)
            session.commit()
            return interv.to_dict(), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

