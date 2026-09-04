import pytest
import pandas as pd
from app.services.leakage_validator import LeakageValidator, DataLeakageError


def test_leakage_validator_pass():
    validator = LeakageValidator()
    clean_df = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "invoice_amount": [100.0, 200.0],
        "days_overdue": [5, 10],
        "is_disputed": [False, True]
    })
    report = validator.validate_features(clean_df, raise_on_error=True)
    assert report["is_clean"] is True
    assert report["status"] == "PASS"


def test_leakage_validator_fail_clear_date():
    validator = LeakageValidator()
    leaky_df = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "invoice_amount": [100.0, 200.0],
        "clear_date": ["2020-01-01", "2020-01-05"] # FORBIDDEN LEAKAGE
    })
    with pytest.raises(DataLeakageError) as exc_info:
        validator.validate_features(leaky_df, raise_on_error=True)
    assert "clear_date" in str(exc_info.value)


def test_leakage_validator_fail_churn_reason():
    validator = LeakageValidator()
    leaky_df = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "churn_reason": ["Price", "Competitor"] # FORBIDDEN LEAKAGE
    })
    with pytest.raises(DataLeakageError):
        validator.validate_features(leaky_df, raise_on_error=True)


def test_sanitize_features():
    validator = LeakageValidator()
    dirty_df = pd.DataFrame({
        "customer_id": ["C1", "C2"],
        "invoice_amount": [100.0, 200.0],
        "clear_date": ["2020-01-01", "2020-01-05"],
        "revenue": [True, False]
    })
    sanitized_df = validator.sanitize_features(dirty_df)
    assert "clear_date" not in sanitized_df.columns
    assert "revenue" not in sanitized_df.columns
    assert "invoice_amount" in sanitized_df.columns
    assert "customer_id" in sanitized_df.columns
