from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.canonical import ActionType, PolicyStatus


class ExecutionState(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    BLOCKED = "BLOCKED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ProviderType(str, Enum):
    TEST_MODE = "TEST_MODE"
    RAZORPAY_TEST = "RAZORPAY_TEST"
    RAZORPAY_PAYMENT_LINK = "RAZORPAY_PAYMENT_LINK"


class ProviderScenario(str, Enum):
    SUCCESS = "SUCCESS"
    TEMPORARY_FAILURE = "TEMPORARY_FAILURE"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"
    TIMEOUT = "TIMEOUT"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"
    BLOCKED = "BLOCKED"


class RecoverySourceType(str, Enum):
    NATURAL_RECOVERY = "NATURAL_RECOVERY"
    SIMULATED_ASSISTED_RECOVERY = "SIMULATED_ASSISTED_RECOVERY"
    TEST_MODE_EXECUTED_RECOVERY = "TEST_MODE_EXECUTED_RECOVERY"


class ExecutionRequest(BaseModel):
    opportunity_id: str = Field(..., description="Unique opportunity ID")
    action: ActionType = Field(..., description="Action requested to execute")
    provider: ProviderType = Field(default=ProviderType.TEST_MODE)
    idempotency_key: Optional[str] = Field(None, description="Client or auto-generated idempotency key")
    provider_scenario: ProviderScenario = Field(default=ProviderScenario.SUCCESS, description="Mock test provider outcome scenario")
    simulate_recovery_on_success: bool = Field(default=True, description="Whether to generate test-mode recovery outcome upon success")


class ExecutionRecordSchema(BaseModel):
    execution_id: str
    opportunity_id: str
    customer_id: str
    invoice_id: str
    action: ActionType
    provider: ProviderType = ProviderType.TEST_MODE
    idempotency_key: str
    requested_at: datetime
    executed_at: Optional[datetime] = None
    execution_status: ExecutionState
    failure_code: Optional[str] = None
    failure_reason: Optional[str] = None
    provider_reference: Optional[str] = None
    intervention_cost: float = 0.0
    policy_snapshot: Dict[str, Any] = Field(default_factory=dict)
    economic_snapshot: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_idempotent_replay: bool = False

    model_config = ConfigDict(from_attributes=True)


class ExecutionValidationResult(BaseModel):
    is_valid: bool
    status: ExecutionState
    blocking_reason: Optional[str] = None
    checks_passed: List[str] = Field(default_factory=list)
    checks_failed: List[str] = Field(default_factory=list)


class DetailedRecoveryOutcomeSchema(BaseModel):
    outcome_id: str
    opportunity_id: str
    is_recovered: bool
    recovered_amount: float
    recovered_at: Optional[datetime] = None
    recovery_window: str = "30d"
    recovery_source: RecoverySourceType
    action_that_preceded_recovery: Optional[ActionType] = None
    intervention_count: int = 0
    total_intervention_cost: float = 0.0
    net_recovery_value: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class OpportunityTimelineEvent(BaseModel):
    timestamp: datetime
    event_type: str
    title: str
    description: str
    actor: str = "SYSTEM"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OpportunityTimelineResponse(BaseModel):
    opportunity_id: str
    status: str
    amount_at_risk: float
    created_at: datetime
    timeline_events: List[OpportunityTimelineEvent]
