# RecoverAI ML — Treatment & Assisted Recovery Estimation

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Observational Data Limitations

The raw empirical datasets represent standard merchant collection records without multi-arm randomized A/B trial logs (`A=REMINDER` vs `A=RETRY` vs `A=NO_ACTION`).

---

## 2. Honest Causal Architecture

We do **NOT** manufacture fake uplift numbers or claim unproven causal identification from observational data. `AssistedRecoveryEstimator` defines the formal action interface $P(R \mid X, A=k)$ and bounded action multipliers, allowing the Phase 4 Recovery Simulator engine to supply verified treatment effects.
