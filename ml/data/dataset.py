from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from app.services.data_loader import DataLoader, DATA_RAW_DIR
from app.core.logging import logger


class InvoiceDatasetManager:
    """
    Dataset Manager for RecoverAI Invoice Recovery Prediction.
    Audits right-censoring, constructs valid non-censored binary target labels,
    and performs chronological temporal data splitting.
    """

    def __init__(self, raw_dir: Optional[str] = None):
        target_dir = raw_dir if raw_dir is not None else DATA_RAW_DIR
        self.loader = DataLoader(raw_dir=target_dir)

    def load_prepared_dataset(self, window_days: int = 30) -> pd.DataFrame:
        """
        Loads Customer Invoices dataset, classifies censoring status,
        and constructs binary target label y (1 if recovered within window, 0 if not),
        while marking RIGHT_CENSORED observations.
        """
        df = self.loader.load_customer_invoices()
        
        # Filter valid due dates
        valid_df = df[df["due_in_date"].notna()].copy()
        
        # Determine dataset observation end date T_obs_end (latest clear_date in dataset)
        max_clear = valid_df["clear_date"].max()
        T_obs_end = max_clear if pd.notna(max_clear) else valid_df["due_in_date"].max()

        # Censoring classification logic
        def classify_row(row):
            due = row["due_in_date"]
            clear = row["clear_date"]
            
            # If cleared on or before due + window_days -> OBSERVABLE_POSITIVE
            if pd.notna(clear) and (clear - due).days <= window_days:
                return "OBSERVABLE_POSITIVE"
            
            # If cleared after window_days -> OBSERVABLE_NEGATIVE
            if pd.notna(clear) and (clear - due).days > window_days:
                return "OBSERVABLE_NEGATIVE"
            
            # If not cleared (clear is NaT)
            window_end = due + pd.Timedelta(days=window_days)
            if window_end <= T_obs_end:
                # Full 30-day window elapsed without payment -> OBSERVABLE_NEGATIVE
                return "OBSERVABLE_NEGATIVE"
            else:
                # 30-day window has not elapsed before snapshot date -> RIGHT_CENSORED
                return "RIGHT_CENSORED"

        valid_df["censoring_class"] = valid_df.apply(classify_row, axis=1)

        # Assign label y:
        # y = 1 for OBSERVABLE_POSITIVE
        # y = 0 for OBSERVABLE_NEGATIVE
        # y = -1 (CENSORED) for RIGHT_CENSORED
        label_map = {
            "OBSERVABLE_POSITIVE": 1,
            "OBSERVABLE_NEGATIVE": 0,
            "RIGHT_CENSORED": -1
        }
        valid_df["recovered_within_window"] = valid_df["censoring_class"].map(label_map)

        pos_cnt = (valid_df["recovered_within_window"] == 1).sum()
        neg_cnt = (valid_df["recovered_within_window"] == 0).sum()
        cen_cnt = (valid_df["recovered_within_window"] == -1).sum()

        logger.info(
            f"Censoring Audit Complete ({len(valid_df)} invoices): "
            f"Observable Positives: {pos_cnt:,} ({pos_cnt/len(valid_df)*100:.2f}%), "
            f"Observable Negatives: {neg_cnt:,} ({neg_cnt/len(valid_df)*100:.2f}%), "
            f"Right-Censored: {cen_cnt:,} ({cen_cnt/len(valid_df)*100:.2f}%)."
        )

        return valid_df

    def temporal_split(
        self,
        df: pd.DataFrame,
        train_end_date: str = "2019-11-30",
        val_end_date: str = "2020-01-31"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Chronological temporal train/validation/test split.
        Excludes RIGHT_CENSORED observations from supervised training and evaluation sets.
        """
        data = df.sort_values("due_in_date").reset_index(drop=True)
        
        train_cutoff = pd.Timestamp(train_end_date)
        val_cutoff = pd.Timestamp(val_end_date)

        # Supervised subsets (excluding y == -1 / RIGHT_CENSORED)
        obs_data = data[data["recovered_within_window"] != -1].copy()

        train_df = obs_data[obs_data["due_in_date"] <= train_cutoff].copy()
        val_df = obs_data[(obs_data["due_in_date"] > train_cutoff) & (obs_data["due_in_date"] <= val_cutoff)].copy()
        test_df = obs_data[obs_data["due_in_date"] > val_cutoff].copy()

        # Censored records in overall dataset
        censored_df = data[data["recovered_within_window"] == -1].copy()

        split_info = {
            "train": {
                "start": str(train_df["due_in_date"].min()),
                "end": str(train_df["due_in_date"].max()),
                "count": len(train_df),
                "positive_count": int((train_df["recovered_within_window"] == 1).sum()),
                "negative_count": int((train_df["recovered_within_window"] == 0).sum()),
                "positive_rate": float(train_df["recovered_within_window"].mean()),
            },
            "validation": {
                "start": str(val_df["due_in_date"].min()),
                "end": str(val_df["due_in_date"].max()),
                "count": len(val_df),
                "positive_count": int((val_df["recovered_within_window"] == 1).sum()),
                "negative_count": int((val_df["recovered_within_window"] == 0).sum()),
                "positive_rate": float(val_df["recovered_within_window"].mean()),
            },
            "test": {
                "start": str(test_df["due_in_date"].min()),
                "end": str(test_df["due_in_date"].max()),
                "count": len(test_df),
                "positive_count": int((test_df["recovered_within_window"] == 1).sum()),
                "negative_count": int((test_df["recovered_within_window"] == 0).sum()),
                "positive_rate": float(test_df["recovered_within_window"].mean()),
            },
            "censored_records_excluded": len(censored_df)
        }

        logger.info(f"Temporal Split Completed: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}, Censored Excluded={len(censored_df)}")
        return train_df, val_df, test_df, split_info
