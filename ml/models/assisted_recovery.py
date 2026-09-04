import numpy as np
from typing import Dict, Any, Optional
from app.schemas.canonical import ActionType
from app.core.logging import logger


class AssistedRecoveryEstimator:
    """
    Step 8: Assisted Recovery Estimator P(R | X, A=k).
    Models the conditional probability of revenue recovery given specific action k:
    - ActionType.NO_ACTION (A=0)
    - ActionType.REMINDER  (A=1)
    - ActionType.RETRY     (A=2)
    - ActionType.ESCALATE  (A=3)

    NOTE ON TREATMENT DATA AVAILABILITY:
    The raw empirical datasets do not contain multi-arm intervention logs (A=REMINDER vs A=RETRY).
    This class defines the unified interface and baseline action multiplier bounds,
    allowing controlled simulation or future A/B experimental logs to fit true treatment effects.
    """

    def __init__(self):
        # Default domain bounds for action uplift (to be updated empirically or via simulator)
        self.action_multipliers: Dict[str, float] = {
            ActionType.NO_ACTION.value: 1.00,  # Natural recovery baseline
            ActionType.REMINDER.value: 1.25,   # Gentle reminder uplift multiplier
            ActionType.RETRY.value: 1.40,      # Payment retry uplift multiplier
            ActionType.ESCALATE.value: 1.15,   # Manual escalation recovery multiplier
        }

    def predict_assisted_recovery(
        self,
        natural_recovery_probs: np.ndarray,
        action: ActionType
    ) -> np.ndarray:
        """
        Estimate P(R | X, A=k) given estimated natural recovery probabilities P(R | X, A=0)
        and proposed action k.
        """
        multiplier = self.action_multipliers.get(action.value, 1.00)
        
        # Apply action multiplier to natural recovery probability, bounded within [0.01, 0.99]
        assisted_probs = natural_recovery_probs * multiplier
        return np.clip(assisted_probs, 0.01, 0.99)

    def calculate_incremental_uplift(
        self,
        natural_recovery_probs: np.ndarray,
        action: ActionType
    ) -> np.ndarray:
        """
        Calculate incremental recovery uplift:
        Uplift(A=k) = P(R | X, A=k) - P(R | X, A=0)
        """
        assisted_probs = self.predict_assisted_recovery(natural_recovery_probs, action)
        return assisted_probs - natural_recovery_probs
