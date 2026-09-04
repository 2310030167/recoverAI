from datetime import datetime, timezone
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.services.leakage_validator import LeakageValidator, DataLeakageError


class FeaturePreparationEngine:
    """
    Point-in-Time Feature Preparation Engine for RecoverAI.
    Constructs leakage-free, point-in-time feature tables for predictive models.
    """

    def __init__(self):
        self.validator = LeakageValidator()

    def prepare_receivables_features(self, df: pd.DataFrame, as_of_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Point-in-time feature construction for Accounts Receivable (IBM AR Dataset).
        Calculates dynamic point-in-time features relative to as_of_date.
        """
        data = df.copy()
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        features = pd.DataFrame(index=data.index)
        features["customer_id"] = data["customerID"].astype(str) if "customerID" in data.columns else "UNKNOWN"
        features["invoice_number"] = data["invoiceNumber"].astype(str) if "invoiceNumber" in data.columns else "UNKNOWN"
        
        amt_col = "invoiceAmount" if "invoiceAmount" in data.columns else ("InvoiceAmount" if "InvoiceAmount" in data.columns else None)
        features["invoice_amount"] = data[amt_col].astype(float) if amt_col else 0.0

        features["is_disputed"] = data["Disputed"].astype(bool) if "Disputed" in data.columns else False
        features["paperless_bill"] = data["PaperlessBill"].astype(bool) if "PaperlessBill" in data.columns else False

        # Dynamic Point-in-time Days Overdue
        if "DueDate" in data.columns and pd.api.types.is_datetime64_any_dtype(data["DueDate"]):
            as_of_ts = pd.Timestamp(as_of_date)
            due_dates = data["DueDate"].dt.tz_localize(None) if data["DueDate"].dt.tz is not None else data["DueDate"]
            as_of_ts_naive = as_of_ts.tz_localize(None) if as_of_ts.tz is not None else as_of_ts
            
            features["days_since_due"] = (as_of_ts_naive - due_dates).dt.days.fillna(0).clip(lower=0)
            features["is_overdue"] = features["days_since_due"] > 0
        else:
            features["days_since_due"] = 0
            features["is_overdue"] = False

        # Verify no leakage
        features = self.validator.sanitize_features(features)
        self.validator.validate_features(features)
        return features

    def prepare_business_churn_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature construction for B2B SaaS Enterprise Churn dataset.
        Extracts customer health, payment delay, and usage metrics.
        """
        data = df.copy()
        features = pd.DataFrame(index=data.index)

        features["customer_id"] = data["customer_id"].astype(str) if "customer_id" in data.columns else "UNKNOWN"
        features["company_size"] = data["company_size"].astype(str) if "company_size" in data.columns else "Unknown"

        rev_col = "annual_revenue" if "annual_revenue" in data.columns else ("total_revenue" if "total_revenue" in data.columns else None)
        features["annual_revenue"] = data[rev_col].astype(float) if rev_col else 0.0

        mrr_col = "monthly_recurring_revenue" if "monthly_recurring_revenue" in data.columns else ("monthly_fee" if "monthly_fee" in data.columns else None)
        features["monthly_recurring_revenue"] = data[mrr_col].astype(float) if mrr_col else 0.0

        features["tenure_months"] = data["tenure_months"].astype(float) if "tenure_months" in data.columns else 0.0
        
        health_col = "account_health_score" if "account_health_score" in data.columns else ("csat_score" if "csat_score" in data.columns else None)
        features["account_health_score"] = data[health_col].astype(float) if health_col else 100.0

        usage_col = "feature_usage_score" if "feature_usage_score" in data.columns else ("features_used" if "features_used" in data.columns else None)
        features["feature_usage_score"] = data[usage_col].astype(float) if usage_col else 0.0

        features["license_utilization_rate"] = data["license_utilization_rate"].astype(float) if "license_utilization_rate" in data.columns else 1.0
        features["payment_delay_days"] = data["payment_delay_days"].astype(float) if "payment_delay_days" in data.columns else 0.0
        features["late_payment_count"] = data["late_payment_count"].astype(int) if "late_payment_count" in data.columns else 0
        
        fail_col = "failed_payment_attempts" if "failed_payment_attempts" in data.columns else ("payment_failures" if "payment_failures" in data.columns else None)
        features["failed_payment_attempts"] = data[fail_col].astype(int) if fail_col else 0
        
        features["auto_renew"] = data["auto_renew"].astype(bool) if "auto_renew" in data.columns else True

        # Sanitize and validate against target leakage (e.g. churn_date, churn_reason, churn)
        features = self.validator.sanitize_features(features)
        self.validator.validate_features(features)
        return features

    def prepare_customer_invoice_features(self, df: pd.DataFrame, as_of_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Feature construction for SAP Customer Invoices dataset.
        Point-in-time calculation of invoice exposure and payment terms.
        """
        data = df.copy()
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        features = pd.DataFrame(index=data.index)
        features["customer_number"] = data["cust_number"].astype(str) if "cust_number" in data.columns else "UNKNOWN"
        features["invoice_id"] = data["invoice_id"].astype(str) if "invoice_id" in data.columns else (data["doc_id"].astype(str) if "doc_id" in data.columns else "UNKNOWN")
        features["total_open_amount"] = data["total_open_amount"].astype(float) if "total_open_amount" in data.columns else 0.0
        features["is_open"] = (data["isOpen"].astype(int) == 1) if "isOpen" in data.columns else True
        features["payment_terms"] = data["cust_payment_terms"].astype(str) if "cust_payment_terms" in data.columns else "UNKNOWN"

        # Dynamic overdue calculation from due_in_date
        if "due_in_date" in data.columns and pd.api.types.is_datetime64_any_dtype(data["due_in_date"]):
            as_of_ts = pd.Timestamp(as_of_date)
            due_dates = data["due_in_date"].dt.tz_localize(None) if data["due_in_date"].dt.tz is not None else data["due_in_date"]
            as_of_ts_naive = as_of_ts.tz_localize(None) if as_of_ts.tz is not None else as_of_ts
            
            features["days_overdue"] = (as_of_ts_naive - due_dates).dt.days.fillna(0).clip(lower=0)
        else:
            features["days_overdue"] = 0

        # Sanitize (stripping clear_date!)
        features = self.validator.sanitize_features(features)
        self.validator.validate_features(features)
        return features

    def prepare_checkout_session_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature construction for UCI Online Shoppers Intention dataset.
        Extracts session friction and intent indicators.
        """
        data = df.copy()
        features = pd.DataFrame(index=data.index)

        features["administrative_duration"] = data["Administrative_Duration"].astype(float) if "Administrative_Duration" in data.columns else 0.0
        features["informational_duration"] = data["Informational_Duration"].astype(float) if "Informational_Duration" in data.columns else 0.0
        features["product_related_duration"] = data["ProductRelated_Duration"].astype(float) if "ProductRelated_Duration" in data.columns else 0.0
        features["bounce_rate"] = data["BounceRates"].astype(float) if "BounceRates" in data.columns else 0.0
        features["exit_rate"] = data["ExitRates"].astype(float) if "ExitRates" in data.columns else 0.0
        features["page_value"] = data["PageValues"].astype(float) if "PageValues" in data.columns else 0.0
        features["special_day"] = data["SpecialDay"].astype(float) if "SpecialDay" in data.columns else 0.0
        features["visitor_type"] = data["VisitorType"].astype(str) if "VisitorType" in data.columns else "Returning_Visitor"
        features["weekend"] = data["Weekend"].astype(bool) if "Weekend" in data.columns else False

        # Sanitize (stripping Revenue target label!)
        features = self.validator.sanitize_features(features)
        self.validator.validate_features(features)
        return features
