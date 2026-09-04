"""initial_canonical_schema

Revision ID: 001_initial_canonical_schema
Revises: 
Create Date: 2026-08-23 20:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_canonical_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Merchants table
    op.create_table(
        'merchants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_merchants_merchant_code'), 'merchants', ['merchant_code'], unique=True)

    # 2. Customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), nullable=False),
        sa.Column('external_customer_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('segment', sa.String(length=50), nullable=True),
        sa.Column('tenure_months', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('account_health_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('paperless_billing', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('total_historical_revenue', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_external_customer_id'), 'customers', ['external_customer_id'], unique=False)
    op.create_index(op.f('ix_customers_merchant_id'), 'customers', ['merchant_id'], unique=False)

    # 3. Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('clear_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='OPEN'),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_disputed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('payment_terms', sa.String(length=50), nullable=True),
        sa.Column('days_late', sa.Integer(), nullable=True),
        sa.Column('days_to_pay', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_customer_id'), 'invoices', ['customer_id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=False)
    op.create_index(op.f('ix_invoices_merchant_id'), 'invoices', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_invoices_status'), 'invoices', ['status'], unique=False)

    # 4. Payment Attempts table
    op.create_table(
        'payment_attempts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('invoice_id', sa.String(length=36), nullable=True),
        sa.Column('transaction_reference', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('sender_bank', sa.String(length=100), nullable=True),
        sa.Column('receiver_bank', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_attempts_customer_id'), 'payment_attempts', ['customer_id'], unique=False)
    op.create_index(op.f('ix_payment_attempts_invoice_id'), 'payment_attempts', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_payment_attempts_merchant_id'), 'payment_attempts', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_payment_attempts_status'), 'payment_attempts', ['status'], unique=False)

    # 5. Checkout Sessions table
    op.create_table(
        'checkout_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=True),
        sa.Column('session_reference', sa.String(length=100), nullable=False),
        sa.Column('administrative_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('informational_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('product_related_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('bounce_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('exit_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('page_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('special_day', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('visitor_type', sa.String(length=50), nullable=False, server_default='Returning_Visitor'),
        sa.Column('weekend', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revenue_converted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('session_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkout_sessions_customer_id'), 'checkout_sessions', ['customer_id'], unique=False)
    op.create_index(op.f('ix_checkout_sessions_merchant_id'), 'checkout_sessions', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_checkout_sessions_session_reference'), 'checkout_sessions', ['session_reference'], unique=False)

    # 6. Recovery Opportunities table
    op.create_table(
        'recovery_opportunities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_reference_id', sa.String(length=100), nullable=False),
        sa.Column('amount_at_risk', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DETECTED'),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('natural_recovery_probability', sa.Float(), nullable=True),
        sa.Column('assisted_recovery_probability', sa.Float(), nullable=True),
        sa.Column('expected_incremental_revenue', sa.Float(), nullable=True),
        sa.Column('recommended_action', sa.String(length=50), nullable=True),
        sa.Column('policy_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recovery_opportunities_customer_id'), 'recovery_opportunities', ['customer_id'], unique=False)
    op.create_index(op.f('ix_recovery_opportunities_merchant_id'), 'recovery_opportunities', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_recovery_opportunities_source_reference_id'), 'recovery_opportunities', ['source_reference_id'], unique=False)
    op.create_index(op.f('ix_recovery_opportunities_source_type'), 'recovery_opportunities', ['source_type'], unique=False)
    op.create_index(op.f('ix_recovery_opportunities_status'), 'recovery_opportunities', ['status'], unique=False)

    # 7. Intervention Events table
    op.create_table(
        'intervention_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('opportunity_id', sa.String(length=36), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('expected_value', sa.Float(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('policy_decision', sa.String(length=50), nullable=False, server_default='APPROVED'),
        sa.Column('execution_status', sa.String(length=50), nullable=False, server_default='EXECUTED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['recovery_opportunities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intervention_events_action'), 'intervention_events', ['action'], unique=False)
    op.create_index(op.f('ix_intervention_events_opportunity_id'), 'intervention_events', ['opportunity_id'], unique=False)

    # 8. Recovery Outcomes table
    op.create_table(
        'recovery_outcomes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('opportunity_id', sa.String(length=36), nullable=False),
        sa.Column('intervention_id', sa.String(length=36), nullable=True),
        sa.Column('is_recovered', sa.Boolean(), nullable=False),
        sa.Column('recovered_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recovery_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('outcome_type', sa.String(length=50), nullable=False, server_default='UNRECOVERED'),
        sa.Column('days_to_recovery', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['intervention_id'], ['intervention_events.id'], ),
        sa.ForeignKeyConstraint(['opportunity_id'], ['recovery_opportunities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recovery_outcomes_intervention_id'), 'recovery_outcomes', ['intervention_id'], unique=False)
    op.create_index(op.f('ix_recovery_outcomes_opportunity_id'), 'recovery_outcomes', ['opportunity_id'], unique=False)

    # 9. Audit Events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('opportunity_id', sa.String(length=36), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False, server_default='SYSTEM'),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['recovery_opportunities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_event_type'), 'audit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_events_opportunity_id'), 'audit_events', ['opportunity_id'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('recovery_outcomes')
    op.drop_table('intervention_events')
    op.drop_table('recovery_opportunities')
    op.drop_table('checkout_sessions')
    op.drop_table('payment_attempts')
    op.drop_table('invoices')
    op.drop_table('customers')
    op.drop_table('merchants')
