# RecoverAI Execution Engine — Idempotency Guarantees

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Idempotency Key Design

Every execution request uses a deterministic idempotency key:
`IDEM_{SHA256(opportunity_id:action:attempt_number)}` or client-provided `idempotency_key`.

---

## 2. Duplicate Request Handling

If the exact same execution request is submitted multiple times:
1. `IdempotencyStore` detects the existing key cache.
2. Returns the stored `ExecutionRecordSchema` with `is_idempotent_replay = True`.
3. Prevents duplicate provider executions or double-billing of intervention costs.
