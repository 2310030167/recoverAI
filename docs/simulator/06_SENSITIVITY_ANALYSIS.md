# RecoverAI Simulator — Treatment-Effect Sensitivity Analysis

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Sensitivity Scenario Benchmark Results (100 Opportunities)

| Sensitivity Scenario | Action Multipliers | Simulated Recovered Revenue | Baseline Recovered Revenue | Simulated Incremental Revenue | Intervention Costs | Simulated Net Incremental Revenue | Simulated Overall Recovery Rate |
|---|---|---|---|---|---|---|---|
| **`ZERO_LIFT`** | All = 1.00x | INR 1,676,117.10 | INR 1,676,117.10 | INR 0.00 | INR 0.00 | **+INR 0.00** | 45.01% |
| **`CONSERVATIVE`** | Rem 1.10x, Ret 1.15x, Esc 1.08x | INR 1,676,117.10 | INR 1,676,117.10 | INR 0.00 | INR 2,568.00 | **INR -2,568.00** | 45.01% |
| **`BASE`** | Rem 1.20x, Ret 1.35x, Esc 1.15x | INR 1,869,764.50 | INR 1,676,117.10 | +INR 193,647.40 | INR 3,014.50 | **+INR 190,632.90** | 50.21% |
| **`OPTIMISTIC`** | Rem 1.35x, Ret 1.50x, Esc 1.25x | INR 2,141,269.40 | INR 1,676,117.10 | +INR 465,152.30 | INR 2,948.00 | **+INR 462,204.30** | 57.50% |
