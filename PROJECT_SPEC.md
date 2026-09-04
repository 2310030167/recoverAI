# RecoverAI — Master Project Specification

> Razorpay AI Buildathon — Track 03: AI Revenue Recovery
>
> This document is the single source of truth for the RecoverAI project.
> All implementation decisions, architecture, ML design, evaluation,
> safety constraints, and MVP scope must follow this specification.

---

# 1. Project Identity

## Project Name

RecoverAI

## Competition

Razorpay AI Buildathon

## Track

Track 03 — AI Revenue Recovery

## Submission Target

September 3, 2026

## Objective

Build a working AI-powered revenue recovery system that:

1. Detects revenue at risk.
2. Diagnoses the likely cause.
3. Predicts recovery probability.
4. Determines whether intervention is economically worthwhile.
5. Selects a bounded recovery action.
6. Executes the action through a controlled workflow.
7. Stops when recovery should no longer be attempted.
8. Maintains a complete audit trail.
9. Measures recovered revenue across a batch.

---

# 2. Track Alignment

RecoverAI must directly satisfy the Razorpay Track 03 requirement:

> Find revenue that is slipping away and win it back.

The system must demonstrate:

Detection
→ Diagnosis
→ Prediction
→ Intervention Decision
→ Bounded Execution
→ Stopping Rules
→ Measurement

The system must NOT merely be a dashboard or prediction model.

The final MVP must demonstrate an end-to-end recovery loop.

---

# 3. Core Problem

Revenue can be lost through multiple mechanisms:

- payment failure
- repeated payment degradation
- checkout abandonment
- failed subscription payment
- overdue invoice
- delayed receivable
- customer inactivity preceding a revenue event

The MVP will focus primarily on:

## Primary Recovery Scenario

Payment / invoice revenue at risk → diagnosis → recovery intervention → measured recovery.

Receivables will be the strongest empirical domain because the available datasets contain explicit invoice, due-date, settlement and delinquency information.

Checkout and payment-failure behavior will provide secondary scenarios.

---

# 4. Core Product

RecoverAI is an economically bounded AI recovery decision engine.

It should answer:

> "This customer/invoice/payment is at risk. What should we do, if anything, and is the expected incremental revenue worth the intervention?"

The system must be able to choose:

- NO_ACTION
- REMINDER
- RETRY
- ESCALATE

Optional actions such as discount or payment-link recovery must only be implemented if time permits and the economics are properly modeled.

---

# 5. System Philosophy

The ML model does NOT directly execute financial actions.

Architecture:

Customer / Payment Event
        ↓
Feature Engineering
        ↓
Risk / Recovery Prediction
        ↓
Treatment / Uplift Estimation
        ↓
Economic Evaluation
        ↓
Policy / Guardrail Engine
        ↓
Action Selection
        ↓
Bounded Executor
        ↓
Outcome
        ↓
Audit + Measurement

---

# 6. ML Responsibilities

ML is responsible for estimating:

## 6.1 Recovery Probability

Estimate:

P(R | X, A)

Where:

R = recovery within the defined recovery window

X = customer/payment/invoice state

A = proposed intervention

---

## 6.2 Natural Recovery

Estimate:

P(R | X, A=0)

This represents the probability that the revenue would be recovered without intervention.

This value is critical because an intervention that recovers money that would have been recovered naturally is not necessarily incremental recovery.

---

## 6.3 Incremental Recovery

For an action A:

Uplift(A) =
P(R | X,A) - P(R | X,0)

This represents estimated incremental recovery probability.

---

# 7. Economic Decision Engine

The system must not optimize probability alone.

For an opportunity with amount:

A

and intervention cost:

C(A)

the system calculates expected incremental value.

Primary formulation:

Expected Incremental Revenue:

ΔE(Rev,A)
=
A × [P(R|X,A) - P(R|X,0)]
-
C(A)

The intervention is eligible only when:

ΔE(Rev,A) > 0

subject to policy constraints.

---

# 8. Economic Factors

The decision engine must consider:

- transaction amount
- recovery probability
- natural recovery probability
- incremental recovery probability
- intervention cost
- number of previous interventions
- customer friction
- time since failure
- overdue duration
- customer value
- recovery window
- action-specific success probability

Possible intervention costs:

REMINDER
→ communication cost

RETRY
→ payment/retry cost where applicable

ESCALATE
→ operational cost

DISCOUNT
→ direct revenue reduction

Costs must be configurable.

Do NOT hard-code external pricing as factual Razorpay pricing unless verified.

