import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from app.core.logging import logger

_default_data_raw = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw")
)
DATA_RAW_DIR = os.getenv("DATA_RAW_DIR", _default_data_raw)


class DataLoader:
    """
    Data Loader & Cleaning Pipeline for RecoverAI CORE datasets inside data/raw/.
    Extracts, cleans, standardizes types, and validates schemas.
    """

    def __init__(self, raw_dir: str = DATA_RAW_DIR):
        self.raw_dir = raw_dir

    def load_accounts_receivable(self) -> pd.DataFrame:
        """
        Load & clean IBM Watson Accounts Receivable benchmark dataset:
        WA_Fn-UseC_-Accounts-Receivable.csv
        """
        file_path = os.path.join(self.raw_dir, "WA_Fn-UseC_-Accounts-Receivable.csv")
        logger.info(f"Loading Accounts Receivable dataset from {file_path}")
        df = pd.read_csv(file_path)

        # Standardize column names
        df.columns = [c.strip() for c in df.columns]

        # Datetime conversions
        for dt_col in ["InvoiceDate", "DueDate", "PaperlessDate", "SettledDate"]:
            if dt_col in df.columns:
                df[dt_col] = pd.to_datetime(df[dt_col], errors="coerce")

        # Numeric conversions (Support InvoiceAmount or invoiceAmount)
        amt_col = "InvoiceAmount" if "InvoiceAmount" in df.columns else ("invoiceAmount" if "invoiceAmount" in df.columns else None)
        if amt_col:
            df["invoiceAmount"] = pd.to_numeric(df[amt_col], errors="coerce").fillna(0.0)

        for int_col in ["DaysToPay", "DaysLate", "DaysToSettle"]:
            if int_col in df.columns:
                df[int_col] = pd.to_numeric(df[int_col], errors="coerce").fillna(0).astype(int)

        # Boolean mapping
        if "Disputed" in df.columns:
            df["Disputed"] = df["Disputed"].astype(str).str.strip().str.lower().map({"yes": True, "no": False}).fillna(False)
        if "PaperlessBill" in df.columns:
            df["PaperlessBill"] = df["PaperlessBill"].astype(str).str.strip().str.lower().map({"paperless": True, "electronic": True, "paper": False}).fillna(False)

        logger.info(f"Loaded Accounts Receivable dataset: {len(df)} records.")
        return df

    def load_business_churn(self) -> pd.DataFrame:
        """
        Load & clean B2B SaaS Enterprise Churn & Health dataset:
        customer_churn_business_dataset.csv
        """
        file_path = os.path.join(self.raw_dir, "customer_churn_business_dataset.csv")
        logger.info(f"Loading Business Churn dataset from {file_path}")
        df = pd.read_csv(file_path)

        # Datetime conversions
        for col in ["contract_start_date", "contract_end_date", "last_login_date", "churn_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Standardize revenue & payment columns
        if "monthly_fee" in df.columns and "monthly_recurring_revenue" not in df.columns:
            df["monthly_recurring_revenue"] = pd.to_numeric(df["monthly_fee"], errors="coerce").fillna(0.0)
        if "total_revenue" in df.columns and "annual_revenue" not in df.columns:
            df["annual_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce").fillna(0.0)

        # Numeric fields
        num_cols = ["annual_revenue", "monthly_recurring_revenue", "monthly_fee", "total_revenue",
                    "support_tickets", "support_tickets_raised", "features_used", "feature_usage_score",
                    "active_users", "license_utilization_rate", "nps_score", "account_health_score",
                    "payment_delay_days", "late_payment_count", "payment_failures", "failed_payment_attempts"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Booleans
        for col in ["auto_renew", "onboarding_completed", "churn"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower().map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}).fillna(False)

        logger.info(f"Loaded Business Churn dataset: {len(df)} records.")
        return df

    def load_customer_invoices(self) -> pd.DataFrame:
        """
        Load & clean SAP Customer Invoices dataset:
        Customer Invoices Dataset.csv
        """
        file_path = os.path.join(self.raw_dir, "Customer Invoices Dataset.csv")
        logger.info(f"Loading Customer Invoices dataset from {file_path}")
        df = pd.read_csv(file_path, low_memory=False)

        # Deduplicate exact duplicates
        initial_len = len(df)
        df = df.drop_duplicates().copy()
        logger.info(f"Removed {initial_len - len(df)} duplicate invoice records.")

        # Datetime conversions
        df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
        df["clear_date"] = pd.to_datetime(df["clear_date"], errors="coerce")

        # due_in_date (Float YYYYMMDD.0)
        def parse_yyyymmdd(val):
            try:
                if pd.isna(val):
                    return pd.NaT
                s = str(int(val))
                if len(s) == 8:
                    return pd.to_datetime(s, format="%Y%m%d")
            except Exception:
                pass
            return pd.NaT

        df["due_in_date"] = df["due_in_date"].apply(parse_yyyymmdd)

        # total_open_amount
        df["total_open_amount"] = pd.to_numeric(df["total_open_amount"], errors="coerce").fillna(0.0)
        df["isOpen"] = pd.to_numeric(df["isOpen"], errors="coerce").fillna(1).astype(int)

        logger.info(f"Loaded Customer Invoices dataset: {len(df)} records.")
        return df

    def load_online_shoppers(self) -> pd.DataFrame:
        """
        Load & clean UCI Online Shoppers Purchasing Intention dataset:
        online_shoppers_intention.csv
        """
        file_path = os.path.join(self.raw_dir, "online_shoppers_intention.csv")
        logger.info(f"Loading Online Shoppers Intention dataset from {file_path}")
        df = pd.read_csv(file_path)

        # Deduplicate
        df = df.drop_duplicates().copy()

        # Booleans
        df["Weekend"] = df["Weekend"].astype(bool)
        df["Revenue"] = df["Revenue"].astype(bool)

        # Numeric session stats
        num_cols = ["Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
                    "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates", "PageValues", "SpecialDay"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        logger.info(f"Loaded Online Shoppers dataset: {len(df)} records.")
        return df
