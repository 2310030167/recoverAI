import os
import sys
import pytest
import numpy as np
import pandas as pd

from ml.data.dataset import InvoiceDatasetManager
from ml.features.pipeline import MLFeaturePipeline
from ml.models.baseline import LogisticRegressionBaseline
from ml.models.tabular import StrongTabularModel
from ml.models.natural_recovery import NaturalRecoveryEstimator
from ml.models.assisted_recovery import AssistedRecoveryEstimator
from ml.evaluation.metrics import ModelEvaluator
from app.services.leakage_validator import LeakageValidator, DataLeakageError
from app.schemas.canonical import ActionType


@pytest.fixture
def dataset_manager():
    return InvoiceDatasetManager()


@pytest.fixture
def sample_dataset(dataset_manager):
    return dataset_manager.load_prepared_dataset(window_days=30)


def test_censoring_detection_and_label_construction(sample_dataset):
    """
    Task 10 Test: Verify right-censoring detection, observable window calculation,
    and valid 3-class target label construction.
    """
    assert "censoring_class" in sample_dataset.columns
    assert "recovered_within_window" in sample_dataset.columns

    censoring_classes = set(sample_dataset["censoring_class"].unique())
    assert censoring_classes.issubset({"OBSERVABLE_POSITIVE", "OBSERVABLE_NEGATIVE", "RIGHT_CENSORED"})

    # Check label mapping
    assert (sample_dataset[sample_dataset["censoring_class"] == "OBSERVABLE_POSITIVE"]["recovered_within_window"] == 1).all()
    assert (sample_dataset[sample_dataset["censoring_class"] == "OBSERVABLE_NEGATIVE"]["recovered_within_window"] == 0).all()
    assert (sample_dataset[sample_dataset["censoring_class"] == "RIGHT_CENSORED"]["recovered_within_window"] == -1).all()


def test_temporal_data_split_excluding_censored(dataset_manager, sample_dataset):
    """
    Task 10 Test: Verify chronological temporal data split excludes RIGHT_CENSORED observations
    from supervised training, validation, and test evaluation sets.
    """
    train_df, val_df, test_df, split_info = dataset_manager.temporal_split(sample_dataset)
    
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0
    
    # Assert zero censored records in supervised splits
    assert (train_df["recovered_within_window"] == -1).sum() == 0
    assert (val_df["recovered_within_window"] == -1).sum() == 0
    assert (test_df["recovered_within_window"] == -1).sum() == 0

    # Chronological integrity check
    assert train_df["due_in_date"].max() <= val_df["due_in_date"].min()
    assert val_df["due_in_date"].max() <= test_df["due_in_date"].min()


def test_historical_customer_feature_generation(sample_dataset):
    """
    Task 10 Test: Verify legitimate point-in-time historical customer feature generation
    without future data leakage.
    """
    pipeline = MLFeaturePipeline()
    X_raw, y = pipeline.extract_raw_features_and_label(sample_dataset)

    # Check enhanced historical customer features exist
    hist_cols = [
        "cust_historical_invoice_count", "cust_historical_avg_amount",
        "cust_historical_avg_delay", "cust_historical_late_rate", "cust_recency_days"
    ]
    for col in hist_cols:
        assert col in X_raw.columns

    # Verify zero leakage
    for forbidden in ["clear_date", "days_to_pay", "revenue", "churn_date"]:
        assert forbidden not in X_raw.columns


def test_time_to_recovery_calculation(sample_dataset):
    """
    Task 10 Test: Verify time-to-recovery delay calculation (clear_date - due_in_date).
    """
    cleared = sample_dataset[sample_dataset["clear_date"].notna()].copy()
    delays = (cleared["clear_date"] - cleared["due_in_date"]).dt.days
    
    assert len(delays) > 0
    assert np.isnan(delays.values).sum() == 0


def test_model_training_and_prediction_shape(sample_dataset):
    """
    Task 10 Test: Test fitting baseline and tabular ML models, prediction output shapes, and probability bounds.
    """
    manager = InvoiceDatasetManager()
    pipeline = MLFeaturePipeline()

    train_df, val_df, _, _ = manager.temporal_split(sample_dataset)
    X_train_raw, y_train = pipeline.extract_raw_features_and_label(train_df)
    X_val_raw, y_val = pipeline.extract_raw_features_and_label(val_df)

    X_train = pipeline.fit_transform(X_train_raw)
    X_val = pipeline.transform(X_val_raw)

    # 1. Baseline Model
    baseline = LogisticRegressionBaseline()
    baseline.fit(X_train, y_train.to_numpy())
    probs_baseline = baseline.predict_proba(X_val)

    assert isinstance(probs_baseline, np.ndarray)
    assert probs_baseline.ndim == 1
    assert len(probs_baseline) == len(val_df)
    assert np.all((probs_baseline >= 0.0) & (probs_baseline <= 1.0))

    # 2. Strong Tabular Model
    tabular = StrongTabularModel(model_type="hist_gb")
    tabular.fit(X_train, y_train.to_numpy())
    probs_tabular = tabular.predict_proba(X_val)

    assert isinstance(probs_tabular, np.ndarray)
    assert probs_tabular.ndim == 1
    assert len(probs_tabular) == len(val_df)
    assert np.all((probs_tabular >= 0.0) & (probs_tabular <= 1.0))


def test_evaluation_metrics():
    """
    Task 10 Test: Test evaluation metric computations including majority baseline accuracy.
    """
    y_true = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    y_prob = np.array([0.9, 0.8, 0.2, 0.1, 0.7, 0.4, 0.85, 0.05])

    metrics = ModelEvaluator.evaluate(y_true, y_prob)

    assert "accuracy" in metrics
    assert "majority_baseline_accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "brier_score" in metrics
    assert metrics["precision"] > 0.8
    assert metrics["roc_auc"] > 0.9


def test_natural_and_assisted_recovery_estimators():
    """
    Task 10 Test: Test Natural and Assisted Recovery Estimators.
    """
    train_probs = np.array([0.1, 0.3, 0.5, 0.7, 0.9] * 20)
    y_train = np.array([0, 0, 1, 1, 1] * 20)

    natural_est = NaturalRecoveryEstimator()
    natural_est.fit(train_probs, y_train)

    test_probs = np.array([0.2, 0.6, 0.8])
    natural_probs = natural_est.predict_natural_recovery(test_probs)

    assert len(natural_probs) == len(test_probs)
    assert np.all((natural_probs >= 0.01) & (natural_probs <= 0.99))

    # Assisted Recovery Estimator
    assisted_est = AssistedRecoveryEstimator()
    assisted_reminder = assisted_est.predict_assisted_recovery(natural_probs, ActionType.REMINDER)
    uplift_reminder = assisted_est.calculate_incremental_uplift(natural_probs, ActionType.REMINDER)

    assert len(assisted_reminder) == len(natural_probs)
    assert np.all(assisted_reminder >= natural_probs)
    assert np.all(uplift_reminder >= 0.0)


def test_empty_or_invalid_data_handling():
    """
    Task 10 Test: Test handling of empty or invalid data in leakage validator.
    """
    validator = LeakageValidator()
    empty_df = pd.DataFrame()
    report = validator.validate_features(empty_df, raise_on_error=False)
    assert report["is_clean"] is True
