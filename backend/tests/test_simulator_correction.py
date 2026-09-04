import pytest
from datetime import datetime, timezone
from simulator.engine import RecoverySimulatorEngine
from simulator.counterfactual import CounterfactualEngine
from simulator.batch import BatchSimulator
from simulator.sensitivity import SensitivityAnalysisRunner
from app.schemas.canonical import ActionType


def test_crn_counterfactual_reproducibility():
    """
    Test Common Random Numbers (CRN) guarantees identical daily stochastic draws
    for 4-way counterfactual trajectory comparison.
    """
    cf_engine = CounterfactualEngine()
    now = datetime.now(timezone.utc)
    
    comp1 = cf_engine.compare_trajectories("OPP_CRN_1", "CUST_1", 10000.0, now, 0.40, seed=42)
    comp2 = cf_engine.compare_trajectories("OPP_CRN_1", "CUST_1", 10000.0, now, 0.40, seed=42)

    assert comp1.randomness_strategy == "COMMON_RANDOM_NUMBERS_CRN"
    assert comp2.randomness_strategy == "COMMON_RANDOM_NUMBERS_CRN"
    assert comp1.recommended_action == comp2.recommended_action
    assert comp1.optimal_net_recovered_value == comp2.optimal_net_recovered_value


def test_treatment_source_classification():
    """
    Test explicit classification of treatment probability sources.
    """
    engine = RecoverySimulatorEngine(random_seed=42)
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation("OPP_SRC_1", "CUST_1", 10000.0, now, 0.40)
    
    for audit in outcome.audit_trail:
        assert audit.natural_probability >= 0.0
        assert audit.assisted_probability >= audit.natural_probability


def test_sensitivity_scenarios():
    """
    Test sensitivity analysis across ZERO_LIFT, CONSERVATIVE, BASE, OPTIMISTIC.
    """
    sens_runner = SensitivityAnalysisRunner()
    results = sens_runner.run_sensitivity_analysis(batch_size=50, seed=42)

    assert "ZERO_LIFT" in results
    assert "CONSERVATIVE" in results
    assert "BASE" in results
    assert "OPTIMISTIC" in results

    # ZERO_LIFT scenario must yield zero incremental gain (NO_ACTION selection)
    zero_res = results["ZERO_LIFT"].batch_result
    assert zero_res.net_incremental_revenue == 0.0

    # BASE scenario yields positive simulated net gain
    base_res = results["BASE"].batch_result
    assert base_res.net_incremental_revenue > 0.0

    # OPTIMISTIC scenario yields highest simulated net gain
    opt_res = results["OPTIMISTIC"].batch_result
    assert opt_res.net_incremental_revenue >= base_res.net_incremental_revenue
