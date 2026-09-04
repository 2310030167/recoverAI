import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from app.core.logging import logger


class NaturalRecoveryEstimator:
    """
    Step 7: Natural Recovery Estimator P(R | X, A=0).
    Estimates the counterfactual probability that an invoice/payment will be recovered
    without active merchant intervention.

    NOTE ON CAUSAL IDENTIFICATION:
    The available historical datasets (Customer Invoices, IBM Accounts Receivable)
    represent observational records of standard business operations. They do NOT contain
    randomized A/B experiment treatment flags. Therefore, this estimator uses empirical
    historical baseline recovery rates within risk deciles/cohorts as an observational
    estimate of P(R | X, A=0).
    """

    def __init__(self, num_deciles: int = 10):
        self.num_deciles = num_deciles
        self.decile_bins: Optional[np.ndarray] = None
        self.decile_recovery_rates: Dict[int, float] = {}
        self.overall_baseline_rate: float = 0.5
        self.is_fitted: bool = False

    def fit(self, baseline_prob_train: np.ndarray, y_train: np.ndarray) -> "NaturalRecoveryEstimator":
        """
        Fit natural recovery rates across probability risk deciles on baseline observational data.
        """
        self.overall_baseline_rate = float(np.mean(y_train)) if len(y_train) > 0 else 0.5

        # Quantile binning on base probabilities
        try:
            percentiles = np.linspace(0, 100, self.num_deciles + 1)
            self.decile_bins = np.percentile(baseline_prob_train, percentiles)
            # Ensure unique edges
            self.decile_bins = np.unique(self.decile_bins)
            
            if len(self.decile_bins) < 2:
                self.decile_bins = np.array([0.0, 1.0])
        except Exception as e:
            logger.warning(f"Could not compute exact deciles for NaturalRecoveryEstimator: {e}")
            self.decile_bins = np.array([0.0, 1.0])

        # Assign deciles and compute mean recovery rate per bin
        bin_indices = np.digitize(baseline_prob_train, self.decile_bins[:-1]) - 1
        for b_idx in range(len(self.decile_bins)):
            mask = (bin_indices == b_idx)
            if np.sum(mask) > 0:
                self.decile_recovery_rates[b_idx] = float(np.mean(y_train[mask]))
            else:
                self.decile_recovery_rates[b_idx] = self.overall_baseline_rate

        self.is_fitted = True
        logger.info(f"Fitted Natural Recovery Estimator across {len(self.decile_recovery_rates)} deciles. Overall baseline: {self.overall_baseline_rate:.4f}")
        return self

    def predict_natural_recovery(self, risk_probs: np.ndarray) -> np.ndarray:
        """
        Estimate P(R | X, A=0) for a vector of opportunity risk probabilities.
        """
        if not self.is_fitted:
            # Fallback to empirical 0.5 if un-fitted
            return np.full_like(risk_probs, 0.5)

        bin_indices = np.digitize(risk_probs, self.decile_bins[:-1]) - 1
        natural_probs = np.zeros_like(risk_probs)

        for i, b_idx in enumerate(bin_indices):
            # Clamp bin index
            b_clamped = min(max(0, b_idx), len(self.decile_bins) - 1)
            # Apply empirical rate scaled smoothly by individual risk prob
            base_rate = self.decile_recovery_rates.get(b_clamped, self.overall_baseline_rate)
            # Smooth interpolation: 0.8 * base_rate + 0.2 * risk_prob
            natural_probs[i] = 0.8 * base_rate + 0.2 * risk_probs[i]

        return np.clip(natural_probs, 0.01, 0.99)
