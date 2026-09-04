from typing import Dict, Any, Optional
from enum import Enum
import numpy as np

from app.schemas.canonical import ActionType
from app.core.config import settings
from app.core.logging import logger


class TreatmentEstimateStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    TREATMENT_ESTIMATE_UNAVAILABLE = "TREATMENT_ESTIMATE_UNAVAILABLE"


class TreatmentEstimator:
    """
    Treatment Estimator Interface for RecoverAI with Data Lineage.
    Provides action-conditioned recovery probabilities P(R | X, A=k).

    NOTE ON CAUSAL IDENTIFICATION:
    Historical raw datasets represent observational records without randomized A/B trial logs.
    This estimator supports explicit treatment probability inputs without fabricating causal uplift claims.
    Action multipliers are explicitly tagged as SIMULATION_ASSUMPTION.
    """

    def __init__(self, action_multipliers: Optional[Dict[str, float]] = None):
        self.action_multipliers = action_multipliers if action_multipliers is not None else settings.recovery.action_multipliers

    def estimate_assisted_probability(
        self,
        natural_prob: float,
        action: ActionType,
        custom_action_prob: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Estimate P(R | X, A=k) given natural recovery P(R | X, A=0) and candidate action k.
        Returns explicit data lineage source metadata.
        """
        if natural_prob is None or np.isnan(natural_prob):
            return {
                "action": action.value,
                "assisted_probability": 0.0,
                "incremental_probability": 0.0,
                "status": TreatmentEstimateStatus.TREATMENT_ESTIMATE_UNAVAILABLE.value,
                "source": "DATA_UNAVAILABLE"
            }

        if action == ActionType.NO_ACTION:
            return {
                "action": action.value,
                "assisted_probability": float(natural_prob),
                "incremental_probability": 0.0,
                "status": TreatmentEstimateStatus.AVAILABLE.value,
                "source": "NATURAL_RECOVERY_BASELINE"
            }

        # If custom experimental / simulated probability is supplied
        if custom_action_prob is not None:
            assisted_p = float(np.clip(custom_action_prob, 0.0, 1.0))
            inc_p = float(np.clip(assisted_p - natural_prob, 0.0, 1.0))
            return {
                "action": action.value,
                "assisted_probability": assisted_p,
                "incremental_probability": inc_p,
                "status": TreatmentEstimateStatus.AVAILABLE.value,
                "source": "SIMULATED_OR_EXPERIMENTAL"
            }

        # Bounded multiplier estimate tagged explicitly as SIMULATION_ASSUMPTION
        mult = self.action_multipliers.get(action.value, 1.0)
        assisted_p = float(np.clip(natural_prob * mult, 0.0, 1.0))
        inc_p = float(np.clip(assisted_p - natural_prob, 0.0, 1.0))

        return {
            "action": action.value,
            "assisted_probability": assisted_p,
            "incremental_probability": inc_p,
            "status": TreatmentEstimateStatus.AVAILABLE.value,
            "source": "SIMULATION_ASSUMPTION"
        }
