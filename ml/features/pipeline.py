import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from app.services.feature_prep import FeaturePreparationEngine
from app.services.leakage_validator import LeakageValidator, DataLeakageError
from app.core.logging import logger


class MLFeaturePipeline:
    """
    ML Feature Extraction & Encoding Pipeline with Enhanced Historical Customer Features.
    Transforms raw cleaned datasets into point-in-time ML feature matrices (X, y).
    Runs automated leakage validation before model ingestion.
    """

    def __init__(self):
        self.prep_engine = FeaturePreparationEngine()
        self.validator = LeakageValidator()
        self.preprocessor: ColumnTransformer = None
        self.feature_names: List[str] = []

    def compute_point_in_time_customer_history(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Task 7: Compute point-in-time historical customer behavioral features strictly prior to due_in_date T0.
        Uses expanding cumulative window calculations grouped by cust_number to prevent future data leakage.
        """
        data = df.sort_values("due_in_date").copy()
        
        # Calculate past historical metrics per customer
        data["past_delay"] = np.where(
            data["clear_date"].notna() & (data["clear_date"] < data["due_in_date"]),
            (data["clear_date"] - data["due_in_date"]).dt.days,
            0
        )
        data["past_is_late"] = (data["clear_date"].notna() & ((data["clear_date"] - data["due_in_date"]).dt.days > 0)).astype(int)

        # Shift by 1 within customer group so current invoice T0 only sees strictly past history
        grouped = data.groupby("cust_number")

        data["cust_historical_invoice_count"] = grouped.cumcount()
        data["cust_historical_avg_amount"] = grouped["total_open_amount"].shift(1).expanding().mean().reset_index(level=0, drop=True)
        data["cust_historical_avg_delay"] = grouped["past_delay"].shift(1).expanding().mean().reset_index(level=0, drop=True)
        data["cust_historical_late_rate"] = grouped["past_is_late"].shift(1).expanding().mean().reset_index(level=0, drop=True)

        # Recency: days since customer's previous invoice due_in_date
        prev_due = grouped["due_in_date"].shift(1)
        data["cust_recency_days"] = (data["due_in_date"] - prev_due).dt.days.fillna(999.0)

        # Restore original index order
        return data.loc[df.index]

    def extract_raw_features_and_label(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract point-in-time raw features and separate target label y.
        Guarantees clear_date and other future fields NEVER enter X.
        """
        data = self.compute_point_in_time_customer_history(df)
        
        # Target label
        if "recovered_within_window" not in data.columns:
            raise ValueError("Target column 'recovered_within_window' missing from input dataset.")
        y = data["recovered_within_window"].copy()

        # Point-in-time feature prep (using due_in_date as decision point T0)
        X_raw = pd.DataFrame(index=data.index)
        X_raw["total_open_amount"] = data["total_open_amount"].astype(float)
        X_raw["is_open"] = (data["isOpen"].astype(int) == 1).astype(int)
        
        # Seasonality signals from due_in_date
        due_dates = pd.to_datetime(data["due_in_date"])
        X_raw["due_month"] = due_dates.dt.month.fillna(1).astype(int)
        X_raw["due_dayofweek"] = due_dates.dt.dayofweek.fillna(0).astype(int)

        # Historical Customer Behavioral Features (Task 7)
        X_raw["cust_historical_invoice_count"] = data["cust_historical_invoice_count"].fillna(0).astype(float)
        X_raw["cust_historical_avg_amount"] = data["cust_historical_avg_amount"].fillna(0.0).astype(float)
        X_raw["cust_historical_avg_delay"] = data["cust_historical_avg_delay"].fillna(0.0).astype(float)
        X_raw["cust_historical_late_rate"] = data["cust_historical_late_rate"].fillna(0.0).astype(float)
        X_raw["cust_recency_days"] = data["cust_recency_days"].fillna(999.0).astype(float)

        # Categorical features
        X_raw["cust_payment_terms"] = data["cust_payment_terms"].astype(str).fillna("UNKNOWN")
        X_raw["business_code"] = data["business_code"].astype(str).fillna("UNKNOWN")

        # STRICT LEAKAGE VALIDATION: Validate that X_raw is 100% clean of future data
        self.validator.sanitize_features(X_raw)
        self.validator.validate_features(X_raw, raise_on_error=True)

        return X_raw, y

    def fit_transform(self, X_train_raw: pd.DataFrame) -> np.ndarray:
        """
        Fit preprocessor on training features and return scaled/one-hot encoded numpy matrix.
        """
        num_cols = [
            "total_open_amount", "is_open", "due_month", "due_dayofweek",
            "cust_historical_invoice_count", "cust_historical_avg_amount",
            "cust_historical_avg_delay", "cust_historical_late_rate", "cust_recency_days"
        ]
        cat_cols = ["cust_payment_terms", "business_code"]

        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ]
        )

        X_transformed = self.preprocessor.fit_transform(X_train_raw)
        
        # Build feature names list
        cat_feature_names = list(self.preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols))
        self.feature_names = num_cols + cat_feature_names

        logger.info(f"Fitted Enhanced Feature Pipeline: Output shape {X_transformed.shape} with {len(self.feature_names)} features.")
        return X_transformed

    def transform(self, X_raw: pd.DataFrame) -> np.ndarray:
        """
        Transform validation or test raw features using fitted preprocessor.
        """
        if self.preprocessor is None:
            raise RuntimeError("MLFeaturePipeline must be fitted prior to calling transform().")
        
        # Validate against leakage
        self.validator.validate_features(X_raw, raise_on_error=True)
        return self.preprocessor.transform(X_raw)
