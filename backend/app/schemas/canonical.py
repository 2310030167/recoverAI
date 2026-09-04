from datetime import datetime
from typing import Optional, List, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ActionType(str, Enum):
    NO_ACTION = "NO_ACTION"
    REMINDER = "REMINDER"
    RETRY = "RETRY"
    ESCALATE = "ESCALATE"


class OpportunityStatus(str, Enum):
    DETECTED = "DETECTED"
    EVALUATING = "EVALUATING"
    INTERVENTION_PENDING = "INTERVENTION_PENDING"
    RECOVERED = "RECOVERED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"
    CLOSED_NO_ACTION = "CLOSED_NO_ACTION"


class PolicyStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    COOLDOWN_BLOCKED = "COOLDOWN_BLOCKED"
    MAX_ATTEMPTS_EXCEEDED = "MAX_ATTEMPTS_EXCEEDED"
    DISPUTE_BLOCKED = "DISPUTE_BLOCKED"
    INSUFFICIENT_ECONOMIC_VALUE = "INSUFFICIENT_ECONOMIC_VALUE"


class ExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# ------------------------------------------------------------------------------
# Pydantic Domain Schemas
# ------------------------------------------------------------------------------

class MerchantBase(BaseModel):
    merchant_code: str
    name: str
    industry: Optional[str] = None
    currency: str = "INR"

class MerchantCreate(MerchantBase):
    pass

class MerchantSchema(MerchantBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    merchant_id: str
    external_customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    segment: Optional[str] = None
    tenure_months: float = 0.0
    account_health_score: float = 100.0
    paperless_billing: bool = True
    total_historical_revenue: float = 0.0

class CustomerCreate(CustomerBase):
    pass

class CustomerSchema(CustomerBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    merchant_id: str
    customer_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    amount: float
    currency: str = "INR"
    status: str = "OPEN"
    is_open: bool = True
    is_disputed: bool = False
    payment_terms: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    clear_date: Optional[datetime] = None

class InvoiceSchema(InvoiceBase):
    id: str
    clear_date: Optional[datetime] = None
    days_late: Optional[int] = None
    days_to_pay: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentAttemptBase(BaseModel):
    merchant_id: str
    customer_id: str
    invoice_id: Optional[str] = None
    transaction_reference: str
    amount: float
    currency: str = "INR"
    payment_method: str
    status: str
    failure_reason: Optional[str] = None
    attempt_number: int = 1
    sender_bank: Optional[str] = None
    receiver_bank: Optional[str] = None
    timestamp: datetime

class PaymentAttemptCreate(PaymentAttemptBase):
    pass

class PaymentAttemptSchema(PaymentAttemptBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CheckoutSessionBase(BaseModel):
    merchant_id: str
    customer_id: Optional[str] = None
    session_reference: str
    administrative_duration: float = 0.0
    informational_duration: float = 0.0
    product_related_duration: float = 0.0
    bounce_rate: float = 0.0
    exit_rate: float = 0.0
    page_value: float = 0.0
    special_day: float = 0.0
    visitor_type: str = "Returning_Visitor"
    weekend: bool = False
    revenue_converted: bool = False
    session_started_at: datetime

class CheckoutSessionCreate(CheckoutSessionBase):
    pass

class CheckoutSessionSchema(CheckoutSessionBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecoveryOpportunityBase(BaseModel):
    merchant_id: str
    customer_id: str
    source_type: str
    source_reference_id: str
    amount_at_risk: float
    currency: str = "INR"
    detected_at: datetime
    status: OpportunityStatus = OpportunityStatus.DETECTED
    risk_score: Optional[float] = None
    natural_recovery_probability: Optional[float] = None
    assisted_recovery_probability: Optional[float] = None
    expected_incremental_revenue: Optional[float] = None
    recommended_action: Optional[ActionType] = None
    policy_status: Optional[PolicyStatus] = None

class RecoveryOpportunityCreate(RecoveryOpportunityBase):
    pass

class RecoveryOpportunitySchema(RecoveryOpportunityBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InterventionEventBase(BaseModel):
    opportunity_id: str
    action: ActionType
    executed_at: datetime
    reason: str
    expected_value: float
    cost: float
    attempt_number: int = 1
    policy_decision: str = "APPROVED"
    execution_status: ExecutionStatus = ExecutionStatus.EXECUTED

class InterventionEventCreate(InterventionEventBase):
    pass

class InterventionEventSchema(InterventionEventBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecoveryOutcomeBase(BaseModel):
    opportunity_id: str
    intervention_id: Optional[str] = None
    is_recovered: bool
    recovered_amount: float = 0.0
    recovery_timestamp: Optional[datetime] = None
    outcome_type: str = "UNRECOVERED"
    days_to_recovery: Optional[float] = None

class RecoveryOutcomeCreate(RecoveryOutcomeBase):
    pass

class RecoveryOutcomeSchema(RecoveryOutcomeBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditEventBase(BaseModel):
    opportunity_id: Optional[str] = None
    event_type: str
    actor: str = "SYSTEM"
    details: str
    timestamp: datetime

class AuditEventCreate(AuditEventBase):
    pass

class AuditEventSchema(AuditEventBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
