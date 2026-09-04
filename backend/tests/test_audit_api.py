import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_global_audit_events_endpoint():
    """
    Test GET /api/v1/audit/events returns list of audit events.
    """
    response = client.get("/api/v1/audit/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)


def test_get_policy_guardrails_endpoint():
    """
    Test GET /api/v1/audit/policy returns policy configuration and 9 rules.
    """
    response = client.get("/api/v1/audit/policy")
    assert response.status_code == 200
    data = response.json()
    assert "thresholds" in data
    assert "rules" in data
    assert len(data["rules"]) == 9
    rule_ids = [r["id"] for r in data["rules"]]
    assert "RULE_01" in rule_ids
    assert "RULE_08" in rule_ids
    assert "RULE_09" in rule_ids