---

# 9. Recovery Actions

## NO_ACTION

Use when:

- natural recovery probability is sufficiently high
- incremental value is negative
- customer is protected by a cooldown
- maximum attempts reached
- recovery window expired

---

## REMINDER

Used for eligible overdue or failed-payment cases.

Must include:

- timing
- reason
- attempt number
- expected benefit
- stopping condition

---

## RETRY

Used for eligible payment failures where retry is economically justified.

Must have:

- retry eligibility
- retry count
- cooldown
- stopping condition

---

## ESCALATE

Used when automated recovery should stop.

Examples:

- high-value overdue account
- repeated failed recovery
- dispute
- policy exception
- customer explicitly requests assistance

---

# 10. Customer State

The system may maintain a customer state representation.

Example:

NEW
ACTIVE
LOYAL
AT_RISK
RECOVERY_ACTIVE
RECOVERED
ESCALATED
LOST

Customer state must be derived from observable historical behavior.

Do not use arbitrary labels merely for presentation.

---

# 11. Core Features

Features should be generated point-in-time.

Potential features:

## Customer

- customer tenure
- transaction count
- previous successful payments
- previous failed payments
- average transaction amount
- total historical revenue
- recency
- frequency
- monetary value
- previous recovery outcomes

## Payment

- failure count
- time since failure
- payment amount
- payment method
- retry count
- recent success/failure ratio

## Invoice

- invoice amount
- days overdue
- payment terms
- dispute status
- customer history
- historical settlement time
- historical late-payment behavior

## Checkout

- session duration
- bounce rate
- exit rate
- page value
- number of pages viewed
- visitor type
- abandonment signal

---

# 12. Point-in-Time Data Rule

No future information may be used to construct features.

For any decision timestamp T:

Only information available at or before T may be used.

Future outcome fields must never enter model features.

Examples of dangerous fields:

- clear_date
- settled_date
- final payment outcome
- future churn
- future recovery result

These can be used for labels/evaluation but not as features.

---

# 13. Dataset Strategy

The audited data contains:

- 10 datasets
- approximately 9.22 million records
- approximately 2.88 GB of data

The audit classified the following as CORE:

1. Customer Invoices Dataset.csv
2. WA_Fn-UseC_-Accounts-Receivable.csv
3. customer_churn_business_dataset.csv
4. online_shoppers_intention.csv

The UPI dataset is secondary/simulator data.

Online Retail and Online Retail II are secondary transaction-history datasets.

Synthetic churn datasets are optional.

Synthetic fraud data is excluded.

---

# 14. Primary Dataset Roles

## Accounts Receivable

WA_Fn-UseC_-Accounts-Receivable.csv

Purpose:

- overdue behavior
- invoice amount
- settlement time
- dispute behavior
- customer payment behavior

Important fields include:

- customerID
- InvoiceDate
- DueDate
- InvoiceAmount
- Disputed
- SettledDate
- DaysToSettle
- DaysLate

---

## Customer Invoices

Customer Invoices Dataset.csv

Purpose:

- invoice state
- open amount
- customer behavior
- payment terms
- clearing behavior

Important fields include:

- cust_number
- posting_date
- clear_date
- total_open_amount
- cust_payment_terms
- invoice_id
- isOpen

Missing clear_date must be treated carefully because it may represent unresolved/open invoices.

---

## Business Customer Dataset

customer_churn_business_dataset.csv

Purpose:

- customer health
- payment failures
- revenue exposure
- lifecycle context

Useful fields include:

- customer_id
- customer_segment
- tenure_months
- monthly_fee
- total_revenue
- payment_failures
- last_login_days_ago
- account health-related variables
- churn

This dataset does not contain native event timestamps, therefore it must NOT be treated as a direct temporal event stream without explicit assumptions.

---

## Online Shoppers

online_shoppers_intention.csv

Purpose:

- checkout abandonment behavior
- session-level intent
- browsing friction

Useful for the checkout-recovery secondary scenario.

---

# 15. Secondary Data

## UPI_transactions.csv

Synthetic dataset.

Use only as:

- simulator input
- payment-failure behavior source
- Indian payment context

Do NOT present it as real production payment data.

---

## Online Retail

Use for:

- RFM features
- repeat purchase behavior
- customer value
- transaction history

---

## Online Retail II

Use for:

- longer transaction history
- customer purchase frequency
- monetary value
- temporal behavior

---

# 16. Excluded Data

synthetic_fraud_data.csv

Do not use as a core RecoverAI model.

