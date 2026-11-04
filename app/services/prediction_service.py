from datetime import datetime
from app.database.connection import db_manager
from app.models.entities import Prediction, PredictionRun, Student, Course, Semester
from app.ml.predictor import predictor

class PredictionService:
    @staticmethod
    def get_predictions(limit=50, risk_category=None, student_id=None, course_id=None):
        session = db_manager.get_session()
        try:
            query = session.query(Prediction)
            if risk_category:
                query = query.filter_by(risk_category=risk_category)
            if student_id:
                query = query.filter_by(student_id=student_id)
            if course_id:
                query = query.filter_by(course_id=course_id)
            preds = query.order_by(Prediction.prediction_date.desc()).limit(limit).all()
            return [p.to_dict() for p in preds]
        finally:
            session.close()

    @staticmethod
    def run_prediction(student_id, course_id, semester_id, user_id=None):
        return predictor.predict_risk(student_id, course_id, semester_id, save_db=True)

    @staticmethod
    def run_batch_predictions(course_id=None, semester_id=None, user_id=None):
        return predictor.run_batch_predictions(course_id, semester_id, user_id)

