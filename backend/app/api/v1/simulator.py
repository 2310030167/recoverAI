from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from simulator.engine import RecoverySimulatorEngine
from simulator.batch import BatchSimulator, BatchSimulationResult
from simulator.counterfactual import CounterfactualEngine, CounterfactualComparison
from simulator.state import SimulationOutcome, AuditEventRecord
from app.schemas.canonical import ActionType
from app.core.logging import logger

router = APIRouter(prefix="/simulator", tags=["Recovery Simulator & Counterfactuals"])

# Persistent simulation store for API fetch requests
SIMULATION_STORE: Dict[str, SimulationOutcome] = {}

simulator_engine = RecoverySimulatorEngine()
counterfactual_engine = CounterfactualEngine()
batch_simulator = BatchSimulator()


class RunSimulationRequest(BaseModel):
    opportunity_id: str = Field(..., description="Unique opportunity ID")
    customer_id: str = Field(..., description="Customer ID")
    amount: float = Field(..., gt=0.0, description="Invoice amount in INR")
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    natural_probability: float = Field(0.35, ge=0.0, le=1.0)
    is_disputed: bool = False
    is_opted_out: bool = False
    strategy_override: Optional[ActionType] = None
    seed: Optional[int] = 42


class RunBatchRequest(BaseModel):
    batch_size: int = Field(100, ge=10, le=1000)
    seed: int = Field(42)


@router.post(
    "/run",
    response_model=SimulationOutcome,
    status_code=status.HTTP_200_OK,
    summary="Run Single Opportunity Recovery Simulation",
    description="Simulates opportunity progression over time steps and reports recovery outcome."
)
async def run_single_simulation_endpoint(payload: RunSimulationRequest):
    """
    POST /api/v1/simulator/run
    """
    logger.info(f"Received single simulation request for Opportunity ID={payload.opportunity_id}")
    try:
        engine = RecoverySimulatorEngine(random_seed=payload.seed)
        outcome = engine.run_simulation(
            opportunity_id=payload.opportunity_id,
            customer_id=payload.customer_id,
            amount=payload.amount,
            due_date=payload.due_date,
            natural_prob=payload.natural_probability,
            is_disputed=payload.is_disputed,
            is_opted_out=payload.is_opted_out,
            strategy_override=payload.strategy_override
        )
        SIMULATION_STORE[outcome.simulation_id] = outcome
        return outcome
    except Exception as e:
        logger.error(f"Failed to run simulation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/run-batch",
    response_model=BatchSimulationResult,
    status_code=status.HTTP_200_OK,
    summary="Run Batch Simulation Baseline vs RecoverAI Comparison",
    description="Executes deterministic batch simulation comparing Baseline (NO_ACTION) vs RecoverAI policy-driven strategy."
)
async def run_batch_simulation_endpoint(payload: RunBatchRequest):
    """
    POST /api/v1/simulator/run-batch
    """
    logger.info(f"Received batch simulation request: Batch Size={payload.batch_size}, Seed={payload.seed}")
    try:
        batch_result = batch_simulator.run_batch_simulation(
            batch_size=payload.batch_size,
            seed=payload.seed
        )
        return batch_result
    except Exception as e:
        logger.error(f"Failed to run batch simulation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{simulation_id}",
    response_model=SimulationOutcome,
    status_code=status.HTTP_200_OK,
    summary="Get Simulation Details",
    description="Fetches stored simulation details by simulation ID."
)
async def get_simulation_endpoint(simulation_id: str):
    """
    GET /api/v1/simulator/{simulation_id}
    """
    if simulation_id not in SIMULATION_STORE:
        raise HTTPException(status_code=404, detail=f"Simulation ID '{simulation_id}' not found.")
    return SIMULATION_STORE[simulation_id]


@router.get(
    "/{simulation_id}/audit",
    response_model=List[AuditEventRecord],
    status_code=status.HTTP_200_OK,
    summary="Get Simulation Audit Trail",
    description="Fetches step-by-step timeline audit records for a simulation."
)
async def get_simulation_audit_endpoint(simulation_id: str):
    """
    GET /api/v1/simulator/{simulation_id}/audit
    """
    if simulation_id not in SIMULATION_STORE:
        raise HTTPException(status_code=404, detail=f"Simulation ID '{simulation_id}' not found.")
    return SIMULATION_STORE[simulation_id].audit_trail