Reason:

Track 03 is revenue recovery, not fraud detection.

The dataset is also synthetic and focused on fraud/security behavior.

---

# 17. Data Engineering Pipeline

Raw data:

data/raw/

        ↓

Validation

        ↓

Cleaning

        ↓

Canonical schemas

        ↓

Feature engineering

        ↓

Point-in-time feature tables

        ↓

Training / validation / test datasets

        ↓

Model training

        ↓

Model registry/artifacts

---

# 18. Canonical Entities

The backend should support these core entities:

Merchant
Customer
Invoice
PaymentAttempt
CheckoutSession
InterventionEvent
RecoveryOpportunity
RecoveryOutcome
ModelPrediction
Decision
AuditEvent

---

# 19. RecoveryOpportunity

Every recovery opportunity should contain approximately:

- opportunity_id
- customer_id
- merchant_id
- source_type
- source_reference
- amount
- detected_at
- state
- risk_score
- natural_recovery_probability
- assisted_recovery_probability
- expected_incremental_revenue
- recommended_action
- policy_status

---

# 20. InterventionEvent

Each intervention must record:

- intervention_id
- opportunity_id
- action
- timestamp
- reason
- expected_value
- cost
- attempt_number
- policy decision
- execution status

---

# 21. Audit Trail

Every decision must be explainable.

Example:

Opportunity:
INV-1234

Amount:
₹12,500

Detected:
Payment overdue by 6 days

Natural recovery:
0.31

Reminder recovery:
0.52

Incremental probability:
0.21

Estimated intervention cost:
₹0.50

Expected incremental value:
₹2,624.50

Decision:
REMINDER

Reason:
Positive expected incremental revenue and policy eligibility.

---

# 22. Policy Engine

Policy must be deterministic and separate from ML.

Example constraints:

- maximum retry count
- cooldown period
- maximum intervention count
- recovery window
- minimum economic value
- disputed invoice protection
- customer opt-out
- escalation threshold

The ML model proposes probabilities.

The policy engine determines whether the action is allowed.

---

# 23. Stopping Rules

Recovery must stop when:

1. Payment recovered.
2. Maximum attempts reached.
3. Recovery window expired.
4. Expected incremental value becomes non-positive.
5. Customer opts out.
6. Dispute is detected.
7. Manual escalation is required.

---

# 24. Model Architecture

The MVP should prioritize reliable tabular ML over unnecessary deep learning.

Candidate models:

1. Logistic Regression
2. Random Forest
3. XGBoost / LightGBM if available
4. Survival model for time-to-recovery

Model selection must be empirical.

Do not use a complex model simply to make the project look advanced.

---

# 25. Model Outputs

For each recovery opportunity:

risk_probability
natural_recovery_probability
action_recovery_probability
incremental_recovery_probability
expected_revenue_gain
recommended_action
confidence
explanation

---

# 26. Uplift / Treatment Modeling

Where sufficient intervention/outcome data exists:

estimate treatment effect.

Possible approaches:

- T-Learner
- S-Learner
- propensity-weighted models
- causal forests if justified

The MVP should use the simplest method that can be validated honestly.

Do not claim causal uplift from purely observational data without clearly documenting assumptions.

---

# 27. Natural Recovery Problem

Natural recovery is the critical counterfactual.

The system must NOT simply assume:

P(R|X,0)

from an arbitrary value.

Possible estimation strategies:

1. Observational no-intervention cases.
2. Historical recovery patterns.
3. Temporal cohorts.
4. Simulator-generated controlled interventions.
5. Sensitivity analysis.

If true treatment/control data is unavailable, the limitation must be explicitly reported.

---

# 28. Triple Barrier Framework

A Triple Barrier-style outcome framework may be used for defining recovery outcomes.

For an opportunity:

Upper barrier:
RECOVERED

Lower barrier:
LOST / OPPORTUNITY EXPIRED

Vertical barrier:
RECOVERY WINDOW EXPIRED

Example:

Detection:
T0

Recovery window:
6 hours / 24 hours / 72 hours depending on scenario

Outcome:

RECOVERED
or
NOT_RECOVERED
or
EXPIRED

Triple Barrier must be treated as an outcome-labeling framework, not automatically as the complete recovery strategy.

---

# 29. Evaluation

The evaluation must compare:

## Baseline

Traditional rule-based recovery.

Example:

IF invoice overdue > X days
THEN reminder

versus:

## RecoverAI

ML
→ economics
→ policy
→ action

---

# 30. Required Metrics

