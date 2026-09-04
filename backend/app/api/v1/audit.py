from fastapi import APIRouter, status
from typing import Dict, Any, List
from app.api.v1.execution import execution_engine
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/audit", tags=["Audit & Policy Governance"])


@router.get(
    "/events",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Portfolio Global Audit Trail",
    description="Fetches real-time portfolio-level audit events across all execution and recovery actions."
)
async def get_global_audit_events_endpoint():
    """
    GET /api/v1/audit/events
    """
    events = execution_engine.result_processor.get_all_audit_events()
    
    # Format timestamps cleanly for JSON serialization
    serialized: List[Dict[str, Any]] = []
    for e in events:
        item = dict(e)
        if hasattr(item.get("timestamp"), "isoformat"):
            item["timestamp"] = item["timestamp"].isoformat()
        serialized.append(item)

    logger.info(f"Fetched {len(serialized)} global audit events.")
    return serialized


@router.get(
    "/policy",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Policy & Autonomy Guardrails Config",
    description="Returns centralized policy thresholds and active AI safety guardrail boundaries."
)
async def get_policy_guardrails_endpoint():
    """
    GET /api/v1/audit/policy
    """
    rec = settings.recovery
    return {
        "source": "CONFIGURED",
        "parameter_ref": "app.core.config.settings.recovery",
        "thresholds": {
            "cooldown_hours": rec.cooldown_hours,
            "max_retry_attempts": rec.max_retry_attempts,
            "max_interventions": rec.max_interventions,
            "min_expected_value": rec.min_expected_value,
            "escalation_amount_threshold": rec.escalation_amount_threshold,
            "escalation_days_overdue": rec.escalation_days_overdue,
        },
        "rules": [
            {
                "id": "RULE_01",
                "name": "Positive Expected Value Required",
                "category": "ECONOMIC_EV",
                "description": "Expected incremental revenue EV = Amount * Delta p - Cost must be strictly > ₹0.",
                "threshold": f"> ₹{rec.min_expected_value:.2f}",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_02",
                "name": "Customer Opt-Out Protection",
                "category": "COMPLIANCE",
                "description": "Automated recovery & communications are immediately blocked if customer opted out.",
                "threshold": "Opt-Out Flag == True -> BLOCK",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_03",
                "name": "Disputed Invoice Protection",
                "category": "COMPLIANCE",
                "description": "Automated recovery actions are blocked for invoices marked under dispute.",
                "threshold": "Dispute Flag == True -> BLOCK",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_04",
                "name": "Intervention Cooldown Window",
                "category": "OPERATIONAL",
                "description": "Requires minimum hours between consecutive intervention attempts on same opportunity.",
                "threshold": f"{rec.cooldown_hours:.1f} Hours",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_05",
                "name": "Maximum Payment Retry Cap",
                "category": "OPERATIONAL",
                "description": "Strict limit on payment retry attempts to prevent customer fatigue.",
                "threshold": f"{rec.max_retry_attempts} Retries Max",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_06",
                "name": "Maximum Total Interventions Cap",
                "category": "OPERATIONAL",
                "description": "Hard cap on cumulative interventions executed per opportunity.",
                "threshold": f"{rec.max_interventions} Interventions Cap",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_07",
                "name": "Escalation Criteria",
                "category": "GOVERNANCE",
                "description": "ESCALATE action permitted only if overdue >= 14d, amount >= ₹100k, or invoice disputed.",
                "threshold": f">= {rec.escalation_days_overdue}d OR >= ₹{rec.escalation_amount_threshold:,.0f} OR Disputed",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_08",
                "name": "Recovery Stopping Rule",
                "category": "SYSTEM_SAFETY",
                "description": "Once payment status is observed as PAID/RECOVERED, all further automated actions are permanently blocked.",
                "threshold": "Recovery Status == RECOVERED -> BLOCK ALL",
                "status": "ACTIVE_ENFORCED"
            },
            {
                "id": "RULE_09",
                "name": "Strict Idempotency Guardrail",
                "category": "SYSTEM_SAFETY",
                "description": "Duplicate execution requests return cached execution record to prevent duplicate payment link creation.",
                "threshold": "Idempotency Key Check -> CACHED RECORD",
                "status": "ACTIVE_ENFORCED"
            }
        ]
    }
