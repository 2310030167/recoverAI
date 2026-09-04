import pytest
import pandas as pd
from datetime import datetime, timezone
from app.services.data_loader import DataLoader
from app.services.feature_prep import FeaturePreparationEngine
from app.services.leakage_validator import LeakageValidator, FORBIDDEN_LEAKAGE_COLUMNS


@pytest.fixture
def prep_engine():
    return FeaturePreparationEngine()


@pytest.fixture
def loader():
    return DataLoader()


def test_prepare_receivables_features(prep_engine, loader):
    df_raw = loader.load_accounts_receivable()
    as_of = datetime(2026, 8, 23, tzinfo=timezone.utc)
    features = prep_engine.prepare_receivables_features(df_raw, as_of_date=as_of)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == len(df_raw)
    assert "invoice_amount" in features.columns
    assert "days_since_due" in features.columns
    assert "is_disputed" in features.columns
    
    # Assert no leakage columns in output
    for forbidden in FORBIDDEN_LEAKAGE_COLUMNS:
        assert forbidden not in features.columns


def test_prepare_business_churn_features(prep_engine, loader):
    df_raw = loader.load_business_churn()
    features = prep_engine.prepare_business_churn_features(df_raw)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == len(df_raw)
    assert "monthly_recurring_revenue" in features.columns
    assert "account_health_score" in features.columns
    assert "failed_payment_attempts" in features.columns

    # Assert target leakage columns like churn_date / churn_reason are stripped
    assert "churn_date" not in features.columns
    assert "churn_reason" not in features.columns


def test_prepare_customer_invoice_features(prep_engine, loader):
    df_raw = loader.load_customer_invoices()
    as_of = datetime(2026, 8, 23, tzinfo=timezone.utc)
    features = prep_engine.prepare_customer_invoice_features(df_raw, as_of_date=as_of)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == len(df_raw)
    assert "total_open_amount" in features.columns
    assert "days_overdue" in features.columns

    # Assert clear_date target leakage column is stripped
    assert "clear_date" not in features.columns


def test_prepare_checkout_session_features(prep_engine, loader):
    df_raw = loader.load_online_shoppers()
    features = prep_engine.prepare_checkout_session_features(df_raw)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == len(df_raw)
    assert "exit_rate" in features.columns
    assert "page_value" in features.columns

    # Assert Revenue target label is stripped from feature set
    assert "revenue" not in features.columns
