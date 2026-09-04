from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.canonical import ActionType, PolicyStatus
from app.services.economic_engine import EconomicEvaluationResult
from app.services.policy_engine import PolicyCheckStatus


class RecoveryStatus(str, Enum):
    PENDING = "PENDING"
    RECOVERED = "RECOVERED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"


class TerminationReason(str, Enum):
    NATURAL_RECOVERY = "NATURAL_RECOVERY"
    INTERVENTION_RECOVERY = "INTERVENTION_RECOVERY"
    EXPIRED_3D = "EXPIRED_3D"
    EXPIRED_7D = "EXPIRED_7D"
    EXPIRED_30D = "EXPIRED_30D"
    POLICY_CAP_REACHED = "POLICY_CAP_REACHED"
    RETRY_CAP_REACHED = "RETRY_CAP_REACHED"
    CUSTOMER_OPT_OUT = "CUSTOMER_OPT_OUT"
    DISPUTE_BLOCKED = "DISPUTE_BLOCKED"
    NEGATIVE_EV_STOP = "NEGATIVE_EV_STOP"
    NO_ELIGIBLE_ACTION = "NO_ELIGIBLE_ACTION"


class AuditEventRecord(BaseModel):
    """
    Step-by-step timeline audit record for recovery simulation.
    """
    step_number: int
    current_date: datetime
    days_overdue: int
    action_selected: ActionType
    natural_probability: float
    assisted_probability: float
    incremental_probability: float
    intervention_cost: float
    expected_incremental_revenue: float
    policy_status: PolicyCheckStatus
    policy_reasons: List[str]
    recovery_occured: bool
    recovery_status: RecoveryStatus
    details: str


class SimulationState(BaseModel):
    """
    State representation of an active recovery opportunity during simulation.
    """
    opportunity_id: str
    customer_id: str
    invoice_id: str
    amount: float
    due_date: datetime
    current_date: datetime
    days_overdue: int = 0
    customer_historical_behavior: Dict[str, Any] = Field(default_factory=dict)
    natural_recovery_probability: float = 0.50
    current_action: ActionType = ActionType.NO_ACTION
    total_interventions: int = 0
    retry_count: int = 0
    last_intervention_timestamp: Optional[datetime] = None
    is_disputed: bool = False
    is_opted_out: bool = False
    recovery_status: RecoveryStatus = RecoveryStatus.PENDING
    cumulative_recovered_amount: float = 0.0
    cumulative_intervention_cost: float = 0.0
    recovery_timestamp: Optional[datetime] = None
    termination_reason: Optional[TerminationReason] = None
    audit_trail: List[AuditEventRecord] = Field(default_factory=list)


class SimulationOutcome(BaseModel):
    """
    Final summary outcome object produced by a recovery simulation.
    """
    simulation_id: str
    opportunity_id: str
    amount: float
    recovery_status: RecoveryStatus
    recovered_amount: float
    recovery_timestamp: Optional[datetime] = None
    recovered_within_3d: bool = False
    recovered_within_7d: bool = False
    recovered_within_30d: bool = False
    total_interventions: int
    total_intervention_cost: float
    net_recovered_value: float = Field(..., description="Recovered Amount - Total Intervention Cost")
    selected_actions_history: List[ActionType]
    termination_reason: TerminationReason
    audit_trail: List[AuditEventRecord]
