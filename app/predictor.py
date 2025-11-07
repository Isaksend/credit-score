import os

import joblib
import pandas as pd
import numpy as np
import json
from pathlib import Path


class CreditScoringPredictor:
    """Credit scoring prediction class"""

    def __init__(self, models_dir='models'):
        """Load all models"""
        self.models_dir = Path(models_dir)

        print("Loading models...")

        # Load models
        self.logistic_model = joblib.load(self.models_dir / 'logistic_model.joblib')
        self.linear_model = joblib.load(self.models_dir / 'linear_regression.joblib')
        self.scaler = joblib.load(self.models_dir / 'scaler.joblib')
        self.label_encoder = joblib.load(self.models_dir / 'label_encoder.joblib')

        # Load metadata
        with open(os.path.join(models_dir, 'model_metadata.json')) as f:
            self.metadata = json.load(f)
        with open(os.path.join(models_dir, 'feature_means.json')) as f:
            self.feature_means = json.load(f)

        self.features = self.feature_means['features']

        print(f"✅ Models loaded successfully!")
        print(f"   Features: {len(self.features)}")

    def predict_full(self, client_data: dict) -> dict:
        """Complete prediction"""
        # Convert to DataFrame
        df = pd.DataFrame([client_data])[self.features]
        print("ПОДАЕМ В МОДЕЛЬ:")
        print(df.T)  # Печатает все 84 признака и значения

        # Ensure all features present
        for feature in self.features:
            if feature not in df.columns:
                df[feature] = 0

        # Select features in correct order
        df = df[self.features]

        # Scale
        X_scaled = self.scaler.transform(df)

        # Predict default
        default_proba = self.logistic_model.predict_proba(X_scaled)[0][1]
        default_class = self.logistic_model.predict(X_scaled)[0]

        # Predict score
        credit_score = self.linear_model.predict(X_scaled)[0]

        # Risk level
        if default_proba < 0.3:
            risk_level = "Low"
            decision = "APPROVE"
        elif default_proba < 0.5:
            risk_level = "Medium"
            decision = "REVIEW"
        else:
            risk_level = "High"
            decision = "REJECT"

        return {
            'default_probability': round(float(default_proba) * 100, 2),
            'default_class': int(default_class),
            'risk_level': risk_level,
            'decision': decision,
            'credit_score': round(float(credit_score), 2),
            'score_range': '300-800'
        }

    def get_model_info(self) -> dict:
        """Get model metadata"""
        return self.metadata
