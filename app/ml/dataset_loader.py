import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatasetLoader:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.join(Config.BASE_DIR, 'datasets')
        self.public_dir = os.path.join(self.data_dir, 'public')
        self.synthetic_dir = os.path.join(self.data_dir, 'synthetic')

    def load_uci_student_data(self, combine=True):
        """
        Loads the official UCI Student Performance dataset.
        Combines Math (student-mat.csv) and Portuguese (student-por.csv)
        or loads math individually.
        """
        mat_path = os.path.join(self.public_dir, 'student-mat.csv')
        por_path = os.path.join(self.public_dir, 'student-por.csv')

        if not os.path.exists(mat_path):
            raise FileNotFoundError(f"UCI dataset not found at {mat_path}. Ensure datasets/public/ is present.")

        df_mat = pd.read_csv(mat_path, sep=';')
        df_mat['subject'] = 'Mathematics'

        if combine and os.path.exists(por_path):
            df_por = pd.read_csv(por_path, sep=';')
            df_por['subject'] = 'Portuguese'
            df = pd.concat([df_mat, df_por], ignore_index=True)
            logger.info(f"Loaded combined UCI dataset: {df.shape[0]} rows across Mathematics and Portuguese.")
        else:
            df = df_mat
            logger.info(f"Loaded UCI Mathematics dataset: {df.shape[0]} rows.")

        return df

    def derive_risk_categories(self, df, target_col='G3'):
        """
        Maps final grade G3 (0-20 scale) to three clinically distinct academic risk tiers:
        - Low Risk: G3 in [14, 20] (70% - 100%) - Student is in good standing
        - Medium Risk: G3 in [10, 13] (50% - 69%) - Vulnerable / border performance
        - High Risk: G3 in [0, 9] (0% - 49%) - High failure risk requiring early intervention
        """
        df = df.copy()
        conditions = [
            (df[target_col] >= 14),
            (df[target_col] >= 10) & (df[target_col] < 14),
            (df[target_col] < 10)
        ]
        choices = ['Low Risk', 'Medium Risk', 'High Risk']
        df['risk_category'] = np.select(conditions, choices, default='Medium Risk')
        
        # Percentage equivalent (0-100%)
        df['target_percentage'] = (df[target_col] / 20.0) * 100.0
        return df

    def generate_synthetic_college_data(self, n_samples=300, random_seed=42):
        """
        Generates realistic synthetic academic data for testing departmental scaling.
        Explicitly marked with is_synthetic=True as per project ethics guidelines.
        """
        np.random.seed(random_seed)
        departments = ['CSE', 'IT', 'ECE', 'ME']
        
        # Correlated feature synthesis
        study_hours = np.random.uniform(2, 25, n_samples)
        attendance_pct = np.clip(np.random.normal(75, 15, n_samples), 30, 100)
        previous_failures = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.75, 0.15, 0.07, 0.03])
        
        # Midterm assessment scores (0-100)
        g1 = np.clip(0.4 * attendance_pct + 1.5 * study_hours - 5 * previous_failures + np.random.normal(20, 8, n_samples), 0, 100)
        g2 = np.clip(0.6 * g1 + 0.3 * attendance_pct - 4 * previous_failures + np.random.normal(10, 6, n_samples), 0, 100)
        
        # Final score G3
        g3 = np.clip(0.5 * g2 + 0.3 * g1 + 0.2 * attendance_pct - 5 * previous_failures + np.random.normal(0, 5, n_samples), 0, 100)
        
        absences = np.clip(np.round((100 - attendance_pct) / 3), 0, 30).astype(int)

        data = {
            'student_id': [f"SYNTH-{i+1:04d}" for i in range(n_samples)],
            'department': np.random.choice(departments, n_samples),
            'studytime': np.clip(np.round(study_hours / 5), 1, 4).astype(int),
            'failures': previous_failures,
            'absences': absences,
            'attendance_pct': np.round(attendance_pct, 1),
            'G1_score': np.round(g1, 1),
            'G2_score': np.round(g2, 1),
            'G3_final': np.round(g3, 1),
            'is_synthetic': True
        }
        df = pd.DataFrame(data)
        
        conditions = [
            (df['G3_final'] >= 70),
            (df['G3_final'] >= 50) & (df['G3_final'] < 70),
            (df['G3_final'] < 50)
        ]
        df['risk_category'] = np.select(conditions, ['Low Risk', 'Medium Risk', 'High Risk'], default='Medium Risk')
        return df
