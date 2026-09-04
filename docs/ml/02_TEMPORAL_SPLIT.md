# RecoverAI ML — Chronological Temporal Data Splitting

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Supervised Temporal Split Breakdown (Excluding Censored Invoices)

| Split Name | Date Range (`due_in_date`) | Total Count | Observable Pos ($y=1$) | Observable Neg ($y=0$) | Positive Rate | Right-Censored Excluded |
|---|---|---|---|---|---|---|
| **TRAIN** | `2018-12-24` to `2019-11-30` | **30,975** | 30,234 | 741 | **97.61%** | 0 |
| **VALIDATION** | `2019-12-01` to `2020-01-31` | **4,434** | 4,385 | 49 | **98.89%** | 0 |
| **TEST** | `2020-02-01` to `2020-06-07` | **9,479** | 3,675 | 5,804 | **38.77%** | **3,951** |
| **TOTAL** | `2018-12-24` to `2020-07-10` | **44,888** | **38,294** | **6,594** | **85.31%** | **3,951** |
