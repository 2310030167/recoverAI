import joblib
import numpy as np
from typing import Dict, Any, Optional
from sklearn.linear_model import LogisticRegression
from app.core.logging import logger


class LogisticRegressionBaseline:
    """
    Step 5: Baseline Recovery Prediction Model using Logistic Regression.
    Provides probability estimates P(R | X).
    """

    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        self.model = LogisticRegression(
            C=C,
            max_iter=max_iter,
            class_weight="balanced",
            random_state=random_state,
            solver="lbfgs"
        )
        self.is_fitted: bool = False

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "LogisticRegressionBaseline":
        """
        Fit baseline model on training features and binary target labels.
        """
        logger.info(f"Fitting Logistic Regression Baseline on shape {X_train.shape}...")
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict recovery probabilities P(R | X). Returns 1D numpy array of probabilities.
        """
        if not self.is_fitted:
            raise RuntimeError("LogisticRegressionBaseline must be fitted before predict_proba().")
        return self.model.predict_proba(X)[:, 1]

    def save(self, filepath: str) -> None:
        joblib.dump(self.model, filepath)
        logger.info(f"Saved Logistic Regression Baseline artifact to {filepath}")

    def load(self, filepath: str) -> "LogisticRegressionBaseline":
        self.model = joblib.load(filepath)
        self.is_fitted = True
        return self
