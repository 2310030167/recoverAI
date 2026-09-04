# RecoverAI ML — Point-in-Time Feature Pipeline

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Enhanced Historical Customer Behavioral Features (Task 7)

Constructed strictly prior to decision cutoff $T_0 = T_{\text{due}}$ using expanding cumulative customer grouping:

- `cust_historical_invoice_count`: Number of past invoices for customer prior to $T_0$.
- `cust_historical_avg_amount`: Expanding mean invoice value prior to $T_0$.
- `cust_historical_avg_delay`: Historical mean payment delay days prior to $T_0$.
- `cust_historical_late_rate`: Proportion of past invoices cleared late prior to $T_0$.
- `cust_recency_days`: Days since customer's previous invoice due date prior to $T_0$.
