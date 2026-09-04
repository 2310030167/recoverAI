# RecoverAI Execution Engine — Deterministic Failure Handling

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Failure Categories & Codes

- `EXECUTION_POLICY_BLOCKED`: Action rejected by pre-execution validator.
- `GATEWAY_TEMPORARY_DOWN`: Temporary gateway connection failure.
- `CARD_EXPIRED_PERMANENT`: Customer card permanently invalidated.
- `PROVIDER_TIMEOUT`: Gateway response timed out.

---

## 2. Failure Recovery & Policy Flow

When an action execution fails:
1. Failure code and reason are persisted in the execution record.
2. An audit event is recorded in the timeline.
3. The policy engine is re-evaluated for future steps; the engine **does NOT retry indefinitely**.
