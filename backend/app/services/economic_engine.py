from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.canonical import ActionType
from app.core.config import settings
from app.core.logging import logger


class EconomicEvaluationResult(BaseModel):
    """
    Economic Evaluation Result for a candidate intervention action with explicit data lineage.
    """
    action: ActionType
    amount: float = Field(..., description="Invoice / opportunity revenue amount at risk")
    natural_probability: float = Field(..., ge=0.0, le=1.0, description="P(R | X, A=0)")
    assisted_probability: float = Field(..., ge=0.0, le=1.0, description="P(R | X, A=k)")
    incremental_probability: float = Field(..., description="Delta p = P_assisted - P_natural")
    intervention_cost: float = Field(..., ge=0.0, description="Direct cost of executing action")
    expected_incremental_revenue: float = Field(..., description="Delta E = Amount * Delta p - intervention_cost")
    is_positive_ev: bool = Field(..., description="True if expected_incremental_revenue > 0")
    decision_summary: str = Field(..., description="Human readable economic summary")
    source: str = Field(default="CONFIGURED_COST", description="Source classification for cost and economic value evaluation")


class EconomicEngine:
    """
    RecoverAI Economic Evaluation Engine.
    Calculates expected incremental revenue Delta E = Amount * Delta p - intervention_cost
    for candidate intervention actions using centralized configuration costs.
    """

    def __init__(self, action_costs: Optional[Dict[str, float]] = None):
        self.action_costs = action_costs if action_costs is not None else settings.recovery.action_costs

    def evaluate_action_economics(
        self,
        amount: float,
        natural_prob: float,
        assisted_prob: float,
        action: ActionType
    ) -> EconomicEvaluationResult:
        """
        Evaluate economic value for a single candidate action.
        """
        cost = float(self.action_costs.get(action.value, 0.00))
        inc_p = float(assisted_prob - natural_prob)
        
        # Expected Incremental Revenue: Delta E = Amount * Delta p - Cost
        expected_inc_rev = float(amount * inc_p - cost)
        is_pos_ev = expected_inc_rev > 0.0

        if action == ActionType.NO_ACTION:
            summary = "NO_ACTION baseline (Zero cost, Zero incremental EV)"
        elif is_pos_ev:
            summary = f"Positive EV: +₹{expected_inc_rev:,.2f} expected incremental gain after ₹{cost:.2f} cost."
        else:
            summary = f"Negative/Zero EV: ₹{expected_inc_rev:,.2f} loss/net zero after ₹{cost:.2f} cost."

        return EconomicEvaluationResult(
            action=action,
            amount=float(amount),
            natural_probability=float(natural_prob),
            assisted_probability=float(assisted_prob),
            incremental_probability=round(inc_p, 4),
            intervention_cost=round(cost, 2),
            expected_incremental_revenue=round(expected_inc_rev, 2),
            is_positive_ev=is_pos_ev,
            decision_summary=summary,
            source="CONFIGURED_COST"
        )