## Model

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Calibration

## Recovery

- recovery rate
- incremental recovery
- recovered revenue
- net recovered revenue
- intervention rate
- no-action rate
- recovery per intervention

## Economics

- gross recovered revenue
- intervention cost
- net recovered revenue
- expected incremental revenue
- ROI

## Safety

- policy violations
- excessive interventions
- retry-limit violations
- incorrect escalation
- audit completeness

---

# 31. Batch Evaluation

The system must evaluate a complete held-out batch.

Do not demonstrate success using only hand-picked examples.

Report:

Total opportunities
Total revenue at risk
Baseline recovered revenue
RecoverAI recovered revenue
Intervention cost
Net recovered revenue
Incremental revenue
Recovery rate
Action distribution

---

# 32. Baseline System

Implement a deterministic baseline.

Example:

IF days_overdue >= threshold
AND amount >= minimum
THEN REMINDER

Otherwise:

NO_ACTION

This provides a transparent benchmark.

---

# 33. RecoverAI Decision

For each candidate action:

Calculate:

P_assisted
P_natural
Incremental probability
Intervention cost
Expected incremental revenue

Then apply policy.

Conceptually:

FOR each opportunity:

    generate candidate actions

    estimate recovery probability

    estimate natural recovery

    calculate incremental value

    remove policy-ineligible actions

    choose highest positive expected value action

    otherwise choose NO_ACTION

---

# 34. Simulation

A controlled recovery simulator will be used to demonstrate end-to-end execution where real intervention outcomes are unavailable.

The simulator must:

- generate recovery outcomes
- model action-specific probabilities
- model natural recovery
- enforce intervention cooldown
- enforce stopping rules
- record outcomes
- calculate recovered revenue

Simulator assumptions must be documented.

Synthetic simulation results must NEVER be presented as real-world observed results.

---

# 35. Backend Architecture

Use a modular monolith.

Technology:

Python
FastAPI
PostgreSQL
Redis
SQLAlchemy
Alembic
Pydantic

Current backend foundation already exists.

Do not replace the existing backend architecture without a documented reason.

---

# 36. Backend Modules

backend/app/

core/
api/
models/
schemas/
services/
repositories/
utils/

Future services:

recovery/
prediction/
economics/
policy/
intervention/
audit/
simulation/

---

# 37. API Architecture

Version APIs:

/api/v1/

Example endpoints:

GET /api/v1/health

GET /api/v1/opportunities

GET /api/v1/opportunities/{id}

POST /api/v1/opportunities/{id}/evaluate

POST /api/v1/opportunities/{id}/execute

GET /api/v1/opportunities/{id}/audit

GET /api/v1/metrics

POST /api/v1/simulation/run

---

# 38. Frontend

The frontend should demonstrate the system, not become a separate product.

Primary screens:

1. Recovery Dashboard
2. Opportunity List
3. Opportunity Detail
4. Decision Explanation
5. Intervention Timeline
6. Batch Evaluation
7. Model / Economics Metrics

---

# 39. Opportunity Dashboard

Show:

- total revenue at risk
- opportunities
- recommended interventions
- recovered revenue
- incremental recovered revenue
- intervention cost
- net recovery
- recovery rate

---

# 40. Opportunity Detail

Show:

Customer
Amount
Problem
Risk
Natural recovery probability
Assisted recovery probability
Expected value
Recommended action
Policy decision
Audit trail
Recovery outcome

---

# 41. Razorpay Integration

The MVP should use Razorpay Test Mode where feasible.

Production money movement is NOT required.

Integration objective:

Razorpay test event
→ RecoverAI receives event
→ detects opportunity
→ evaluates
→ applies policy
→ executes bounded test action
→ records result

External integration must never bypass the policy engine.

---

# 42. Webhook Architecture

Expected pattern:

Razorpay/Test Event
        ↓
Webhook endpoint
        ↓
Event validation
        ↓
Opportunity creation/update
        ↓
Feature generation
        ↓
Prediction
        ↓
Economic evaluation
        ↓
Policy
        ↓
Action

---

# 43. Failure Handling

The system must demonstrate at least one graceful failure.

Example:

Payment retry fails.

System:

1. records failed attempt
2. increments retry count
3. recalculates opportunity
4. checks policy
5. stops further retry if threshold reached
6. escalates or marks recovery exhausted

The system must never blindly retry indefinitely.

---

# 44. Explainability

Every action must answer:

WHY?

Example:

