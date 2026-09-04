from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.services.decision_engine import DecisionEngine, RecoveryDecisionExplanation
from app.schemas.canonical import ActionType
from simulator.batch import BatchSimulator
from app.core.logging import logger

router = APIRouter(prefix="/opportunities", tags=["Opportunities & Economics"])
decision_engine = DecisionEngine()
batch_simulator = BatchSimulator()


class OpportunityEvaluateRequest(BaseModel):
    amount: float = Field(..., gt=0.0, description="Monetary exposure amount at risk (INR)")
    natural_probability: float = Field(0.35, ge=0.0, le=1.0, description="P(R | X, A=0) baseline probability")
    is_disputed: bool = Field(False, description="True if invoice is currently under dispute")
    is_opted_out: bool = Field(False, description="True if customer opted out of communications")
    retry_count: int = Field(0, ge=0, description="Number of past payment retries")
    total_interventions: int = Field(0, ge=0, description="Total interventions executed so far")
    hours_since_last_intervention: Optional[float] = Field(None, description="Hours elapsed since last intervention")
    days_overdue: int = Field(0, ge=0, description="Number of days invoice is past due date")
    custom_action_probs: Optional[Dict[str, float]] = Field(None, description="Action-conditioned treatment probabilities P(R | X, A=k)")


from app.api.v1.execution import execution_engine


@router.get(
    "",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Empirical Recovery Opportunities",
    description="Fetches empirical recovery opportunities sampled deterministically from Customer Invoices Dataset."
)
async def list_opportunities_endpoint(
    limit: int = Query(100, ge=10, le=500),
    seed: int = Query(42)
):
    """
    GET /api/v1/opportunities
    """
    try:
        opps = batch_simulator.generate_empirical_opportunity_batch(batch_size=limit, seed=seed)
        
        # Enrich each opportunity with initial evaluation and execution outcome overlay
        enriched: List[Dict[str, Any]] = []
        for idx, o in enumerate(opps):
            opp_id = o["opportunity_id"]
            days_overdue = (idx * 3) % 28 # Realistic spread across 3d, 7d, 30d windows
            horizon = "3d" if days_overdue <= 3 else ("7d" if days_overdue <= 7 else "30d")

            eval_res = decision_engine.evaluate_opportunity(
                opportunity_id=opp_id,
                amount=o["amount"],
                natural_prob=o["natural_prob"],
                is_disputed=o["is_disputed"],
                is_opted_out=o["is_opted_out"],
                days_overdue=days_overdue
            )

            outcome = execution_engine.result_processor.get_outcome(opp_id)
            matching_recs = [r for r in execution_engine.execution_records.values() if r.opportunity_id == opp_id]

            is_rec = bool(outcome and outcome.is_recovered)
            rec_amt = outcome.recovered_amount if is_rec else 0.0
            rec_status = "RECOVERED" if is_rec else ("AWAITING_PAYMENT" if matching_recs else "UNRECOVERED")
            pol_status = "RECOVERED" if is_rec else eval_res.policy_status.value

            enriched.append({
                "opportunity_id": opp_id,
                "customer_id": o["customer_id"],
                "invoice_number": f"INV_{opp_id}",
                "amount": o["amount"],
                "due_date": o["due_date"].isoformat() if hasattr(o["due_date"], "isoformat") else str(o["due_date"]),
                "days_overdue": days_overdue,
                "horizon_window": horizon,
                "natural_probability": o["natural_prob"],
                "assisted_probability": eval_res.assisted_probability,
                "expected_incremental_revenue": eval_res.expected_incremental_revenue,
                "recommended_action": eval_res.selected_action.value,
                "policy_status": pol_status,
                "recovery_status": rec_status,
                "is_recovered": is_rec,
                "recovered_amount": rec_amt,
                "is_disputed": o["is_disputed"],
                "is_opted_out": o["is_opted_out"],
            })
        return enriched
    except Exception as e:
        logger.error(f"Error listing opportunities: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{id}/evaluate",
    response_model=RecoveryDecisionExplanation,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Recovery Opportunity & Select Bounded Intervention",
    description="Calculates expected incremental revenue Delta E = Amount * Delta p - Cost, evaluates policy constraints, and selects optimal action."
)
async def evaluate_opportunity_endpoint(
    id: str,
    payload: OpportunityEvaluateRequest
):
    """
    POST /api/v1/opportunities/{id}/evaluate
    """
    logger.info(f"Received opportunity evaluation request for Opportunity ID={id}, Amount=INR {payload.amount:,.2f}")

    try:
        explanation = decision_engine.evaluate_opportunity(
            opportunity_id=id,
            amount=payload.amount,
            natural_prob=payload.natural_probability,
            is_disputed=payload.is_disputed,
            is_opted_out=payload.is_opted_out,
            retry_count=payload.retry_count,
            total_interventions=payload.total_interventions,
            hours_since_last_intervention=payload.hours_since_last_intervention,
            days_overdue=payload.days_overdue,
            custom_action_probs=payload.custom_action_probs
        )

        logger.info(f"Evaluated Opportunity ID={id}: Selected Action={explanation.selected_action.value}, Expected Incremental Revenue=+INR {explanation.expected_incremental_revenue:,.2f}")
        return explanation

    except Exception as e:
        logger.error(f"Error evaluating opportunity ID={id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate opportunity economics: {str(e)}"
        )
