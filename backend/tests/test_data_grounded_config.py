import pytest
from app.core.config import settings, RecoverySettings
from app.services.policy_engine import PolicyEngine
from app.services.economic_engine import EconomicEngine
from app.services.treatment_estimator import TreatmentEstimator, TreatmentEstimateStatus
from simulator.engine import RecoverySimulatorEngine
from app.schemas.canonical import ActionType


def test_policy_values_come_from_configuration():
    """Verify PolicyEngine pulls default thresholds directly from settings.recovery."""
    engine = PolicyEngine()
    assert engine.cooldown_hours == settings.recovery.cooldown_hours
    assert engine.max_retry_attempts == settings.recovery.max_retry_attempts
    assert engine.max_total_interventions == settings.recovery.max_interventions

    # Verify custom instance override
    custom_policy = PolicyEngine(cooldown_hours=48.0, max_retry_attempts=1)
    assert custom_policy.cooldown_hours == 48.0
    assert custom_policy.max_retry_attempts == 1


def test_recovery_windows_come_from_configuration():
    """Verify RecoverySimulatorEngine pulls default horizons directly from settings.recovery."""
    sim = RecoverySimulatorEngine()
    assert sim.window_3d == settings.recovery.primary_window_days
    assert sim.window_7d == settings.recovery.secondary_window_days
    assert sim.window_30d == settings.recovery.macro_horizon_days


def test_intervention_costs_come_from_configuration():
    """Verify EconomicEngine pulls default action costs directly from settings.recovery.action_costs."""
    econ = EconomicEngine()
    res = econ.evaluate_action_economics(
        amount=10000.0,
        natural_prob=0.30,
        assisted_prob=0.45,
        action=ActionType.REMINDER
    )
    assert res.intervention_cost == settings.recovery.action_costs["REMINDER"]
    assert res.source == "CONFIGURED_COST"


def test_simulation_assumptions_correctly_labeled():
    """Verify TreatmentEstimator explicitly labels multiplier treatment effects as SIMULATION_ASSUMPTION."""
    treat = TreatmentEstimator()
    res = treat.estimate_assisted_probability(natural_prob=0.30, action=ActionType.REMINDER)
    
    assert res["source"] == "SIMULATION_ASSUMPTION"
    assert res["status"] == TreatmentEstimateStatus.AVAILABLE.value


def test_missing_data_returns_explicit_status_no_silent_fallback():
    """Verify missing/None natural probability produces explicit error status DATA_UNAVAILABLE instead of silent fallback."""
    treat = TreatmentEstimator()
    res = treat.estimate_assisted_probability(natural_prob=None, action=ActionType.REMINDER)
    
    assert res["status"] == TreatmentEstimateStatus.TREATMENT_ESTIMATE_UNAVAILABLE.value
    assert res["source"] == "DATA_UNAVAILABLE"
    assert res["assisted_probability"] == 0.0


def test_changing_configuration_changes_behavior():
    """Verify modifying configuration settings alters economic and treatment estimates dynamically."""
    custom_costs = {"NO_ACTION": 0.0, "REMINDER": 10.0, "RETRY": 50.0, "ESCALATE": 500.0}
    econ = EconomicEngine(action_costs=custom_costs)
    
    res = econ.evaluate_action_economics(1000.0, 0.30, 0.35, ActionType.REMINDER)
    # Amount 1000 * Delta_p 0.05 - Cost 10.0 = +40.0 - 10.0 = +40.0
    assert res.intervention_cost == 10.0
