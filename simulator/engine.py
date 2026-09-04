import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from simulator.state import (
    SimulationState,
    SimulationOutcome,
    AuditEventRecord,
    RecoveryStatus,
    TerminationReason,
)
from app.schemas.canonical import ActionType, PolicyStatus
from app.services.decision_engine import DecisionEngine
from app.core.config import settings
from app.core.logging import logger


class RecoverySimulatorEngine:
    """
    Controlled Recovery Simulator & Timeline Engine with Common Random Numbers (CRN).
    Simulates recovery opportunity progression through operational recovery horizons.
    Pulls operational recovery horizons (3d, 7d, 30d) directly from centralized configuration (settings.recovery).
    """

    def __init__(
        self,
        decision_engine: Optional[DecisionEngine] = None,
        operational_window_3d: Optional[int] = None,
        operational_window_7d: Optional[int] = None,
        macro_window_30d: Optional[int] = None,
        random_seed: Optional[int] = 42
    ):
        rec_set = settings.recovery
        self.decision_engine = decision_engine or DecisionEngine()
        self.window_3d = operational_window_3d if operational_window_3d is not None else rec_set.primary_window_days
        self.window_7d = operational_window_7d if operational_window_7d is not None else rec_set.secondary_window_days
        self.window_30d = macro_window_30d if macro_window_30d is not None else rec_set.macro_horizon_days
        self.random_seed = random_seed

    def run_simulation(
        self,
        opportunity_id: str,
        customer_id: str,
        amount: float,
        due_date: datetime,
        natural_prob: float,
        is_disputed: bool = False,
        is_opted_out: bool = False,
        strategy_override: Optional[ActionType] = None,
        custom_action_probs: Optional[Dict[str, float]] = None,
        crn_draws: Optional[List[float]] = None,
        max_simulation_days: Optional[int] = None
    ) -> SimulationOutcome:
        """
        Run a single opportunity recovery simulation across time steps.
        """
        if max_simulation_days is None:
            max_simulation_days = self.window_30d

        sim_id = f"SIM_{uuid.uuid4().hex[:8].upper()}"
        start_date = due_date
        current_date = start_date

        state = SimulationState(
            opportunity_id=opportunity_id,
            customer_id=customer_id,
            invoice_id=f"INV_{opportunity_id}",
            amount=amount,
            due_date=due_date,
            current_date=current_date,
            days_overdue=0,
            natural_recovery_probability=natural_prob,
            is_disputed=is_disputed,
            is_opted_out=is_opted_out,
            recovery_status=RecoveryStatus.PENDING
        )

        actions_history: List[ActionType] = []
        step = 0

        local_rng = random.Random(self.random_seed) if self.random_seed is not None else random.Random()

        while state.recovery_status == RecoveryStatus.PENDING and state.days_overdue <= max_simulation_days:
            step += 1
            state.current_date = start_date + timedelta(days=state.days_overdue)

            hours_since_last = None
            if state.last_intervention_timestamp:
                hours_since_last = (state.current_date - state.last_intervention_timestamp).total_seconds() / 3600.0

            decision = self.decision_engine.evaluate_opportunity(
                opportunity_id=opportunity_id,
                amount=amount,
                natural_prob=natural_prob,
                is_disputed=is_disputed,
                is_opted_out=is_opted_out,
                retry_count=state.retry_count,
                total_interventions=state.total_interventions,
                hours_since_last_intervention=hours_since_last,
                days_overdue=state.days_overdue,
                custom_action_probs=custom_action_probs
            )

            if strategy_override is not None:
                selected_action = strategy_override
                cand_eval = [c for c in decision.candidate_evaluations if c.action == strategy_override][0]
            else:
                selected_action = decision.selected_action
                cand_eval = [c for c in decision.candidate_evaluations if c.action == selected_action][0]

            actions_history.append(selected_action)

            if selected_action != ActionType.NO_ACTION:
                state.total_interventions += 1
                state.cumulative_intervention_cost += cand_eval.intervention_cost
                state.last_intervention_timestamp = state.current_date
                if selected_action == ActionType.RETRY:
                    state.retry_count += 1

            win_prob = cand_eval.assisted_probability
            daily_recovery_prob = 1.0 - (1.0 - win_prob) ** (1.0 / float(self.window_30d))

            if crn_draws is not None and (step - 1) < len(crn_draws):
                roll = crn_draws[step - 1]
            else:
                roll = local_rng.random()

            recovery_occurred = roll < daily_recovery_prob

            if recovery_occurred:
                state.recovery_status = RecoveryStatus.RECOVERED
                state.cumulative_recovered_amount = amount
                state.recovery_timestamp = state.current_date
                state.termination_reason = (
                    TerminationReason.NATURAL_RECOVERY
                    if selected_action == ActionType.NO_ACTION
                    else TerminationReason.INTERVENTION_RECOVERY
                )

            audit_rec = AuditEventRecord(
                step_number=step,
                current_date=state.current_date,
                days_overdue=state.days_overdue,
                action_selected=selected_action,
                natural_probability=cand_eval.natural_probability,
                assisted_probability=cand_eval.assisted_probability,
                incremental_probability=cand_eval.incremental_probability,
                intervention_cost=cand_eval.intervention_cost,
                expected_incremental_revenue=cand_eval.expected_incremental_revenue,
                policy_status=cand_eval.policy_status,
                policy_reasons=cand_eval.policy_reasons,
                recovery_occured=recovery_occurred,
                recovery_status=state.recovery_status,
                details=f"Step {step} (Day {state.days_overdue}): Action {selected_action.value} executed. "
                        f"EV=+₹{cand_eval.expected_incremental_revenue:,.2f}. Recovery={recovery_occurred}"
            )
            state.audit_trail.append(audit_rec)

            if state.recovery_status == RecoveryStatus.RECOVERED:
                break

            state.days_overdue += 1

        if state.recovery_status == RecoveryStatus.PENDING:
            state.recovery_status = RecoveryStatus.EXPIRED
            state.termination_reason = TerminationReason.EXPIRED_30D

        rec_3d = False
        rec_7d = False
        rec_30d = False

        if state.recovery_status == RecoveryStatus.RECOVERED and state.recovery_timestamp:
            elapsed_days = (state.recovery_timestamp - state.due_date).days
            rec_3d = elapsed_days <= self.window_3d
            rec_7d = elapsed_days <= self.window_7d
            rec_30d = elapsed_days <= self.window_30d

        net_val = state.cumulative_recovered_amount - state.cumulative_intervention_cost

        return SimulationOutcome(
            simulation_id=sim_id,
            opportunity_id=opportunity_id,
            amount=amount,
            recovery_status=state.recovery_status,
            recovered_amount=state.cumulative_recovered_amount,
            recovery_timestamp=state.recovery_timestamp,
            recovered_within_3d=rec_3d,
            recovered_within_7d=rec_7d,
            recovered_within_30d=rec_30d,
            total_interventions=state.total_interventions,
            total_intervention_cost=state.cumulative_intervention_cost,
            net_recovered_value=round(net_val, 2),
            selected_actions_history=actions_history,
            termination_reason=state.termination_reason or TerminationReason.EXPIRED_30D,
            audit_trail=state.audit_trail
        )
