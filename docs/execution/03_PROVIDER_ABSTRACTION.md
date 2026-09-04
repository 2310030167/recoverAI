# RecoverAI Execution Engine — Razorpay Test-Mode Provider Abstraction

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Provider Design & Safety

To guarantee safety during buildathon demonstration:
- **Provider Identifier**: `provider = ProviderType.TEST_MODE`
- **Zero Real Money Movement**: Never executes real financial transactions.
- **Pathway Abstraction**:
  - `REMINDER`: Notification Provider abstraction
  - `RETRY`: Payment Gateway Retry Provider abstraction
  - `ESCALATE`: Operations Agent Escalation Provider abstraction
  - `NO_ACTION`: Created as skipped execution record

---

## 2. Deterministic Scenario Simulation

`RazorpayTestModeProvider` supports deterministic scenario simulation:
- `SUCCESS`: Returns `SUCCEEDED` status with provider reference `PAYOUT_TEST_XXXX`.
- `TEMPORARY_FAILURE`: Returns `FAILED` status with code `GATEWAY_TEMPORARY_DOWN`.
- `PERMANENT_FAILURE`: Returns `FAILED` status with code `CARD_EXPIRED_PERMANENT`.
- `TIMEOUT`: Returns `FAILED` status with code `PROVIDER_TIMEOUT`.
