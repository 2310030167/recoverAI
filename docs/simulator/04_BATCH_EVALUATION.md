# RecoverAI Simulator — Simulated Batch Results Using Empirical Invoice States

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Methodological Clarification

The invoice exposure amounts, due dates, customer payment terms, and historical late-payment rates originate directly from **empirical invoice states** (`Customer Invoices Dataset.csv`). However, intervention treatment effects and payment resolution events are **simulated**. The resulting incremental revenue is therefore a **simulated estimate**, not a proven real-world causal uplift claim.

---

## 2. 100-Opportunity Batch Results (Seed=42, Reproducible)

| Evaluation Metric | Simulated Baseline (`NO_ACTION`) | Simulated RecoverAI Strategy | Simulated Incremental Gain |
|---|---|---|---|
| **Total Invoices Evaluated** | 100 | 100 | — |
| **Total Invoice Exposure at Risk** | INR 3,723,928.21 | INR 3,723,928.21 | — |
| **Simulated Recovered Revenue** | INR 1,676,117.10 | INR 1,869,764.50 | **+INR 193,647.40** |
| **Total Intervention Costs** | INR 0.00 | INR 3,014.50 | INR 3,014.50 |
| **Simulated Net Recovered Value** | INR 1,676,117.10 | INR 1,866,750.00 | **+INR 190,632.90** |
| **Simulated Recovery Rate** | 45.01% | 50.21% | **+5.20%** |

- **Simulated 3-Day Window Recovery Rate**: **18.00%**
- **Simulated 7-Day Window Recovery Rate**: **29.00%**
- **Simulated 30-Day Window Recovery Rate**: **56.00%**

---

## 3. 500-Opportunity Batch Results (Larger Evaluation Mode)

| Evaluation Metric | Simulated Baseline (`NO_ACTION`) | Simulated RecoverAI Strategy | Simulated Incremental Gain |
|---|---|---|---|
| **Total Invoices Evaluated** | 500 | 500 | — |
| **Total Invoice Exposure at Risk** | INR 16,422,245.78 | INR 16,422,245.78 | — |
| **Simulated Recovered Revenue** | INR 8,392,675.78 | INR 9,274,593.27 | **+INR 881,917.49** |
| **Total Intervention Costs** | INR 0.00 | INR 13,153.00 | INR 13,153.00 |
| **Simulated Net Recovered Value** | INR 8,392,675.78 | INR 9,261,440.27 | **+INR 868,764.49** |
| **Simulated Recovery Rate** | 51.11% | 56.48% | **+5.37%** |
