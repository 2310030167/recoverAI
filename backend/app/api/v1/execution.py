from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.execution import (
    ExecutionRequest,
    ExecutionRecordSchema,
    DetailedRecoveryOutcomeSchema,
    OpportunityTimelineResponse,
    OpportunityTimelineEvent
)
from app.schemas.canonical import ActionType
from app.services.execution import BoundedRecoveryExecutionEngine
from app.core.logging import logger

router = APIRouter(tags=["Bounded Recovery Execution Engine"])

execution_engine = BoundedRecoveryExecutionEngine()


class OpportunityExecuteRequest(BaseModel):
    action: ActionType = Field(..., description="Requested action to execute")
    amount: float = Field(10000.0, gt=0.0, description="Invoice amount in INR")
    natural_probability: float = Field(0.35, ge=0.0, le=1.0)
    customer_id: str = "CUST_DEFAULT"
    invoice_id: str = "INV_DEFAULT"
    is_disputed: bool = False
    is_opted_out: bool = False
    idempotency_key: Optional[str] = None
    provider_scenario: str = "SUCCESS"


@router.post(
    "/opportunities/{opportunity_id}/execute",
    response_model=ExecutionRecordSchema,
    status_code=status.HTTP_200_OK,
    summary="Execute Bounded Opportunity Action",
    description="Revalidates policy and executes requested action via test-mode provider."
)
async def execute_opportunity_action_endpoint(
    opportunity_id: str,
    payload: OpportunityExecuteRequest
):
    """
    POST /api/v1/opportunities/{opportunity_id}/execute
    """
    logger.info(f"Received execution request for Opportunity ID={opportunity_id}, Action={payload.action.value}")
    try:
        from app.schemas.execution import ProviderScenario
        scen = ProviderScenario(payload.provider_scenario) if payload.provider_scenario in ProviderScenario.__members__ else ProviderScenario.SUCCESS

        req = ExecutionRequest(
            opportunity_id=opportunity_id,
            action=payload.action,
            idempotency_key=payload.idempotency_key,
            provider_scenario=scen
        )

        record = execution_engine.execute_opportunity_action(
            request=req,
            amount=payload.amount,
            natural_prob=payload.natural_probability,
            customer_id=payload.customer_id,
            invoice_id=payload.invoice_id,
            is_disputed=payload.is_disputed,
            is_opted_out=payload.is_opted_out
        )
        return record
    except Exception as e:
        logger.error(f"Execution endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/executions/{execution_id}",
    response_model=ExecutionRecordSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Execution Record Details",
    description="Fetches detailed execution record by execution ID."
)
async def get_execution_endpoint(execution_id: str):
    """
    GET /api/v1/executions/{execution_id}
    """
    record = execution_engine.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Execution ID '{execution_id}' not found.")
    return record


@router.get(
    "/opportunities/{opportunity_id}/timeline",
    response_model=List[OpportunityTimelineEvent],
    status_code=status.HTTP_200_OK,
    summary="Get Opportunity Timeline",
    description="Fetches chronologically ordered opportunity timeline events."
)
async def get_opportunity_timeline_endpoint(opportunity_id: str):
    """
    GET /api/v1/opportunities/{opportunity_id}/timeline
    """
    timeline = execution_engine.result_processor.get_timeline(opportunity_id)
    return timeline


@router.get(
    "/opportunities/{opportunity_id}/audit",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Opportunity Audit Trail",
    description="Fetches detailed audit event log records for an opportunity."
)
async def get_opportunity_audit_endpoint(opportunity_id: str):
    """
    GET /api/v1/opportunities/{opportunity_id}/audit
    """
    audit = execution_engine.result_processor.get_audit_trail(opportunity_id)
    return audit


@router.post(
    "/test-provider/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset Test Provider & Engine State",
    description="Resets test provider logs, idempotency cache, and execution stores."
)
async def reset_test_provider_endpoint():
    """
    POST /api/v1/test-provider/reset
    """
    execution_engine.reset_engine_state()
    return {"message": "Execution engine and test provider state reset successfully."}


@router.post(
    "/opportunities/{opportunity_id}/sync-payment",
    status_code=status.HTTP_200_OK,
    summary="Synchronize Razorpay Payment Link Status",
    description="Live-queries Razorpay Payment Links API to verify payment status and update recovery settlement."
)
async def sync_opportunity_payment_endpoint(opportunity_id: str):
    """
    POST /api/v1/opportunities/{opportunity_id}/sync-payment
    """
    res = execution_engine.sync_opportunity_payment(opportunity_id)
    if not res.get("success", False) and res.get("error_code") == "EXECUTION_RECORD_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error_message", "Execution record not found")
        )
    return res
