import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="merchant", cascade="all, delete-orphan")
    opportunities: Mapped[List["RecoveryOpportunity"]] = relationship("RecoveryOpportunity", back_populates="merchant", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), index=True, nullable=False)
    external_customer_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    segment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tenure_months: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    account_health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    paperless_billing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_historical_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="customers")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    opportunities: Mapped[List["RecoveryOpportunity"]] = relationship("RecoveryOpportunity", back_populates="customer", cascade="all, delete-orphan")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), index=True, nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    clear_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # LEAKAGE TARGET
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True, nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    days_late: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_to_pay: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="invoices")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="invoices")
    payment_attempts: Mapped[List["PaymentAttempt"]] = relationship("PaymentAttempt", back_populates="invoice")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), index=True, nullable=False)
    invoice_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("invoices.id"), index=True, nullable=True)
    transaction_reference: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sender_bank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receiver_bank: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    invoice: Mapped[Optional["Invoice"]] = relationship("Invoice", back_populates="payment_attempts")


class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), index=True, nullable=False)
    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id"), index=True, nullable=True)
    session_reference: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    administrative_duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    informational_duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    product_related_duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bounce_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    exit_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    page_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    special_day: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    visitor_type: Mapped[str] = mapped_column(String(50), default="Returning_Visitor", nullable=False)
    weekend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revenue_converted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # Target label
    session_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RecoveryOpportunity(Base):
    __tablename__ = "recovery_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # e.g. INVOICE, PAYMENT_FAILURE, CHECKOUT
    source_reference_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    amount_at_risk: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DETECTED", index=True, nullable=False)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    natural_recovery_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assisted_recovery_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_incremental_revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    policy_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="opportunities")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="opportunities")
    interventions: Mapped[List["InterventionEvent"]] = relationship("InterventionEvent", back_populates="opportunity", cascade="all, delete-orphan")
    outcomes: Mapped[List["RecoveryOutcome"]] = relationship("RecoveryOutcome", back_populates="opportunity", cascade="all, delete-orphan")


class InterventionEvent(Base):
    __tablename__ = "intervention_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("recovery_opportunities.id"), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    expected_value: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    policy_decision: Mapped[str] = mapped_column(String(50), default="APPROVED", nullable=False)
    execution_status: Mapped[str] = mapped_column(String(50), default="EXECUTED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    opportunity: Mapped["RecoveryOpportunity"] = relationship("RecoveryOpportunity", back_populates="interventions")


class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("recovery_opportunities.id"), index=True, nullable=False)
    intervention_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("intervention_events.id"), index=True, nullable=True)
    is_recovered: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recovered_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recovery_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome_type: Mapped[str] = mapped_column(String(50), default="UNRECOVERED", nullable=False)
    days_to_recovery: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    opportunity: Mapped["RecoveryOpportunity"] = relationship("RecoveryOpportunity", back_populates="outcomes")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("recovery_opportunities.id"), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    actor: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
