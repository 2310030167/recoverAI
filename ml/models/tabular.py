import joblib
import numpy as np
from typing import Dict, Any, Optional
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from app.core.logging import logger


class StrongTabularModel:
    """
    Step 6: Stronger Tabular Recovery Prediction Model using HistGradientBoosting
    or RandomForest Classifier.
    """

    def __init__(self, model_type: str = "hist_gb", random_state: int = 42):
        self.model_type = model_type
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                class_weight="balanced",
                random_state=random_state,
                n_jobs=-1
            )
        else:
            self.model = HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=random_state,
                class_weight="balanced"
            )
        self.is_fitted: bool = False

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "StrongTabularModel":
        """
        Fit stronger tabular model on training dataset.
        """
        logger.info(f"Fitting Strong Tabular Model ({self.model_type}) on shape {X_train.shape}...")
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict recovery probabilities P(R | X). Returns 1D array of probabilities.
        """
        if not self.is_fitted:
            raise RuntimeError("StrongTabularModel must be fitted before calling predict_proba().")
        return self.model.predict_proba(X)[:, 1]

    def save(self, filepath: str) -> None:
        joblib.dump(self.model, filepath)
        logger.info(f"Saved Strong Tabular Model artifact to {filepath}")

    def load(self, filepath: str) -> "StrongTabularModel":
        self.model = joblib.load(filepath)
        self.is_fitted = True
        return self
