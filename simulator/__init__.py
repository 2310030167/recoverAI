"""
RecoverAI Simulator Package.
Provides controlled single opportunity simulation, 4-way counterfactual trajectory comparisons,
and batch baseline vs RecoverAI policy evaluations.
"""

from simulator.state import SimulationState, SimulationOutcome, AuditEventRecord, RecoveryStatus, TerminationReason
from simulator.engine import RecoverySimulatorEngine
from simulator.counterfactual import CounterfactualEngine, CounterfactualComparison
from simulator.batch import BatchSimulator, BatchSimulationResult

__all__ = [
    "SimulationState",
    "SimulationOutcome",
    "AuditEventRecord",
    "RecoveryStatus",
    "TerminationReason",
    "RecoverySimulatorEngine",
    "CounterfactualEngine",
    "CounterfactualComparison",
    "BatchSimulator",
    "BatchSimulationResult",
]
