from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.batch import BatchSimulator, BatchSimulationResult
from app.core.logging import logger

SENSITIVITY_SCENARIOS: Dict[str, Dict[str, float]] = {
    "ZERO_LIFT": {
        "NO_ACTION": 1.00,
        "REMINDER": 1.00,
        "RETRY": 1.00,
        "ESCALATE": 1.00,
    },
    "CONSERVATIVE": {
        "NO_ACTION": 1.00,
        "REMINDER": 1.10,
        "RETRY": 1.15,
        "ESCALATE": 1.08,
    },
    "BASE": {
        "NO_ACTION": 1.00,
        "REMINDER": 1.20,
        "RETRY": 1.35,
        "ESCALATE": 1.15,
    },
    "OPTIMISTIC": {
        "NO_ACTION": 1.00,
        "REMINDER": 1.35,
        "RETRY": 1.50,
        "ESCALATE": 1.25,
    },
}


class SensitivityScenarioResult(BaseModel):
    scenario_name: str
    action_multipliers: Dict[str, float]
    batch_result: BatchSimulationResult


class SensitivityAnalysisRunner:
    """
    Treatment-Effect Sensitivity Analysis Evaluator for RecoverAI.
    Evaluates ZERO_LIFT, CONSERVATIVE, BASE, and OPTIMISTIC action treatment scenarios.
    """

    def __init__(self, raw_data_dir: Optional[str] = None):
        self.batch_simulator = BatchSimulator(raw_data_dir=raw_data_dir)

    def run_sensitivity_analysis(
        self,
        batch_size: int = 100,
        seed: int = 42
    ) -> Dict[str, SensitivityScenarioResult]:
        """
        Run batch simulation under 4 sensitivity scenarios on identical invoice batch.
        """
        results: Dict[str, SensitivityScenarioResult] = {}
        
        # Pre-generate single opportunity batch for identical invoice baseline comparison
        opps = self.batch_simulator.generate_empirical_opportunity_batch(batch_size=batch_size, seed=seed)

        for name, multipliers in SENSITIVITY_SCENARIOS.items():
            logger.info(f"Running Sensitivity Scenario: {name} (Multipliers={multipliers})")
            batch_res = self.batch_simulator.run_batch_simulation(
                batch_size=batch_size,
                seed=seed,
                custom_opportunities=opps,
                custom_action_multipliers=multipliers
            )
            results[name] = SensitivityScenarioResult(
                scenario_name=name,
                action_multipliers=multipliers,
                batch_result=batch_res
            )

        return results
