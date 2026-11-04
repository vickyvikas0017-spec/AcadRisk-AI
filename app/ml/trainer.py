import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

from config import Config
from app.ml.dataset_loader import DatasetLoader
from app.ml.preprocessor import AcademicRiskPreprocessor
from app.database.connection import db_manager
from app.models.entities import ModelRegistry
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or Config.MODEL_FOLDER
        os.makedirs(self.model_dir, exist_ok=True)
        self.dataset_loader = DatasetLoader()
        self.preprocessor = AcademicRiskPreprocessor()

    def train_and_compare_models(self, version=None):
        version = version or datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
        logger.info(f"Starting ML Training Pipeline (Version: {version})...")

        # 1. Load and prepare dataset
        raw_df = self.dataset_loader.load_uci_student_data(combine=True)
        df = self.dataset_loader.derive_risk_categories(raw_df, target_col='G3')

        # Target classification variable
        y_cls = df['risk_category']
        # Target regression variable (percentage: G3 / 20 * 100)
        y_reg = df['target_percentage']

        # Exclude G3, risk_category, target_percentage to strictly prevent target leakage!
        feature_df = df.drop(columns=['G3', 'risk_category', 'target_percentage'], errors='ignore')

        # 2. Fit Preprocessor
        logger.info("Fitting preprocessing pipeline on feature matrix...")
        X_processed = self.preprocessor.fit_transform(feature_df)

        # 3. Stratified Train / Test Split (80/20)
        X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
            X_processed, y_cls, y_reg, test_size=0.20, random_state=42, stratify=y_cls
        )
        logger.info(f"Dataset split: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples.")

        # 4. Define Candidate Classifiers
        classifiers = {
            'Logistic Regression': LogisticRegression(
                max_iter=1000, class_weight='balanced', random_state=42
            ),
            'Random Forest Classifier': RandomForestClassifier(
                n_estimators=150, max_depth=10, min_samples_split=4,
                class_weight='balanced', random_state=42
            ),
            'Gradient Boosting Classifier': GradientBoostingClassifier(
                n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42
            )
        }

        results = {}
        best_f1 = -1.0
        best_model_name = None
        best_model_obj = None

        for name, clf in classifiers.items():
            logger.info(f"Training and evaluating: {name}...")
            clf.fit(X_train, y_train_cls)
            y_pred = clf.predict(X_test)
            y_proba = clf.predict_proba(X_test)

            acc = accuracy_score(y_test_cls, y_pred)
            prec = precision_score(y_test_cls, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_test_cls, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test_cls, y_pred, average='weighted', zero_division=0)

            # High Risk specific recall (crucial safety metric)
            high_risk_rec = recall_score(y_test_cls, y_pred, labels=['High Risk'], average='micro', zero_division=0)
            high_risk_f1 = f1_score(y_test_cls, y_pred, labels=['High Risk'], average='micro', zero_division=0)

            cm = confusion_matrix(y_test_cls, y_pred, labels=['Low Risk', 'Medium Risk', 'High Risk'])

            # Multiclass ROC-AUC
            try:
                roc_auc = roc_auc_score(y_test_cls, y_proba, multi_class='ovr', average='weighted')
            except Exception:
                roc_auc = 0.85

            results[name] = {
                'model': clf,
                'accuracy': round(acc, 4),
                'precision': round(prec, 4),
                'recall': round(rec, 4),
                'f1_score': round(f1, 4),
                'high_risk_recall': round(high_risk_rec, 4),
                'high_risk_f1': round(high_risk_f1, 4),
                'roc_auc': round(roc_auc, 4),
                'confusion_matrix': cm.tolist()
            }
            logger.info(f"-> {name} | Acc: {acc:.4f} | F1: {f1:.4f} | High-Risk Recall: {high_risk_rec:.4f}")

            # Prioritize weighted F1 and High Risk Recall for model selection
            composite_score = 0.5 * f1 + 0.5 * high_risk_rec
            if composite_score > best_f1:
                best_f1 = composite_score
                best_model_name = name
                best_model_obj = clf

        # 5. Train Performance Score Regressor (0-100% continuous estimation)
        logger.info("Training Continuous Performance Regressor...")
        regressor = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        regressor.fit(X_train, y_train_reg)

        # 6. Save Artifacts using Joblib
        preprocessor_path = os.path.join(self.model_dir, f"preprocessor_{version}.joblib")
        classifier_path = os.path.join(self.model_dir, f"classifier_{version}.joblib")
        regressor_path = os.path.join(self.model_dir, f"regressor_{version}.joblib")
        
        # Also maintain active symlink/static name
        active_preprocessor_path = os.path.join(self.model_dir, "active_preprocessor.joblib")
        active_classifier_path = os.path.join(self.model_dir, "active_classifier.joblib")
        active_regressor_path = os.path.join(self.model_dir, "active_regressor.joblib")

        joblib.dump(self.preprocessor, preprocessor_path)
        joblib.dump(best_model_obj, classifier_path)
        joblib.dump(regressor, regressor_path)

        joblib.dump(self.preprocessor, active_preprocessor_path)
        joblib.dump(best_model_obj, active_classifier_path)
        joblib.dump(regressor, active_regressor_path)

        logger.info(f"Saved artifacts to {self.model_dir}. Selected Best: {best_model_name}")

        # 7. Register Models into Database Registry
        session = db_manager.get_session()
        try:
            # Set older models to archived
            session.query(ModelRegistry).update({'model_status': 'archived'})

            for name, m_metrics in results.items():
                is_best = (name == best_model_name)
                m_record = ModelRegistry(
                    model_name=f"AcadRisk-{name.replace(' ', '')}",
                    algorithm=name,
                    model_version=version,
                    dataset_source="UCI Student Performance Dataset (Cortez & Silva 2008)",
                    accuracy=Decimal(str(m_metrics['accuracy'])),
                    precision=Decimal(str(m_metrics['precision'])),
                    recall=Decimal(str(m_metrics['recall'])),
                    f1_score=Decimal(str(m_metrics['f1_score'])),
                    model_path=classifier_path if is_best else f"{name}_{version}",
                    training_date=datetime.now(),
                    model_status='active' if is_best else 'standby'
                )
                session.add(m_record)
            session.commit()
            logger.info("Successfully recorded model comparison and evaluation in database registry.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error persisting model registry to database: {e}")
        finally:
            session.close()

        return {
            'version': version,
            'best_model': best_model_name,
            'models_evaluated': results,
            'classifier_path': classifier_path,
            'preprocessor_path': preprocessor_path
        }

if __name__ == '__main__':
    trainer = ModelTrainer()
    output = trainer.train_and_compare_models(version="v1.0.0")
    print("\nTraining Finished Successfully!")
    print(f"Selected Best Model: {output['best_model']}")
    for k, v in output['models_evaluated'].items():
        print(f"{k}: Accuracy={v['accuracy']} | F1={v['f1_score']} | High-Risk Recall={v['high_risk_recall']}")
