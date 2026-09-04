import pytest
from datetime import datetime, timezone
from app.schemas.canonical import (
    MerchantCreate,
    CustomerCreate,
    InvoiceCreate,
    PaymentAttemptCreate,
    CheckoutSessionCreate,
    RecoveryOpportunityCreate,
    InterventionEventCreate,
    RecoveryOutcomeCreate,
    AuditEventCreate,
    ActionType,
    OpportunityStatus,
    PolicyStatus,
    ExecutionStatus,
)
from app.models.canonical import (
    Merchant,
    Customer,
    Invoice,
    PaymentAttempt,
    CheckoutSession,
    RecoveryOpportunity,
    InterventionEvent,
    RecoveryOutcome,
    AuditEvent,
)


def test_merchant_schema_and_model():
    m_create = MerchantCreate(
        merchant_code="MCH_TEST_001",
        name="Test Merchant Pvt Ltd",
        industry="E-Commerce",
        currency="INR"
    )
    assert m_create.merchant_code == "MCH_TEST_001"

    m_orm = Merchant(
        merchant_code=m_create.merchant_code,
        name=m_create.name,
        industry=m_create.industry,
        currency=m_create.currency
    )
    assert m_orm.merchant_code == "MCH_TEST_001"
    assert m_orm.currency == "INR"


def test_customer_schema_and_model():
    c_create = CustomerCreate(
        merchant_id="mch-123",
        external_customer_id="CUST_99",
        name="Acme Corp",
        email="billing@acme.com",
        segment="Enterprise",
        tenure_months=24.5,
        account_health_score=85.0,
        paperless_billing=True,
        total_historical_revenue=150000.0
    )
    assert c_create.external_customer_id == "CUST_99"

    c_orm = Customer(
        merchant_id=c_create.merchant_id,
        external_customer_id=c_create.external_customer_id,
        name=c_create.name,
        email=c_create.email,
        segment=c_create.segment,
        tenure_months=c_create.tenure_months,
        account_health_score=c_create.account_health_score,
        paperless_billing=c_create.paperless_billing,
        total_historical_revenue=c_create.total_historical_revenue
    )
    assert c_orm.account_health_score == 85.0


def test_invoice_schema_and_model():
    now = datetime.now(timezone.utc)
    inv_create = InvoiceCreate(
        merchant_id="mch-123",
        customer_id="cust-456",
        invoice_number="INV-2026-001",
        invoice_date=now,
        due_date=now,
        amount=25000.0,
        currency="INR",
        status="OPEN",
        is_open=True,
        is_disputed=False,
        payment_terms="Net30"
    )
    assert inv_create.amount == 25000.0

    inv_orm = Invoice(
        merchant_id=inv_create.merchant_id,
        customer_id=inv_create.customer_id,
        invoice_number=inv_create.invoice_number,
        invoice_date=inv_create.invoice_date,
        due_date=inv_create.due_date,
        amount=inv_create.amount,
        currency=inv_create.currency,
        status=inv_create.status,
        is_open=inv_create.is_open,
        is_disputed=inv_create.is_disputed,
        payment_terms=inv_create.payment_terms
    )
    assert inv_orm.invoice_number == "INV-2026-001"


def test_recovery_opportunity_schema_and_model():
    now = datetime.now(timezone.utc)
    opp_create = RecoveryOpportunityCreate(
        merchant_id="mch-123",
        customer_id="cust-456",
        source_type="INVOICE",
        source_reference_id="INV-2026-001",
        amount_at_risk=25000.0,
        currency="INR",
        detected_at=now,
        status=OpportunityStatus.DETECTED,
        risk_score=0.75,
        natural_recovery_probability=0.30,
        assisted_recovery_probability=0.65,
        expected_incremental_revenue=8250.0,
        recommended_action=ActionType.REMINDER,
        policy_status=PolicyStatus.ELIGIBLE
    )
    assert opp_create.recommended_action == ActionType.REMINDER

    opp_orm = RecoveryOpportunity(
        merchant_id=opp_create.merchant_id,
        customer_id=opp_create.customer_id,
        source_type=opp_create.source_type,
        source_reference_id=opp_create.source_reference_id,
        amount_at_risk=opp_create.amount_at_risk,
        currency=opp_create.currency,
        detected_at=opp_create.detected_at,
        status=opp_create.status.value,
        risk_score=opp_create.risk_score,
        natural_recovery_probability=opp_create.natural_recovery_probability,
        assisted_recovery_probability=opp_create.assisted_recovery_probability,
        expected_incremental_revenue=opp_create.expected_incremental_revenue,
        recommended_action=opp_create.recommended_action.value,
        policy_status=opp_create.policy_status.value
    )
    assert opp_orm.amount_at_risk == 25000.0
    assert opp_orm.recommended_action == "REMINDER"
