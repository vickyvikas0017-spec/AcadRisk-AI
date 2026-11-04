import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class AcademicRiskPreprocessor:
    NUMERIC_FEATURES = [
        'G1',           # First internal assessment score (scaled to 0-20)
        'G2',           # Second internal assessment score (scaled to 0-20)
        'absences',     # Number of missed sessions / absences
        'failures',     # Number of previous course failures
        'studytime',    # Weekly study hours category (1 to 4)
        'age',          # Student age
        'Medu',         # Parent education
        'health'        # Health rating (1-5)
    ]

    CATEGORICAL_FEATURES = [
        'schoolsup',    # Institutional academic support
        'famsup',       # Family support
        'paid',         # Extra tutoring / support
        'higher',       # Plans for higher studies
        'internet'      # Internet access
    ]

    def __init__(self):
        self.pipeline = None
        self.feature_names = None
        self._build_pipeline()

    def _build_pipeline(self):
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='no')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        self.pipeline = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.NUMERIC_FEATURES),
                ('cat', categorical_transformer, self.CATEGORICAL_FEATURES)
            ]
        )

    def fit(self, X):
        X_clean = self._validate_and_impute_missing(X)
        self.pipeline.fit(X_clean)
        return self

    def transform(self, X):
        X_clean = self._validate_and_impute_missing(X)
        return self.pipeline.transform(X_clean)

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def _validate_and_impute_missing(self, df):
        """Ensures all expected feature columns exist with reasonable defaults."""
        df_out = df.copy()
        
        # Ensure numeric features exist
        defaults_numeric = {
            'G1': 10.0,
            'G2': 10.0,
            'absences': 4.0,
            'failures': 0,
            'studytime': 2,
            'age': 20,
            'Medu': 2,
            'health': 3
        }
        for col, default_val in defaults_numeric.items():
            if col not in df_out.columns:
                df_out[col] = default_val
            else:
                df_out[col] = pd.to_numeric(df_out[col], errors='coerce').fillna(default_val)

        # Ensure categorical features exist
        defaults_categorical = {
            'schoolsup': 'no',
            'famsup': 'yes',
            'paid': 'no',
            'higher': 'yes',
            'internet': 'yes'
        }
        for col, default_val in defaults_categorical.items():
            if col not in df_out.columns:
                df_out[col] = default_val
            else:
                df_out[col] = df_out[col].fillna(default_val).astype(str)

        return df_out[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]

    @staticmethod
    def map_college_record_to_features(g1_pct, g2_pct, absent_sessions, past_failures=0, study_hours_category=2):
        """
        Maps institutional college metrics (percentages, absence counts, failures)
        into the standardized UCI feature schema (0-20 scale for G1 and G2).
        """
        g1_uci = (float(g1_pct) / 100.0) * 20.0 if g1_pct is not None else 10.0
        g2_uci = (float(g2_pct) / 100.0) * 20.0 if g2_pct is not None else g1_uci
        
        return pd.DataFrame([{
            'G1': np.clip(g1_uci, 0.0, 20.0),
            'G2': np.clip(g2_uci, 0.0, 20.0),
            'absences': max(0, int(absent_sessions)),
            'failures': max(0, int(past_failures)),
            'studytime': int(study_hours_category),
            'age': 20,
            'Medu': 3,
            'health': 4,
            'schoolsup': 'yes' if past_failures > 0 else 'no',
            'famsup': 'yes',
            'paid': 'no',
            'higher': 'yes',
            'internet': 'yes'
        }])

