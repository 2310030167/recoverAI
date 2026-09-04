import pytest
import pandas as pd
from app.services.data_loader import DataLoader


@pytest.fixture
def loader():
    return DataLoader()


def test_load_accounts_receivable(loader):
    """
    Test loading IBM Watson Accounts Receivable benchmark dataset.
    """
    df = loader.load_accounts_receivable()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2466
    assert "invoiceAmount" in df.columns
    assert "InvoiceDate" in df.columns
    assert "DueDate" in df.columns
    assert "Disputed" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["InvoiceDate"])
    assert pd.api.types.is_datetime64_any_dtype(df["DueDate"])
    assert df["Disputed"].dtype == bool


def test_load_business_churn(loader):
    """
    Test loading B2B SaaS Enterprise Churn dataset.
    """
    df = loader.load_business_churn()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10000
    assert "monthly_fee" in df.columns or "monthly_recurring_revenue" in df.columns
    assert "total_revenue" in df.columns or "annual_revenue" in df.columns
    assert "payment_failures" in df.columns or "failed_payment_attempts" in df.columns


def test_load_customer_invoices(loader):
    """
    Test loading SAP Customer Invoices dataset.
    """
    df = loader.load_customer_invoices()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 40000 # Deduplicated from 50,000
    assert "total_open_amount" in df.columns
    assert "clear_date" in df.columns
    assert "due_in_date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["due_in_date"])


def test_load_online_shoppers(loader):
    """
    Test loading UCI Online Shoppers Purchasing Intention dataset.
    """
    df = loader.load_online_shoppers()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 12000
    assert "PageValues" in df.columns
    assert "ExitRates" in df.columns
    assert "Revenue" in df.columns
    assert df["Revenue"].dtype == bool
