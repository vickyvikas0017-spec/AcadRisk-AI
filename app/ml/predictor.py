import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func

from config import Config
from app.database.connection import db_manager
from app.models.entities import (
    Student, Course, Semester, Enrollment, AttendanceRecord, AttendanceSession,
    Assessment, Mark, AcademicHistory, Prediction, PredictionRun, Notification, RiskThreshold,
    ModelRegistry
)
from app.ml.preprocessor import AcademicRiskPreprocessor
import logging

logger = logging.getLogger(__name__)

class AcademicRiskPredictor:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or Config.MODEL_FOLDER
        self.classifier = None
        self.regressor = None
        self.preprocessor = None
        self._load_active_models()

    def _load_active_models(self):
        cls_path = os.path.join(self.model_dir, "active_classifier.joblib")
        reg_path = os.path.join(self.model_dir, "active_regressor.joblib")
        prep_path = os.path.join(self.model_dir, "active_preprocessor.joblib")

        if os.path.exists(cls_path) and os.path.exists(prep_path):
            self.classifier = joblib.load(cls_path)
            self.preprocessor = joblib.load(prep_path)
            if os.path.exists(reg_path):
                self.regressor = joblib.load(reg_path)
            logger.info("Successfully loaded active ML models and preprocessor.")
        else:
            logger.warning(f"Active model artifacts not found in {self.model_dir}. Please run trainer first.")

    def extract_student_features(self, student_id, course_id, semester_id):
        """
        Extracts genuine institutional metrics from the database for feature vector construction.
        """
        session = db_manager.get_session()
        try:
            # 1. Find enrollment
            enrollment = session.query(Enrollment).filter_by(
                student_id=student_id,
                course_id=course_id,
                semester_id=semester_id
            ).first()

            if not enrollment:
                return None, "Student is not enrolled in the specified course and semester."

            # 2. Extract assessment marks
            marks = session.query(Mark, Assessment).join(
                Assessment, Mark.assessment_id == Assessment.assessment_id
            ).filter(Mark.enrollment_id == enrollment.enrollment_id).all()

            g1_pct = None
            g2_pct = None

            for m, a in marks:
                pct = (float(m.obtained_marks) / float(a.maximum_marks)) * 100.0 if a.maximum_marks > 0 else 0
                if '1' in a.assessment_name or a.assessment_type == 'Internal 1':
                    g1_pct = pct
                elif '2' in a.assessment_name or a.assessment_type == 'Internal 2' or 'Mid' in a.assessment_name:
                    g2_pct = pct
                elif g1_pct is None:
                    g1_pct = pct
                elif g2_pct is None:
                    g2_pct = pct

            # Defaults if assessments haven't occurred yet
            if g1_pct is None and g2_pct is None:
                # Early semester estimation: check attendance
                g1_pct = 60.0
                g2_pct = 60.0
            elif g2_pct is None:
                g2_pct = g1_pct
            elif g1_pct is None:
                g1_pct = g2_pct

            # 3. Extract Attendance Absences
            att_records = session.query(AttendanceRecord).filter_by(enrollment_id=enrollment.enrollment_id).all()
            total_classes = len(att_records)
            absent_classes = sum(1 for r in att_records if r.attendance_status in ('Absent', 'Late'))
            present_classes = sum(1 for r in att_records if r.attendance_status == 'Present')
            attendance_pct = (present_classes / total_classes * 100.0) if total_classes > 0 else 85.0

            # 4. Extract Historical Failures
            past_failures = session.query(AcademicHistory).filter_by(
                student_id=student_id,
                result_status='Fail'
            ).count()

            # Student details
            student = session.query(Student).get(student_id)
            course = session.query(Course).get(course_id)

            feature_data = {
                'g1_pct': round(g1_pct, 1),
                'g2_pct': round(g2_pct, 1),
                'absent_classes': absent_classes,
                'total_classes': total_classes,
                'attendance_pct': round(attendance_pct, 1),
                'past_failures': past_failures,
                'student_name': student.student_name if student else 'Unknown',
                'registration_number': student.registration_number if student else 'Unknown',
                'course_name': course.course_name if course else 'Unknown'
            }
            return feature_data, None
        finally:
            session.close()

    def predict_risk(self, student_id, course_id, semester_id, run_id=None, save_db=True):
        if not self.classifier or not self.preprocessor:
            self._load_active_models()
            if not self.classifier:
                raise RuntimeError("No active ML model loaded. Please train or activate a model first.")

        feat, err = self.extract_student_features(student_id, course_id, semester_id)
        if err:
            return {'success': False, 'error': err}

        # Build standardized feature vector
        feature_df = AcademicRiskPreprocessor.map_college_record_to_features(
            g1_pct=feat['g1_pct'],
            g2_pct=feat['g2_pct'],
            absent_sessions=feat['absent_classes'],
            past_failures=feat['past_failures']
        )

        # Transform features
        X_vec = self.preprocessor.transform(feature_df)

        # Classification prediction & class probabilities
        pred_category = self.classifier.predict(X_vec)[0]
        classes = list(self.classifier.classes_)
        probas = self.classifier.predict_proba(X_vec)[0]
        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probas)}
        main_prob = prob_dict.get(pred_category, 0.75)

        # Regression prediction (predicted marks percentage)
        predicted_marks = 50.0
        if self.regressor:
            predicted_marks = float(np.clip(self.regressor.predict(X_vec)[0], 0.0, 100.0))

        # Check Department / Course custom threshold overrides if available
        session = db_manager.get_session()
        try:
            custom_thresh = session.query(RiskThreshold).filter(
                (RiskThreshold.course_id == course_id) | (RiskThreshold.course_id == None)
            ).order_by(RiskThreshold.course_id.desc()).first()

            if custom_thresh:
                high_th = float(custom_thresh.high_risk_threshold)
                med_th = float(custom_thresh.medium_risk_threshold)
                if predicted_marks < high_th:
                    pred_category = 'High Risk'
                elif predicted_marks < med_th and pred_category != 'High Risk':
                    pred_category = 'Medium Risk'
        finally:
            session.close()

        # Identify contributing factors
        contributing_factors = []
        if feat['attendance_pct'] < 75.0:
            contributing_factors.append(f"Low Course Attendance: {feat['attendance_pct']}% ({feat['absent_classes']} missed sessions)")
        if feat['g1_pct'] < 50.0:
            contributing_factors.append(f"Critical score in Assessment 1: {feat['g1_pct']}%")
        if feat['g2_pct'] < 50.0:
            contributing_factors.append(f"Critical score in Assessment 2 / Midterm: {feat['g2_pct']}%")
        if feat['past_failures'] > 0:
            contributing_factors.append(f"Prior course backlogs / failures: {feat['past_failures']} recorded")
        if not contributing_factors:
            contributing_factors.append("Consistent continuous assessment scores and regular class attendance.")

        prediction_id = None
        if save_db:
            session = db_manager.get_session()
            try:
                pred_record = Prediction(
                    run_id=run_id,
                    student_id=student_id,
                    course_id=course_id,
                    semester_id=semester_id,
                    predicted_marks=Decimal(str(round(predicted_marks, 2))),
                    risk_category=pred_category,
                    risk_probability=Decimal(str(round(main_prob, 4))),
                    prediction_date=datetime.now()
                )
                session.add(pred_record)
                session.flush()
                prediction_id = pred_record.prediction_id

                # Trigger early warning notification for High Risk
                if pred_category == 'High Risk':
                    student = session.query(Student).get(student_id)
                    if student and student.user_id:
                        # Check for existing unread alert
                        existing_notif = session.query(Notification).filter_by(
                            user_id=student.user_id,
                            notification_type='High Risk Alert',
                            read_status=False
                        ).first()
                        if not existing_notif:
                            notif = Notification(
                                user_id=student.user_id,
                                notification_type='High Risk Alert',
                                message=f"Early Warning: High academic risk detected in {feat['course_name']} (Predicted: {round(predicted_marks, 1)}%, Probability: {round(main_prob*100, 1)}%). Recommended: Schedule faculty counselling.",
                                read_status=False,
                                created_at=datetime.now()
                            )
                            session.add(notif)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error persisting prediction: {e}")
            finally:
                session.close()

        return {
            'success': True,
            'prediction_id': prediction_id,
            'student_id': student_id,
            'student_name': feat['student_name'],
            'registration_number': feat['registration_number'],
            'course_id': course_id,
            'course_name': feat['course_name'],
            'risk_category': pred_category,
            'risk_probability': round(main_prob * 100, 1),
            'predicted_marks': round(predicted_marks, 1),
            'probability_breakdown': prob_dict,
            'contributing_factors': contributing_factors,
            'features_used': feat
        }

    def run_batch_predictions(self, course_id=None, semester_id=None, user_id=None):
        """
        Executes genuine ML batch inference for all students enrolled in specified scope.
        """
        session = db_manager.get_session()
        try:
            query = session.query(Enrollment)
            if course_id:
                query = query.filter_by(course_id=course_id)
            if semester_id:
                query = query.filter_by(semester_id=semester_id)

            enrollments = query.all()
            if not enrollments:
                return {'success': False, 'message': 'No enrollments found matching the criteria.'}

            # Extract raw ID tuples so inner session calls do not conflict with detached instances
            enr_tuples = [(e.student_id, e.course_id, e.semester_id) for e in enrollments]

            # Create prediction run entry
            active_model = session.query(ModelRegistry).filter_by(model_status='active').first()
            model_id = active_model.model_id if active_model else 1

            run = PredictionRun(
                model_id=model_id,
                initiated_by=user_id,
                start_time=datetime.now(),
                total_predictions=len(enr_tuples),
                run_status='in_progress'
            )
            session.add(run)
            session.commit()
            run_id = run.run_id

            results = []
            risk_counts = {'Low Risk': 0, 'Medium Risk': 0, 'High Risk': 0}

            for s_id, c_id, sem_id in enr_tuples:
                res = self.predict_risk(
                    student_id=s_id,
                    course_id=c_id,
                    semester_id=sem_id,
                    run_id=run_id,
                    save_db=True
                )
                if res.get('success'):
                    cat = res['risk_category']
                    risk_counts[cat] = risk_counts.get(cat, 0) + 1
                    results.append(res)

            # Update run completion
            run.completion_time = datetime.now()
            run.run_status = 'completed'
            session.commit()

            return {
                'success': True,
                'run_id': run_id,
                'total_analyzed': len(results),
                'risk_distribution': risk_counts,
                'results': results
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error in batch predictions: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            session.close()

predictor = AcademicRiskPredictor()
