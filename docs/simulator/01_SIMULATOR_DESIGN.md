# RecoverAI Simulator — Controlled Recovery Simulator Design

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Controlled Simulation Architecture

The RecoverAI Recovery Simulator executes deterministic time-step simulations for B2B invoice recovery opportunities over a 30-day timeline.

### Integrated Pipeline Structure

```text
Recovery Opportunity State (S0)
        ↓
ML Natural Recovery P(R | X, A=0)
        ↓
Treatment Estimator P(R | X, A=k) [CONFIGURED / SIMULATED]
        ↓
Economic Engine: Delta E = Amount * Delta p - Cost
        ↓
Policy Engine: Cooldown (24h), Retries (3), Opt-Out, Disputes
        ↓
Decision Engine: Action Selection (Max Delta E Eligible Action)
        ↓
Stochastic Recovery Resolution & Time Step (+1 Day)
        ↓
AuditEvent Trail Persisted
```

---

## 2. Distinction of Evidence Types

- **`EMPIRICAL`**: Ground-truth invoice amounts, payment terms, and due dates extracted from `Customer Invoices Dataset.csv`.
- **`OBSERVATION`**: Natural recovery probability baseline $P(R \mid X, A=0)$ derived from historical settlement patterns.
- **`SIMULATED`**: Action-conditioned probability uplift $P(R \mid X, A=k)$ and stochastic daily clearing events.
- **`ASSUMPTIONS`**: Configurable action cost matrix (₹0.50 REMINDER, ₹2.00 RETRY, ₹50.00 ESCALATE) and 24h cooldown windows.
