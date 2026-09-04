import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.economic_engine import EconomicEngine
from app.services.policy_engine import PolicyEngine, PolicyCheckStatus
from app.services.treatment_estimator import TreatmentEstimator
from app.services.decision_engine import DecisionEngine
from app.schemas.canonical import ActionType, PolicyStatus

client = TestClient(app)


def test_expected_revenue_calculation():
    """
    Test Delta E = Amount * Delta p - intervention_cost calculation.
    """
    econ_engine = EconomicEngine()
    
    # Amount = 10,000, P_nat = 0.30, P_assist = 0.50 -> Delta p = 0.20
    # Action = REMINDER (Cost = 0.50)
    # Expected Inc Rev = 10,000 * 0.20 - 0.50 = 1,999.50
    result = econ_engine.evaluate_action_economics(
        amount=10000.0,
        natural_prob=0.30,
        assisted_prob=0.50,
        action=ActionType.REMINDER
    )

    assert result.incremental_probability == 0.20
    assert result.intervention_cost == 0.50
    assert result.expected_incremental_revenue == 1999.50
    assert result.is_positive_ev is True


def test_negative_expected_value():
    """
    Test negative expected value when incremental gain does not cover cost.
    """
    econ_engine = EconomicEngine()
    
    # Amount = 100, P_nat = 0.50, P_assist = 0.51 -> Delta p = 0.01
    # Action = ESCALATE (Cost = 50.00)
    # Expected Inc Rev = 100 * 0.01 - 50.00 = -49.00
    result = econ_engine.evaluate_action_economics(
        amount=100.0,
        natural_prob=0.50,
        assisted_prob=0.51,
        action=ActionType.ESCALATE
    )

    assert result.expected_incremental_revenue == -49.00
    assert result.is_positive_ev is False


def test_policy_blocks_disputed_invoice():
    """
    Test policy engine blocks automated REMINDER and RETRY for disputed invoices.
    """
    policy_engine = PolicyEngine()
    
    res_reminder = policy_engine.evaluate_policy(
        action=ActionType.REMINDER,
        amount=10000.0,
        expected_incremental_revenue=500.0,
        is_disputed=True
    )
    assert res_reminder.is_permitted is False
    assert res_reminder.status == PolicyCheckStatus.BLOCKED
    assert "dispute" in res_reminder.reasons[0].lower()


def test_policy_blocks_cooldown_and_max_retries():
    """
    Test policy blocks action during active cooldown or max retries reached.
    """
    policy_engine = PolicyEngine(cooldown_hours=24.0, max_retry_attempts=3)

    # Active cooldown block (12h < 24h)
    res_cooldown = policy_engine.evaluate_policy(
        action=ActionType.REMINDER,
        amount=5000.0,
        expected_incremental_revenue=100.0,
        hours_since_last_intervention=12.0
    )
    assert res_cooldown.is_permitted is False

    # Max retries block (3 >= 3)
    res_retries = policy_engine.evaluate_policy(
        action=ActionType.RETRY,
        amount=5000.0,
        expected_incremental_revenue=100.0,
        retry_count=3
    )
    assert res_retries.is_permitted is False


def test_decision_engine_action_selection_and_no_action_fallback():
    """
    Test decision engine selects highest positive EV policy-permitted action,
    and falls back to NO_ACTION if no action is eligible.
    """
    decision_engine = DecisionEngine()

    # Case 1: Eligible REMINDER (+₹1,999.50 EV)
    exp1 = decision_engine.evaluate_opportunity(
        opportunity_id="OPP_TEST_001",
        amount=10000.0,
        natural_prob=0.30
    )
    assert exp1.selected_action in [ActionType.REMINDER, ActionType.RETRY]
    assert exp1.expected_incremental_revenue > 0

    # Case 2: Small amount + Disputed + Opted out -> All actions negative EV or policy-blocked -> Fallback to NO_ACTION
    exp2 = decision_engine.evaluate_opportunity(
        opportunity_id="OPP_TEST_002",
        amount=100.0,
        natural_prob=0.30,
        is_disputed=True,
        is_opted_out=True
    )
    assert exp2.selected_action == ActionType.NO_ACTION


def test_api_evaluate_opportunity_endpoint():
    """
    Test API endpoint POST /api/v1/opportunities/{id}/evaluate
    """
    response = client.post(
        "/api/v1/opportunities/OPP_HTTP_100/evaluate",
        json={
            "amount": 25000.0,
            "natural_probability": 0.40,
            "is_disputed": False,
            "days_overdue": 5
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["opportunity_id"] == "OPP_HTTP_100"
    assert "selected_action" in data
    assert "expected_incremental_revenue" in data
    assert "candidate_evaluations" in data
    assert len(data["candidate_evaluations"]) == 4
