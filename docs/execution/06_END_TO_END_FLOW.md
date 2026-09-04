# RecoverAI Execution Engine — End-to-End Execution Flow

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Complete Integration Workflow

```text
POST /api/v1/opportunities/{id}/evaluate
        ↓ (Recommended Action Returned)
POST /api/v1/opportunities/{id}/execute
        ↓ (Policy Revalidated)
RazorpayTestModeProvider (TEST_MODE Invoked)
        ↓ (Execution Result Returned)
ExecutionResultProcessor (InterventionEvent & RecoveryOutcome Created)
        ↓ (AuditEvent & Timeline Event Recorded)
GET /api/v1/opportunities/{id}/timeline
```

---

## 2. End-to-End Demo Benchmark (INR 80,000 Overdue Invoice)

1. **Invoice Exposure**: INR 80,000.00 overdue invoice.
2. **Evaluation**: $P_{	ext{nat}} = 0.25$, Recommended Action = `REMINDER` / `RETRY`.
3. **Execution**: Bounded execution succeeded via `RazorpayTestModeProvider` (Ref `PAYOUT_TEST_XXXX`).
4. **Outcome**: Test-Mode Executed Recovery recorded with Net Value = **INR 79,998.00** (Cost = INR 2.00).
