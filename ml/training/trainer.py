import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from ml.data.dataset import InvoiceDatasetManager
from ml.features.pipeline import MLFeaturePipeline
from ml.models.baseline import LogisticRegressionBaseline
from ml.models.tabular import StrongTabularModel
from ml.models.natural_recovery import NaturalRecoveryEstimator
from ml.models.assisted_recovery import AssistedRecoveryEstimator
from ml.evaluation.metrics import ModelEvaluator
from app.core.logging import logger

_default_artifacts_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "artifacts")
)
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", _default_artifacts_dir)


class ModelTrainer:
    """
    End-to-End RecoverAI Model Trainer & Evaluator.
    Manages data loading, temporal splitting, feature encoding, baseline & tabular model fitting,
    natural recovery estimation, and artifact saving.
    """

    def __init__(self, raw_data_dir: Optional[str] = None, artifacts_dir: str = ARTIFACTS_DIR):
        self.dataset_manager = InvoiceDatasetManager(raw_dir=raw_data_dir)
        self.feature_pipeline = MLFeaturePipeline()
        self.baseline_model = LogisticRegressionBaseline()
        self.tabular_model = StrongTabularModel(model_type="hist_gb")
        self.natural_estimator = NaturalRecoveryEstimator()
        self.assisted_estimator = AssistedRecoveryEstimator()
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def train_and_evaluate(self, window_days: int = 30) -> Dict[str, Any]:
        """
        Execute full training and evaluation workflow.
        """
        logger.info("Starting RecoverAI ML Training & Evaluation Workflow...")

        # 1. Load data & target label
        dataset = self.dataset_manager.load_prepared_dataset(window_days=window_days)

        # 2. Chronological temporal data split
        train_df, val_df, test_df, split_info = self.dataset_manager.temporal_split(dataset)

        # 3. Feature extraction & leakage validation
        X_train_raw, y_train = self.feature_pipeline.extract_raw_features_and_label(train_df)
        X_val_raw, y_val = self.feature_pipeline.extract_raw_features_and_label(val_df)
        X_test_raw, y_test = self.feature_pipeline.extract_raw_features_and_label(test_df)

        # 4. Transform features
        X_train = self.feature_pipeline.fit_transform(X_train_raw)
        X_val = self.feature_pipeline.transform(X_val_raw)
        X_test = self.feature_pipeline.transform(X_test_raw)

        y_train_np = y_train.to_numpy()
        y_val_np = y_val.to_numpy()
        y_test_np = y_test.to_numpy()

        # 5. Fit Baseline Logistic Regression Model
        self.baseline_model.fit(X_train, y_train_np)
        val_probs_baseline = self.baseline_model.predict_proba(X_val)
        test_probs_baseline = self.baseline_model.predict_proba(X_test)

        eval_baseline_val = ModelEvaluator.evaluate(y_val_np, val_probs_baseline)
        eval_baseline_test = ModelEvaluator.evaluate(y_test_np, test_probs_baseline)

        # 6. Fit Stronger Tabular Model (HistGradientBoosting)
        self.tabular_model.fit(X_train, y_train_np)
        val_probs_tabular = self.tabular_model.predict_proba(X_val)
        test_probs_tabular = self.tabular_model.predict_proba(X_test)

        eval_tabular_val = ModelEvaluator.evaluate(y_val_np, val_probs_tabular)
        eval_tabular_test = ModelEvaluator.evaluate(y_test_np, test_probs_tabular)

        # 7. Fit Natural Recovery Estimator
        train_probs_baseline = self.baseline_model.predict_proba(X_train)
        self.natural_estimator.fit(train_probs_baseline, y_train_np)

        # Predict natural recovery on test set
        natural_probs_test = self.natural_estimator.predict_natural_recovery(test_probs_tabular)

        # 8. Save artifacts
        self.baseline_model.save(os.path.join(self.artifacts_dir, "baseline_logistic_regression.joblib"))
        self.tabular_model.save(os.path.join(self.artifacts_dir, "strong_hist_gradient_boosting.joblib"))
        joblib.dump(self.feature_pipeline, os.path.join(self.artifacts_dir, "feature_pipeline.joblib"))
        joblib.dump(self.natural_estimator, os.path.join(self.artifacts_dir, "natural_estimator.joblib"))

        results = {
            "target_window_days": window_days,
            "temporal_splits": split_info,
            "models": {
                "baseline_logistic_regression": {
                    "validation_metrics": eval_baseline_val,
                    "test_metrics": eval_baseline_test,
                },
                "strong_hist_gradient_boosting": {
                    "validation_metrics": eval_tabular_val,
                    "test_metrics": eval_tabular_test,
                }
            },
            "natural_recovery_estimation": {
                "overall_baseline_rate": self.natural_estimator.overall_baseline_rate,
                "test_mean_natural_recovery": float(np.mean(natural_probs_test)),
            }
        }

        logger.info(
            f"Model Training Complete! Test ROC-AUC: "
            f"Baseline={eval_baseline_test['roc_auc']:.4f}, "
            f"Tabular={eval_tabular_test['roc_auc']:.4f}"
        )

        return results
