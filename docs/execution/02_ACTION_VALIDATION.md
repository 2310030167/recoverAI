# RecoverAI Execution Engine — Action Validation & Safety Rules

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Independent Pre-Execution Checks

Before any action is sent to the execution provider, `ActionValidator` verifies:

1. **Opportunity Active**: Opportunity has not been previously recovered or expired past 30 days.
2. **Action Support**: Action is one of `NO_ACTION`, `REMINDER`, `RETRY`, `ESCALATE`.
3. **Policy Rules**:
   - `is_disputed == False` (Disputed invoices block automated actions)
   - `is_opted_out == False` (Opted-out customers block communication)
   - Cooldown $\ge 24	ext{h}$ since last intervention
   - Retries $\le 3$ and Total Interventions $\le 5$
4. **Economic Value Check**: Expected incremental value $\Delta E > 0.00$.

If any check fails, execution is immediately **BLOCKED** (`execution_status = BLOCKED`) with explicit blocking reasons recorded.
