# RecoverAI Execution Engine — Architecture & Control Flow

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Architectural Separation

The Bounded Recovery Execution Engine enforces strict architectural separation between **DECISION** and **EXECUTION**:

```text
Opportunity State (S0)
        ↓
ML Natural Recovery P(R | X, A=0)
        ↓
Economic Engine: Delta E = Amount * Delta p - Cost
        ↓
Policy Engine: Cooldown (24h), Retries (3), Opt-Out, Disputes
        ↓
DecisionEngine (Determines WHAT action should be selected)
        ↓
ActionValidator (Independently revalidates BEFORE execution)
        ↓
BoundedRecoveryExecutionEngine (Determines WHETHER & HOW action is executed)
        ↓
RazorpayTestModeProvider (Executes via TEST_MODE pathway)
        ↓
ResultProcessor (Generates InterventionEvent, AuditEvent & RecoveryOutcome)
```

**Key Guarantee**: The execution engine **NEVER** bypasses the `PolicyEngine`.

---

## 2. Execution Engine Modules

- `app.services.execution.executor`: Orchestrates target workflow and manages execution records.
- `app.services.execution.action_validator`: Pre-execution validation safety check.
- `app.services.execution.provider`: Provider abstraction (`TEST_MODE` pathway).
- `app.services.execution.idempotency`: Idempotency key generation & cache store.
- `app.services.execution.result_processor`: Timeline events, audit logs, and recovery outcomes.
