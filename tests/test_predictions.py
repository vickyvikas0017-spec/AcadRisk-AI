import pytest
from app.ml.predictor import predictor
from app.database.connection import db_manager
from app.models.entities import Prediction, Notification

def test_single_prediction_low_risk():
    """Verify inference for a high-performing student produces Low Risk."""
    # Student 1 (John Doe) has high assessment marks and regular attendance
    res = predictor.predict_risk(student_id=1, course_id=1, semester_id=1, save_db=True)
    assert res['success'] is True
    assert res['risk_category'] in ('Low Risk', 'Medium Risk')
    assert res['predicted_marks'] >= 60.0
    assert len(res['contributing_factors']) > 0

def test_single_prediction_high_risk_and_alert():
    """Verify inference for low-performing student produces High Risk and creates alert."""
    # Student 3 (Raj Sharma) has 20% attendance and low assessment marks
    res = predictor.predict_risk(student_id=3, course_id=1, semester_id=1, save_db=True)
    assert res['success'] is True
    assert res['risk_category'] == 'High Risk'
    assert res['predicted_marks'] < 50.0

    # Verify notification created
    session = db_manager.get_session()
    try:
        notif = session.query(Notification).filter_by(
            user_id=7,  # Raj Sharma's user_id
            notification_type='High Risk Alert'
        ).first()
        assert notif is not None
        assert "High academic risk detected" in notif.message
    finally:
        session.close()

def test_batch_prediction_execution():
    """Verify batch predictions run across all enrolled students."""
    batch_res = predictor.run_batch_predictions(user_id=1)
    assert batch_res['success'] is True
    assert batch_res['total_analyzed'] > 0
    assert 'High Risk' in batch_res['risk_distribution']
    assert 'Low Risk' in batch_res['risk_distribution']

