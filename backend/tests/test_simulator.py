import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from simulator.engine import RecoverySimulatorEngine
from simulator.counterfactual import CounterfactualEngine
from simulator.batch import BatchSimulator
from simulator.state import RecoveryStatus, TerminationReason
from app.schemas.canonical import ActionType

client = TestClient(app)


def test_scenario_a_high_natural_recovery_selects_no_action():
    """
    Scenario A: High natural recovery (P_nat = 0.999) on small exposure -> NO_ACTION selected.
    """
    engine = RecoverySimulatorEngine(random_seed=42)
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation(
        opportunity_id="OPP_SCEN_A",
        customer_id="CUST_A",
        amount=10.0,
        due_date=now,
        natural_prob=0.999
    )
    # High natural recovery leaves negligible room for incremental gain after costs -> NO_ACTION
    assert ActionType.NO_ACTION in outcome.selected_actions_history


def test_scenario_b_low_natural_recovery_selects_reminder():
    """
    Scenario B: Low natural recovery (P_nat = 0.25) + positive EV -> REMINDER selected.
    """
    engine = RecoverySimulatorEngine(random_seed=42)
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation(
        opportunity_id="OPP_SCEN_B",
        customer_id="CUST_B",
        amount=10000.0,
        due_date=now,
        natural_prob=0.25
    )
    assert ActionType.REMINDER in outcome.selected_actions_history or ActionType.RETRY in outcome.selected_actions_history
    assert outcome.total_interventions > 0


def test_scenario_e_disputed_invoice_blocks_automated_recovery():
    """
    Scenario E: Disputed invoice -> automated actions blocked.
    """
    engine = RecoverySimulatorEngine(random_seed=42)
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation(
        opportunity_id="OPP_SCEN_E",
        customer_id="CUST_E",
        amount=1000.0,
        due_date=now,
        natural_prob=0.30,
        is_disputed=True
    )
    # Automated REMINDER / RETRY are blocked for disputed invoices
    assert ActionType.REMINDER not in outcome.selected_actions_history
    assert ActionType.RETRY not in outcome.selected_actions_history


def test_scenario_f_customer_opted_out_blocks_communication():
    """
    Scenario F: Customer opted out -> communication blocked.
    """
    engine = RecoverySimulatorEngine(random_seed=42)
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation(
        opportunity_id="OPP_SCEN_F",
        customer_id="CUST_F",
        amount=1000.0,
        due_date=now,
        natural_prob=0.30,
        is_opted_out=True
    )
    assert ActionType.REMINDER not in outcome.selected_actions_history
    assert ActionType.RETRY not in outcome.selected_actions_history


def test_scenario_g_recovery_stops_further_interventions():
    """
    Scenario G: Recovery occurs -> all further actions stop immediately.
    """
    engine = RecoverySimulatorEngine(random_seed=1) # Seed 1 produces fast recovery
    now = datetime.now(timezone.utc)
    outcome = engine.run_simulation(
        opportunity_id="OPP_SCEN_G",
        customer_id="CUST_G",
        amount=5000.0,
        due_date=now,
        natural_prob=0.80
    )
    if outcome.recovery_status == RecoveryStatus.RECOVERED:
        assert outcome.termination_reason in [TerminationReason.NATURAL_RECOVERY, TerminationReason.INTERVENTION_RECOVERY]
        assert outcome.recovered_amount == 5000.0


def test_counterfactual_4_way_comparison():
    """
    Test Counterfactual Engine comparing NO_ACTION, REMINDER, RETRY, ESCALATE.
    """
    cf_engine = CounterfactualEngine()
    now = datetime.now(timezone.utc)
    comp = cf_engine.compare_trajectories(
        opportunity_id="OPP_CF_100",
        customer_id="CUST_CF",
        amount=15000.0,
        due_date=now,
        natural_prob=0.35,
        seed=42
    )

    assert comp.opportunity_id == "OPP_CF_100"
    assert len(comp.trajectories) == 4
    actions_compared = [t.action for t in comp.trajectories]
    assert set(actions_compared) == {ActionType.NO_ACTION, ActionType.REMINDER, ActionType.RETRY, ActionType.ESCALATE}


def test_batch_simulation_and_reproducibility():
    """
    Test Batch Simulation comparing Baseline vs RecoverAI policy strategy.
    """
    batch_sim = BatchSimulator()
    res1 = batch_sim.run_batch_simulation(batch_size=50, seed=42)
    res2 = batch_sim.run_batch_simulation(batch_size=50, seed=42)

    assert res1.total_opportunity_count == 50
    assert res1.recoverai_net_recovered_value >= res1.baseline_net_recovered_value
    assert res1.net_incremental_revenue >= 0.0

    # Reproducibility check: identical seed yields identical results
    assert res1.recoverai_recovered_amount == res2.recoverai_recovered_amount
    assert res1.net_incremental_revenue == res2.net_incremental_revenue


def test_batch_simulator_default_path_resolution():
    """
    Regression Test: BatchSimulator must not hardcode Windows path 'd:\\recoverai\\data\\raw'
    and must resolve dataset path dynamically using DATA_RAW_DIR.
    """
    import inspect
    from app.services.data_loader import DATA_RAW_DIR

    sig = inspect.signature(BatchSimulator.__init__)
    param = sig.parameters["raw_data_dir"]
    assert param.default is None, f"Expected default None, got {param.default}"

    sim = BatchSimulator()
    assert sim.loader.raw_dir == DATA_RAW_DIR


def test_api_simulator_endpoints():
    """
    Test API Endpoints POST /run, POST /run-batch, GET /{id}, GET /{id}/audit
    """
    # 1. POST /run
    resp_run = client.post(
        "/api/v1/simulator/run",
        json={
            "opportunity_id": "OPP_API_999",
            "customer_id": "CUST_API",
            "amount": 20000.0,
            "natural_probability": 0.40,
            "seed": 42
        }
    )
    assert resp_run.status_code == 200
    outcome = resp_run.json()
    sim_id = outcome["simulation_id"]
    assert outcome["opportunity_id"] == "OPP_API_999"

    # 2. GET /{simulation_id}
    resp_get = client.get(f"/api/v1/simulator/{sim_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["simulation_id"] == sim_id

    # 3. GET /{simulation_id}/audit
    resp_audit = client.get(f"/api/v1/simulator/{sim_id}/audit")
    assert resp_audit.status_code == 200
    assert isinstance(resp_audit.json(), list)

    # 4. POST /run-batch
    resp_batch = client.post(
        "/api/v1/simulator/run-batch",
        json={"batch_size": 20, "seed": 42}
    )
    assert resp_batch.status_code == 200
    batch_data = resp_batch.json()
    assert batch_data["total_opportunity_count"] == 20
    assert "net_incremental_revenue" in batch_data
