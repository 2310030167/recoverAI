from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.schemas.execution import ExecutionValidationResult, ExecutionState
from app.schemas.canonical import ActionType, PolicyStatus
from app.services.policy_engine import PolicyEngine
from app.services.economic_engine import EconomicEngine
from app.services.treatment_estimator import TreatmentEstimator
from app.core.logging import logger


class ActionValidator:
    """
    Independent Pre-Execution Action Validator.
    Revalidates opportunity state, policy rules, customer preferences, and economic EV before execution.
    The ExecutionEngine must NEVER bypass this validator.
    """

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        economic_engine: Optional[EconomicEngine] = None,
        treatment_estimator: Optional[TreatmentEstimator] = None
    ):
        self.policy_engine = policy_engine or PolicyEngine()
        self.economic_engine = economic_engine or EconomicEngine()
        self.treatment_estimator = treatment_estimator or TreatmentEstimator()

    def validate_execution_request(
        self,
        opportunity_id: str,
        action: ActionType,
        amount: float,
        natural_prob: float,
        is_disputed: bool = False,
        is_opted_out: bool = False,
        retry_count: int = 0,
        total_interventions: int = 0,
        hours_since_last_intervention: Optional[float] = None,
        days_overdue: int = 0,
        is_recovered: bool = False,
        is_expired: bool = False
    ) -> ExecutionValidationResult:
        """
        Independently validate whether requested action is eligible for execution.
        """
        passed: List[str] = []
        failed: List[str] = []

        # 1. Opportunity existence & status checks
        if is_recovered:
            failed.append("Opportunity has already been recovered.")
        else:
            passed.append("Opportunity recovery state active.")

        if is_expired or days_overdue > 30:
            failed.append("Recovery opportunity has expired past 30-day window.")
        else:
            passed.append("Opportunity within 30-day operational recovery window.")

        # 2. Action Type check
        if action not in [ActionType.NO_ACTION, ActionType.REMINDER, ActionType.RETRY, ActionType.ESCALATE]:
            failed.append(f"Unsupported action type '{action}'.")
        else:
            passed.append(f"Action '{action.value}' supported.")

        # 3. Calculate Expected Economic Value
        treat_res = self.treatment_estimator.estimate_assisted_probability(natural_prob, action)
        assisted_prob = treat_res["assisted_probability"]

        econ_eval = self.economic_engine.evaluate_action_economics(
            amount=amount,
            natural_prob=natural_prob,
            assisted_prob=assisted_prob,
            action=action
        )
        expected_inc_rev = econ_eval.expected_incremental_revenue

        if action != ActionType.NO_ACTION and expected_inc_rev <= 0.0:
            failed.append(f"Economic Check: Expected incremental revenue EV (+₹{expected_inc_rev:,.2f}) is non-positive.")
        else:
            passed.append("Economic expected value EV check passed.")

        # 4. Policy Engine Validation
        policy_res = self.policy_engine.evaluate_policy(
            action=action,
            amount=amount,
            expected_incremental_revenue=expected_inc_rev,
            is_disputed=is_disputed,
            is_opted_out=is_opted_out,
            retry_count=retry_count,
            total_interventions=total_interventions,
            hours_since_last_intervention=hours_since_last_intervention,
            days_overdue=days_overdue
        )

        if not policy_res.is_permitted:
            failed.append(f"Policy Engine Block: {policy_res.status.value} - {', '.join(policy_res.reasons)}")
        else:
            passed.append("Policy Engine check passed.")

        if failed:
            blocking_msg = "; ".join(failed)
            logger.warning(f"Execution Validation BLOCKED for Opportunity ID={opportunity_id}, Action={action.value}: {blocking_msg}")
            return ExecutionValidationResult(
                is_valid=False,
                status=ExecutionState.BLOCKED,
                blocking_reason=blocking_msg,
                checks_passed=passed,
                checks_failed=failed
            )

        logger.info(f"Execution Validation PASSED for Opportunity ID={opportunity_id}, Action={action.value}.")
        return ExecutionValidationResult(
            is_valid=True,
            status=ExecutionState.EXECUTING,
            checks_passed=passed,
            checks_failed=failed
        )
