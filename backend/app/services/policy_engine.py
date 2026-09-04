from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.canonical import ActionType
from app.core.config import settings
from app.core.logging import logger


class PolicyCheckStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"


class PolicyEvaluationResult(BaseModel):
    """
    Policy evaluation result for a candidate action with source data lineage.
    """
    action: ActionType
    status: PolicyCheckStatus
    reasons: List[str] = Field(default_factory=list)
    is_permitted: bool
    source: str = "CONFIGURED"
    parameter_ref: str = "settings.recovery"


class PolicyEngine:
    """
    RecoverAI Deterministic Policy Constraint Engine.
    Enforces business policies, retry bounds, cooldowns, dispute protection, and escalation rules.
    Pulls default threshold values directly from centralized application configuration (settings.recovery).
    """

    def __init__(
        self,
        max_retry_attempts: Optional[int] = None,
        cooldown_hours: Optional[float] = None,
        max_total_interventions: Optional[int] = None,
        min_expected_value: Optional[float] = None,
        escalation_amount_threshold: Optional[float] = None,
        escalation_days_overdue: Optional[int] = None
    ):
        rec_set = settings.recovery
        self.max_retry_attempts = max_retry_attempts if max_retry_attempts is not None else rec_set.max_retry_attempts
        self.cooldown_hours = cooldown_hours if cooldown_hours is not None else rec_set.cooldown_hours
        self.max_total_interventions = max_total_interventions if max_total_interventions is not None else rec_set.max_interventions
        self.min_expected_value = min_expected_value if min_expected_value is not None else rec_set.min_expected_value
        self.escalation_amount_threshold = escalation_amount_threshold if escalation_amount_threshold is not None else rec_set.escalation_amount_threshold
        self.escalation_days_overdue = escalation_days_overdue if escalation_days_overdue is not None else rec_set.escalation_days_overdue

    def evaluate_policy(
        self,
        action: ActionType,
        amount: float,
        expected_incremental_revenue: float,
        is_disputed: bool = False,
        is_opted_out: bool = False,
        retry_count: int = 0,
        total_interventions: int = 0,
        hours_since_last_intervention: Optional[float] = None,
        days_overdue: int = 0
    ) -> PolicyEvaluationResult:
        """
        Evaluate deterministic business policy compliance for a candidate action.
        """
        reasons: List[str] = []

        # NO_ACTION is always permitted
        if action == ActionType.NO_ACTION:
            return PolicyEvaluationResult(
                action=action,
                status=PolicyCheckStatus.ELIGIBLE,
                reasons=["NO_ACTION baseline is always policy permitted."],
                is_permitted=True,
                source="SYSTEM_SAFETY"
            )

        # Rule 1: Customer Opt-Out Protection
        if is_opted_out and action in [ActionType.REMINDER, ActionType.RETRY]:
            reasons.append("Customer opted out of automated communications/retries.")

        # Rule 2: Disputed Invoice Protection
        if is_disputed and action in [ActionType.REMINDER, ActionType.RETRY]:
            reasons.append("Invoice is under legal/billing dispute; automated recovery blocked.")

        # Rule 3: Max Retry Limit
        if action == ActionType.RETRY and retry_count >= self.max_retry_attempts:
            reasons.append(f"Maximum payment retry limit ({self.max_retry_attempts}) reached.")

        # Rule 4: Total Interventions Cap
        if total_interventions >= self.max_total_interventions:
            reasons.append(f"Maximum intervention cap ({self.max_total_interventions}) reached.")

        # Rule 5: Cooldown Enforcement
        if hours_since_last_intervention is not None and hours_since_last_intervention < self.cooldown_hours:
            reasons.append(f"Intervention cooldown active ({hours_since_last_intervention:.1f}h < {self.cooldown_hours}h required).")

        # Rule 6: Minimum Expected Economic Value
        if expected_incremental_revenue <= self.min_expected_value:
            reasons.append(f"Expected incremental revenue (+₹{expected_incremental_revenue:.2f}) does not exceed min threshold (+₹{self.min_expected_value:.2f}).")

        # Rule 7: Escalation Specific Check
        if action == ActionType.ESCALATE:
            if not (days_overdue >= self.escalation_days_overdue or amount >= self.escalation_amount_threshold or is_disputed):
                reasons.append(f"Escalation criteria not met (Amount >= ₹{self.escalation_amount_threshold:,.0f} or Days Overdue >= {self.escalation_days_overdue} or Disputed required).")

        is_permitted = (len(reasons) == 0)
        status = PolicyCheckStatus.ELIGIBLE if is_permitted else PolicyCheckStatus.BLOCKED

        return PolicyEvaluationResult(
            action=action,
            status=status,
            reasons=reasons if not is_permitted else ["All policy constraints satisfied."],
            is_permitted=is_permitted,
            source="CONFIGURED"
        )
