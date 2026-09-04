import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.services.execution import BoundedRecoveryExecutionEngine
from app.schemas.execution import (
    ExecutionRequest,
    ExecutionState,
    ProviderScenario,
    RecoverySourceType
)
from app.schemas.canonical import ActionType

from app.services.execution.provider import RazorpayTestModeProvider

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_api_provider():
    from app.api.v1.execution import execution_engine
    orig_provider = execution_engine.provider
    execution_engine.provider = RazorpayTestModeProvider()
    yield
    execution_engine.provider = orig_provider


@pytest.fixture
def engine():
    eng = BoundedRecoveryExecutionEngine(provider=RazorpayTestModeProvider())
    eng.reset_engine_state()
    return eng


def test_1_successful_reminder_execution(engine):
    """Scenario 1: Successful REMINDER execution."""
    req = ExecutionRequest(opportunity_id="OPP_REM_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=12000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.SUCCEEDED
    assert rec.action == ActionType.REMINDER
    assert rec.intervention_cost == 0.50
    assert rec.provider_reference is not None


def test_2_successful_retry_execution(engine):
    """Scenario 2: Successful RETRY execution."""
    req = ExecutionRequest(opportunity_id="OPP_RET_1", action=ActionType.RETRY)
    rec = engine.execute_opportunity_action(req, amount=15000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.SUCCEEDED
    assert rec.action == ActionType.RETRY
    assert rec.intervention_cost == 2.00


def test_3_successful_escalate_execution(engine):
    """Scenario 3: Successful ESCALATE execution."""
    req = ExecutionRequest(opportunity_id="OPP_ESC_1", action=ActionType.ESCALATE)
    rec = engine.execute_opportunity_action(req, amount=250000.0, natural_prob=0.10)
    
    assert rec.execution_status == ExecutionState.SUCCEEDED
    assert rec.action == ActionType.ESCALATE
    assert rec.intervention_cost == 50.00


def test_4_no_action_execution_creates_skipped_record(engine):
    """Scenario 4: NO_ACTION creates skipped record without provider call."""
    req = ExecutionRequest(opportunity_id="OPP_NOACT_1", action=ActionType.NO_ACTION)
    rec = engine.execute_opportunity_action(req, amount=5000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.SKIPPED
    assert rec.intervention_cost == 0.00
    assert "NO_ACTION_SKIPPED" in rec.provider_reference


def test_5_policy_blocked_execution(engine):
    """Scenario 5: Policy-blocked execution returns BLOCKED status."""
    req = ExecutionRequest(opportunity_id="OPP_BLK_1", action=ActionType.REMINDER)
    # Natural prob 0.999 makes expected incremental value negative/negligible -> Policy/Economic block
    rec = engine.execute_opportunity_action(req, amount=10.0, natural_prob=0.999)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "Economic Check" in rec.failure_reason or "Policy Engine Block" in rec.failure_reason


def test_6_expired_opportunity_blocked(engine):
    """Scenario 6: Expired opportunity blocked."""
    req = ExecutionRequest(opportunity_id="OPP_EXP_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, is_expired=True)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "expired" in rec.failure_reason


def test_7_disputed_invoice_blocked(engine):
    """Scenario 7: Disputed invoice blocks automated action."""
    req = ExecutionRequest(opportunity_id="OPP_DISP_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, is_disputed=True)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "dispute" in rec.failure_reason.lower()


def test_8_customer_opt_out_blocked(engine):
    """Scenario 8: Customer opt-out blocks action."""
    req = ExecutionRequest(opportunity_id="OPP_OPT_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, is_opted_out=True)
    
    assert rec.execution_status == ExecutionState.BLOCKED


def test_9_retry_limit_exceeded_blocked(engine):
    """Scenario 9: Retry limit (3) exceeded blocks RETRY action."""
    req = ExecutionRequest(opportunity_id="OPP_RETCAP_1", action=ActionType.RETRY)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, retry_count=3)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "retry limit" in rec.failure_reason.lower() or "maximum" in rec.failure_reason.lower()


def test_10_intervention_limit_exceeded_blocked(engine):
    """Scenario 10: Total intervention limit (5) exceeded blocks action."""
    req = ExecutionRequest(opportunity_id="OPP_INTCAP_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, total_interventions=5)
    
    assert rec.execution_status == ExecutionState.BLOCKED


def test_11_cooldown_blocked(engine):
    """Scenario 11: Cooldown (<24h since last intervention) blocks action."""
    req = ExecutionRequest(opportunity_id="OPP_COOL_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, hours_since_last_intervention=12.0)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "cooldown" in rec.failure_reason.lower()


def test_12_already_recovered_blocked(engine):
    """Scenario 12: Already recovered opportunity blocks action."""
    req = ExecutionRequest(opportunity_id="OPP_REC_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30, is_recovered=True)
    
    assert rec.execution_status == ExecutionState.BLOCKED
    assert "already been recovered" in rec.failure_reason


def test_13_duplicate_idempotent_request_returns_cached_record(engine):
    """Scenario 13: Duplicate request with same idempotency key returns cached record."""
    req = ExecutionRequest(opportunity_id="OPP_IDEM_1", action=ActionType.REMINDER, idempotency_key="UNIQUE_KEY_999")
    
    rec1 = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    rec2 = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    
    assert rec1.execution_id == rec2.execution_id
    assert rec2.is_idempotent_replay is True


def test_14_provider_success(engine):
    """Scenario 14: Provider scenario SUCCESS."""
    req = ExecutionRequest(opportunity_id="OPP_PSUCC_1", action=ActionType.REMINDER, provider_scenario=ProviderScenario.SUCCESS)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.SUCCEEDED


def test_15_provider_temporary_failure(engine):
    """Scenario 15: Provider scenario TEMPORARY_FAILURE."""
    req = ExecutionRequest(opportunity_id="OPP_PTEMP_1", action=ActionType.RETRY, provider_scenario=ProviderScenario.TEMPORARY_FAILURE)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.FAILED
    assert rec.failure_code == "GATEWAY_TEMPORARY_DOWN"


def test_16_provider_permanent_failure(engine):
    """Scenario 16: Provider scenario PERMANENT_FAILURE."""
    req = ExecutionRequest(opportunity_id="OPP_PPERM_1", action=ActionType.RETRY, provider_scenario=ProviderScenario.PERMANENT_FAILURE)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.FAILED
    assert rec.failure_code == "CARD_EXPIRED_PERMANENT"


def test_17_provider_timeout(engine):
    """Scenario 17: Provider scenario TIMEOUT."""
    req = ExecutionRequest(opportunity_id="OPP_PTIME_1", action=ActionType.REMINDER, provider_scenario=ProviderScenario.TIMEOUT)
    rec = engine.execute_opportunity_action(req, amount=10000.0, natural_prob=0.30)
    
    assert rec.execution_status == ExecutionState.FAILED
    assert rec.failure_code == "PROVIDER_TIMEOUT"


def test_18_audit_and_timeline_generation(engine):
    """Scenario 18 & 19 & 20: Audit event, timeline, and recovery outcome generation."""
    req = ExecutionRequest(opportunity_id="OPP_AUD_1", action=ActionType.REMINDER)
    rec = engine.execute_opportunity_action(req, amount=8000.0, natural_prob=0.35)
    
    timeline = engine.result_processor.get_timeline("OPP_AUD_1")
    audit = engine.result_processor.get_audit_trail("OPP_AUD_1")
    outcome = engine.result_processor.get_outcome("OPP_AUD_1")

    assert len(timeline) >= 2
    assert len(audit) >= 1
    assert outcome is not None
    assert outcome.recovery_source == RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY
    assert outcome.recovered_amount == 8000.0


def test_21_end_to_end_evaluate_execute_outcome_demo(engine):
    """
    Scenario 21: Final End-to-End Acceptance Test (₹80,000 overdue invoice).
    Evaluates opportunity -> selects action -> executes action -> generates recovery outcome & timeline.
    """
    opp_id = "OPP_E2E_80K"
    amount = 80000.0
    nat_prob = 0.25

    # Step 1: Decision Evaluation
    eval_res = engine.decision_engine.evaluate_opportunity(opp_id, amount, nat_prob)
    assert eval_res.selected_action in [ActionType.REMINDER, ActionType.RETRY]

    # Step 2: Bounded Execution
    exec_req = ExecutionRequest(opportunity_id=opp_id, action=eval_res.selected_action)
    exec_rec = engine.execute_opportunity_action(exec_req, amount=amount, natural_prob=nat_prob)

    assert exec_rec.execution_status == ExecutionState.SUCCEEDED
    assert exec_rec.provider_reference is not None

    # Step 3: Verification of Outcome & Timeline
    outcome = engine.result_processor.get_outcome(opp_id)
    timeline = engine.result_processor.get_timeline(opp_id)

    assert outcome is not None
    assert outcome.recovered_amount == 80000.0
    assert outcome.net_recovery_value == round(80000.0 - exec_rec.intervention_cost, 2)
    assert len(timeline) >= 2


def test_22_api_execution_endpoints_and_reset():
    """
    Scenario 22: API endpoints test (POST /execute, GET /executions/{id}, GET /timeline, GET /audit, POST /test-provider/reset).
    """
    # 1. POST /execute
    resp_exec = client.post(
        "/api/v1/opportunities/OPP_API_EXEC_100/execute",
        json={
            "action": "REMINDER",
            "amount": 50000.0,
            "natural_probability": 0.30,
            "idempotency_key": "IDEM_API_100"
        }
    )
    assert resp_exec.status_code == 200
    exec_data = resp_exec.json()
    exec_id = exec_data["execution_id"]
    assert exec_data["execution_status"] in ["SUCCEEDED", "SKIPPED"]

    # 2. GET /executions/{id}
    resp_get = client.get(f"/api/v1/executions/{exec_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["execution_id"] == exec_id

    # 3. GET /opportunities/{id}/timeline
    resp_time = client.get("/api/v1/opportunities/OPP_API_EXEC_100/timeline")
    assert resp_time.status_code == 200
    assert isinstance(resp_time.json(), list)

    # 4. GET /opportunities/{id}/audit
    resp_audit = client.get("/api/v1/opportunities/OPP_API_EXEC_100/audit")
    assert resp_audit.status_code == 200
    assert isinstance(resp_audit.json(), list)

    # 5. POST /test-provider/reset
    resp_reset = client.post("/api/v1/test-provider/reset")
    assert resp_reset.status_code == 200
    assert "reset successfully" in resp_reset.json()["message"]


def test_list_opportunities_with_recovered_outcome_overlay():
    from app.schemas.execution import DetailedRecoveryOutcomeSchema, RecoverySourceType
    from datetime import datetime, timezone
    import uuid
    from app.api.v1.execution import execution_engine

    # 1. Verify GET /api/v1/opportunities without outcomes has normal status
    res1 = client.get("/api/v1/opportunities?limit=10&seed=42")
    assert res1.status_code == 200
    items = res1.json()
    assert len(items) == 10
    opp_0 = items[0]
    assert opp_0["is_recovered"] is False
    assert opp_0["recovery_status"] == "UNRECOVERED"
    assert opp_0["policy_status"] == "ELIGIBLE"

    # 2. Inject a recovered outcome for opp_0["opportunity_id"] into execution_engine
    target_id = opp_0["opportunity_id"]
    execution_engine.result_processor.outcomes_store[target_id] = DetailedRecoveryOutcomeSchema(
        outcome_id=f"OUT_{uuid.uuid4().hex[:8].upper()}",
        opportunity_id=target_id,
        is_recovered=True,
        recovered_amount=opp_0["amount"],
        recovered_at=datetime.now(timezone.utc),
        recovery_window="30d",
        recovery_source=RecoverySourceType.TEST_MODE_EXECUTED_RECOVERY,
        action_that_preceded_recovery=opp_0["recommended_action"],
        intervention_count=1,
        total_intervention_cost=2.0,
        net_recovery_value=opp_0["amount"] - 2.0
    )

    # 3. Query GET /api/v1/opportunities again and verify overlay
    res2 = client.get("/api/v1/opportunities?limit=10&seed=42")
    assert res2.status_code == 200
    items2 = res2.json()
    target_item = next(i for i in items2 if i["opportunity_id"] == target_id)
    
    assert target_item["is_recovered"] is True
    assert target_item["recovery_status"] == "RECOVERED"
    assert target_item["policy_status"] == "RECOVERED"
    assert target_item["recovered_amount"] == opp_0["amount"]

    # Verify original decision trace & dataset fields are preserved
    assert target_item["amount"] == opp_0["amount"]
    assert target_item["natural_probability"] == opp_0["natural_probability"]
    assert target_item["assisted_probability"] == opp_0["assisted_probability"]
    assert target_item["recommended_action"] == opp_0["recommended_action"]
    assert target_item["expected_incremental_revenue"] == opp_0["expected_incremental_revenue"]

    # Clean up outcomes store
    execution_engine.result_processor.outcomes_store.clear()