"REMINDER selected because the customer has a high probability of assisted recovery, natural recovery probability is low, expected incremental revenue is positive, and the customer is within the intervention policy limits."

---

# 45. Data Leakage Requirements

Never allow future information into prediction features.

Strictly separate:

FEATURES

from:

OUTCOMES

from:

FUTURE EVENTS

Any questionable field must be documented as:

SAFE
CAUTION
LEAKAGE_RISK

---

# 46. Testing Strategy

Testing layers:

## Unit Tests

- economics calculations
- policy rules
- feature transformations
- action selection

## Integration Tests

- API
- PostgreSQL
- Redis
- recovery workflow

## ML Tests

- schema validation
- feature leakage
- model prediction shape
- calibration
- threshold behavior

## End-to-End

Opportunity
→ prediction
→ economics
→ policy
→ action
→ outcome
→ audit

---

# 47. Security / Safety

No offensive fraud functionality.

No unrestricted financial actions.

No production money movement.

All external actions must pass policy.

All actions must be logged.

Sensitive information must not be unnecessarily exposed in logs.

---

# 48. MVP Definition

The MVP is COMPLETE only when the following works end-to-end:

1. Load real historical data.
2. Generate point-in-time features.
3. Train a validated recovery-related model.
4. Generate recovery probabilities.
5. Estimate natural recovery.
6. Evaluate candidate interventions economically.
7. Apply policy constraints.
8. Select an action.
9. Execute a bounded simulated/test action.
10. Record the action.
11. Produce an outcome.
12. Calculate recovered revenue.
13. Compare against a rule-based baseline.
14. Display results in the dashboard.
15. Show complete audit trail.

---

# 49. Explicit Non-Goals

Do NOT build:

- generic chatbot
- generic AI assistant
- fraud detection platform
- unlimited multi-agent architecture
- reinforcement learning
- unnecessary microservices
- production payment processing
- unrestricted automated financial actions
- fake customer outcomes
- fabricated benchmark results
- unnecessary LLM features

---

# 50. Engineering Priority

Priority order:

P0 — End-to-end Track 03 functionality

P1 — Correct economics

P1 — Reliable ML

P1 — Evaluation

P1 — Auditability

P2 — Razorpay Test Mode integration

P2 — Dashboard

P3 — Advanced ML

P3 — UI polish

Never sacrifice P0/P1 for P3.

---

# 51. Definition of Success

RecoverAI succeeds if a reviewer can give it a batch of revenue-at-risk cases and clearly see:

1. What revenue is at risk?
2. Why is it at risk?
3. What does the model predict?
4. What would probably happen without intervention?
5. Which action is recommended?
6. Why is that action economically justified?
7. What policy limits apply?
8. What happened after the action?
9. How much money was recovered?
10. How does this compare with a traditional rule-based approach?

---

# 52. Golden Architecture

The final architecture should follow:

DATA
 ↓
POINT-IN-TIME FEATURES
 ↓
ML PREDICTION
 ↓
RECOVERY / UPLIFT ESTIMATION
 ↓
ECONOMIC ENGINE
 ↓
POLICY ENGINE
 ↓
ACTION SELECTOR
 ↓
BOUNDED EXECUTOR
 ↓
OUTCOME
 ↓
AUDIT
 ↓
BATCH EVALUATION

This is the core RecoverAI architecture.

---

# 53. Current Project State

Data audit:
COMPLETE

Backend foundation:
COMPLETE

ML:
NOT STARTED

Feature pipeline:
NOT STARTED

Database models:
NOT STARTED

Economics engine:
NOT STARTED

Policy engine:
NOT STARTED

Recovery simulator:
NOT STARTED

Razorpay integration:
NOT STARTED

Frontend:
NOT STARTED

Evaluation:
NOT STARTED

---

# 54. Immediate Next Step

Build the canonical data layer and database models.

Do NOT start frontend.

Do NOT start Razorpay integration.

Do NOT build advanced ML yet.

First establish:

Raw
→ Clean
→ Canonical
→ Feature-ready

and:

Merchant
Customer
Invoice
PaymentAttempt
RecoveryOpportunity
InterventionEvent
RecoveryOutcome
AuditEvent

---

# 55. Agent Rule

This specification is authoritative.

If an implementation decision conflicts with this document:

STOP.

Explain the conflict.

Do not silently change architecture.

Do not invent requirements.

Do not fabricate data.

Do not fabricate metrics.

Do not claim completion without executing tests.

Every major implementation step must produce:

IMPLEMENTED
TESTED
FAILED
CHANGED
NEXT STEP
