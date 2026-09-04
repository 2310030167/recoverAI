from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from app.schemas.canonical import ActionType, OpportunityStatus, PolicyStatus
from app.services.economic_engine import EconomicEngine, EconomicEvaluationResult
from app.services.policy_engine import PolicyEngine, PolicyEvaluationResult, PolicyCheckStatus
from app.services.treatment_estimator import TreatmentEstimator
from ml.models.natural_recovery import NaturalRecoveryEstimator
from ml.models.tabular import StrongTabularModel
from app.core.logging import logger


class ActionCandidateEvaluation(BaseModel):
    action: ActionType
    treatment_source: str
    natural_probability: float
    assisted_probability: float
    incremental_probability: float
    intervention_cost: float
    expected_incremental_revenue: float
    is_positive_ev: bool
    policy_status: PolicyCheckStatus
    policy_reasons: List[str]
    is_eligible: bool


class RecoveryDecisionExplanation(BaseModel):
    opportunity_id: str
    selected_action: ActionType
    decision_reason: str
    amount: float
    natural_probability: float
    assisted_probability: float
    incremental_probability: float
    intervention_cost: float
    expected_incremental_revenue: float
    policy_status: PolicyStatus
    candidate_evaluations: List[ActionCandidateEvaluation]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionEngine:
    """
    RecoverAI Decision Engine.
    Orchestrates ML probability predictions, treatment estimation, economic evaluation,
    policy constraints, action selection, and audit event generation.
    """

    def __init__(
        self,
        economic_engine: Optional[EconomicEngine] = None,
        policy_engine: Optional[PolicyEngine] = None,
        treatment_estimator: Optional[TreatmentEstimator] = None,
    ):
        self.economic_engine = economic_engine or EconomicEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.treatment_estimator = treatment_estimator or TreatmentEstimator()

    def evaluate_opportunity(
        self,
        opportunity_id: str,
        amount: float,
        natural_prob: float,
        is_disputed: bool = False,
        is_opted_out: bool = False,
        retry_count: int = 0,
        total_interventions: int = 0,
        hours_since_last_intervention: Optional[float] = None,
        days_overdue: int = 0,
        custom_action_probs: Optional[Dict[str, float]] = None
    ) -> RecoveryDecisionExplanation:
        """
        Evaluate all candidate actions for a recovery opportunity and select the optimal bounded intervention.
        """
        candidate_actions = [
            ActionType.NO_ACTION,
            ActionType.REMINDER,
            ActionType.RETRY,
            ActionType.ESCALATE,
        ]

        candidate_evaluations: List[ActionCandidateEvaluation] = []
        eligible_candidates: List[ActionCandidateEvaluation] = []

        custom_probs = custom_action_probs or {}

        for act in candidate_actions:
            # 1. Treatment estimation P(R | X, A=k)
            custom_p = custom_probs.get(act.value, None)
            treatment_info = self.treatment_estimator.estimate_assisted_probability(
                natural_prob=natural_prob,
                action=act,
                custom_action_prob=custom_p
            )

            assisted_p = treatment_info["assisted_probability"]
            inc_p = treatment_info["incremental_probability"]
            t_source = treatment_info["source"]

            # 2. Economic evaluation Delta E = Amount * Delta p - Cost
            econ = self.economic_engine.evaluate_action_economics(
                amount=amount,
                natural_prob=natural_prob,
                assisted_prob=assisted_p,
                action=act
            )

            # 3. Policy evaluation
            policy = self.policy_engine.evaluate_policy(
                action=act,
                amount=amount,
                expected_incremental_revenue=econ.expected_incremental_revenue,
                is_disputed=is_disputed,
                is_opted_out=is_opted_out,
                retry_count=retry_count,
                total_interventions=total_interventions,
                hours_since_last_intervention=hours_since_last_intervention,
                days_overdue=days_overdue
            )

            is_eligible = econ.is_positive_ev and policy.is_permitted if act != ActionType.NO_ACTION else True

            cand_eval = ActionCandidateEvaluation(
                action=act,
                treatment_source=t_source,
                natural_probability=round(natural_prob, 4),
                assisted_probability=round(assisted_p, 4),
                incremental_probability=round(inc_p, 4),
                intervention_cost=econ.intervention_cost,
                expected_incremental_revenue=econ.expected_incremental_revenue,
                is_positive_ev=econ.is_positive_ev,
                policy_status=policy.status,
                policy_reasons=policy.reasons,
                is_eligible=is_eligible
            )

            candidate_evaluations.append(cand_eval)

            # Collect non-NO_ACTION eligible candidates
            if act != ActionType.NO_ACTION and is_eligible:
                eligible_candidates.append(cand_eval)

        # 4. Action Selection Rule:
        # Select highest expected_incremental_revenue among eligible candidate actions.
        # Fallback to NO_ACTION if no non-NO_ACTION action has positive EV or is policy-permitted.
        if eligible_candidates:
            # Sort descending by expected_incremental_revenue
            eligible_candidates.sort(key=lambda x: x.expected_incremental_revenue, reverse=True)
            selected_cand = eligible_candidates[0]
            selected_action = selected_cand.action
            reason = (
                f"Selected {selected_action.value}: Highest policy-eligible expected incremental revenue "
                f"(+₹{selected_cand.expected_incremental_revenue:,.2f}) after ₹{selected_cand.intervention_cost:.2f} cost."
            )
            final_cand = selected_cand
        else:
            selected_action = ActionType.NO_ACTION
            no_action_cand = [c for c in candidate_evaluations if c.action == ActionType.NO_ACTION][0]
            reason = "Selected NO_ACTION: No alternative intervention yielded positive policy-eligible incremental economic value."
            final_cand = no_action_cand

        return RecoveryDecisionExplanation(
            opportunity_id=opportunity_id,
            selected_action=selected_action,
            decision_reason=reason,
            amount=float(amount),
            natural_probability=final_cand.natural_probability,
            assisted_probability=final_cand.assisted_probability,
            incremental_probability=final_cand.incremental_probability,
            intervention_cost=final_cand.intervention_cost,
            expected_incremental_revenue=final_cand.expected_incremental_revenue,
            policy_status=PolicyStatus.ELIGIBLE if final_cand.is_eligible else PolicyStatus.BLOCKED,
            candidate_evaluations=candidate_evaluations,
            timestamp=datetime.now(timezone.utc)
        )
