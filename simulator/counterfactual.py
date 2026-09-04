import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from simulator.state import SimulationOutcome, RecoveryStatus
from simulator.engine import RecoverySimulatorEngine
from app.schemas.canonical import ActionType
from app.core.logging import logger


class TrajectoryResult(BaseModel):
    action: ActionType
    outcome: SimulationOutcome


class CounterfactualComparison(BaseModel):
    """
    Simulated Counterfactual Trajectory Comparison with Common Random Numbers (CRN).
    Compares outcomes of NO_ACTION, REMINDER, RETRY, and ESCALATE trajectories
    starting from identical initial opportunity state S0 under identical stochastic draws.

    DISCLAIMER:
    This comparison represents a SIMULATED counterfactual trajectory analysis.
    It is NOT an empirical causal inference claim.
    """
    opportunity_id: str
    amount: float
    due_date: datetime
    natural_probability: float
    trajectories: List[TrajectoryResult]
    recommended_action: ActionType
    optimal_net_recovered_value: float
    randomness_strategy: str = "COMMON_RANDOM_NUMBERS_CRN"


class CounterfactualEngine:
    """
    Counterfactual Trajectory Engine with Common Random Numbers (CRN) Variance Reduction.
    Simulates and compares parallel action paths for a recovery opportunity.
    """

    def __init__(self, simulator_engine: Optional[RecoverySimulatorEngine] = None):
        self.simulator_engine = simulator_engine or RecoverySimulatorEngine()

    def compare_trajectories(
        self,
        opportunity_id: str,
        customer_id: str,
        amount: float,
        due_date: datetime,
        natural_prob: float,
        is_disputed: bool = False,
        is_opted_out: bool = False,
        seed: int = 42
    ) -> CounterfactualComparison:
        """
        Simulate 4 parallel potential trajectories from identical initial state S0
        using Common Random Numbers (CRN) to ensure identical random noise streams.
        """
        candidate_actions = [
            ActionType.NO_ACTION,
            ActionType.REMINDER,
            ActionType.RETRY,
            ActionType.ESCALATE,
        ]

        # Generate CRN uniform random draws for 35 daily steps
        rng = random.Random(seed)
        crn_draws = [rng.random() for _ in range(35)]

        trajectories: List[TrajectoryResult] = []
        best_net_val = -float("inf")
        recommended_act = ActionType.NO_ACTION

        for act in candidate_actions:
            # Pass pre-generated crn_draws for identical stochastic resolution
            engine = RecoverySimulatorEngine(random_seed=seed)
            outcome = engine.run_simulation(
                opportunity_id=opportunity_id,
                customer_id=customer_id,
                amount=amount,
                due_date=due_date,
                natural_prob=natural_prob,
                is_disputed=is_disputed,
                is_opted_out=is_opted_out,
                strategy_override=act,
                crn_draws=crn_draws
            )

            trajectories.append(TrajectoryResult(action=act, outcome=outcome))

            if outcome.net_recovered_value > best_net_val:
                best_net_val = outcome.net_recovered_value
                recommended_act = act

        logger.info(
            f"CRN Counterfactual Analysis Completed for Opportunity ID={opportunity_id}: "
            f"Optimal Action={recommended_act.value}, Net Recovered Value=₹{best_net_val:,.2f}"
        )

        return CounterfactualComparison(
            opportunity_id=opportunity_id,
            amount=amount,
            due_date=due_date,
            natural_probability=natural_prob,
            trajectories=trajectories,
            recommended_action=recommended_act,
            optimal_net_recovered_value=round(best_net_val, 2),
            randomness_strategy="COMMON_RANDOM_NUMBERS_CRN"
        )
