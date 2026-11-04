import os
import pytest
import joblib
from app.ml.dataset_loader import DatasetLoader
from app.ml.preprocessor import AcademicRiskPreprocessor
from config import Config

def test_uci_dataset_loading():
    """Verify loading and schema of UCI Student Performance dataset."""
    loader = DatasetLoader()
    df = loader.load_uci_student_data(combine=True)
    assert df.shape[0] >= 395
    assert 'G1' in df.columns
    assert 'G2' in df.columns
    assert 'G3' in df.columns
    assert 'absences' in df.columns
    assert 'failures' in df.columns

def test_risk_category_derivation_and_no_target_leakage():
    """Verify target derivation and that G3 is never used as an input feature."""
    loader = DatasetLoader()
    raw_df = loader.load_uci_student_data(combine=False)
    df = loader.derive_risk_categories(raw_df, target_col='G3')
    
    assert 'risk_category' in df.columns
    assert set(df['risk_category'].unique()).issubset({'Low Risk', 'Medium Risk', 'High Risk'})

    # Target leakage check: Preprocessor input feature list must NEVER include 'G3'
    preprocessor = AcademicRiskPreprocessor()
    assert 'G3' not in preprocessor.NUMERIC_FEATURES
    assert 'G3' not in preprocessor.CATEGORICAL_FEATURES

def test_feature_preprocessing_pipeline():
    """Verify transforming features through Scikit-Learn ColumnTransformer."""
    preprocessor = AcademicRiskPreprocessor()
    sample_feat = AcademicRiskPreprocessor.map_college_record_to_features(
        g1_pct=85.0,
        g2_pct=80.0,
        absent_sessions=2,
        past_failures=0
    )
    # Fit & Transform
    X_mat = preprocessor.fit_transform(sample_feat)
    assert X_mat.shape[0] == 1
    assert X_mat.shape[1] > 0

def test_model_artifacts_loading():
    """Verify trained joblib model artifacts exist and load properly."""
    cls_path = os.path.join(Config.MODEL_FOLDER, "active_classifier.joblib")
    prep_path = os.path.join(Config.MODEL_FOLDER, "active_preprocessor.joblib")
    reg_path = os.path.join(Config.MODEL_FOLDER, "active_regressor.joblib")

    assert os.path.exists(cls_path), "active_classifier.joblib artifact missing."
    assert os.path.exists(prep_path), "active_preprocessor.joblib artifact missing."
    assert os.path.exists(reg_path), "active_regressor.joblib artifact missing."

    model = joblib.load(cls_path)
    assert hasattr(model, 'predict')
    assert hasattr(model, 'predict_proba')

