from typing import List, Set, Dict, Any, Union
import pandas as pd
from app.core.logging import logger


class DataLeakageError(Exception):
    """Exception raised when target or temporal leakage columns are detected in feature datasets."""
    pass


# Strict Registry of Forbidden Leakage Columns
FORBIDDEN_LEAKAGE_COLUMNS: Set[str] = {
    # Accounts Receivable / Invoices
    "clear_date",
    "settled_date",
    "days_to_pay",
    "daystopay",
    "days_to_settle",
    "final_payment_status",
    "recovery_outcome",
    "recovered_amount",
    "is_recovered",
    
    # Subscription / Customer Churn
    "churn_date",
    "churn_reason",
    "exit_interview_notes",
    "cancellation_timestamp",

    # Checkout Sessions
    "revenue", # In online_shoppers_intention, Revenue is the target label y!

    # Card Fraud
    "is_fraud",
}


class LeakageValidator:
    """
    Automated Data Leakage Validator.
    Enforces point-in-time temporal boundaries and prevents future-information contamination.
    """

    def __init__(self, forbidden_cols: Set[str] = FORBIDDEN_LEAKAGE_COLUMNS):
        self.forbidden_cols = set(c.lower() for c in forbidden_cols)

    def validate_features(self, df: pd.DataFrame, raise_on_error: bool = True) -> Dict[str, Any]:
        """
        Validate that a feature DataFrame contains zero leakage columns.
        """
        cols_in_df = [str(c).lower().strip() for c in df.columns]
        detected_leakage = [c for c in cols_in_df if c in self.forbidden_cols]

        is_clean = (len(detected_leakage) == 0)

        report = {
            "is_clean": is_clean,
            "detected_leakage_columns": detected_leakage,
            "total_columns": len(df.columns),
            "status": "PASS" if is_clean else "FAIL"
        }

        if not is_clean:
            err_msg = f"DATA LEAKAGE DETECTED! The following target/future columns were found in the feature matrix: {detected_leakage}"
            logger.error(err_msg)
            if raise_on_error:
                raise DataLeakageError(err_msg)

        logger.info(f"Leakage Validation Passed: {len(df.columns)} columns verified clean.")
        return report

    def sanitize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Safely remove any potential leakage columns from a DataFrame prior to model ingestion.
        """
        cols_to_drop = [c for c in df.columns if str(c).lower().strip() in self.forbidden_cols]
        if cols_to_drop:
            logger.warning(f"Sanitizing features: dropping leakage columns {cols_to_drop}")
            return df.drop(columns=cols_to_drop).copy()
        return df.copy()
