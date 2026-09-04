# RecoverAI Simulator — Methodological & Causal Limitations

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Classification of Evidence Sources

| Component | Classification | Description |
|---|---|---|
| **Invoice Exposure & Due Dates** | `EMPIRICAL` | Extracted directly from `Customer Invoices Dataset.csv` |
| **Natural Recovery $P(R \mid X, A=0)$** | `OBSERVATIONAL` | Calibrated against historical settlement deciles |
| **Intervention Multipliers** | `CONFIGURED` | Multiplier bounds (REMINDER 1.20x, RETRY 1.35x, ESCALATE 1.15x) |
| **Recovery Outcomes** | `SIMULATED` | Stochastic timeline progression under Common Random Numbers |

---

## 2. Strict Causal Inference Boundary

All reported gains represent **Simulated Net Incremental Revenue**, not proven real-world causal uplift. Randomized A/B trial logs from live merchant deployments are required before making causal claims.
