# RecoverAI Data Engineering — Target & Temporal Leakage Audit

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Rule Enforcement**: Absolute temporal segregation. Features must rely solely on point-in-time information available *prior* to the intervention decision.

## Column Risk Classification Summary

| Dataset Name | Column Name | Risk Status | Why it is Dangerous / Leakage Mechanism | Mandatory Pipeline Safeguard |
|---|---|---|---|---|
| `Customer Invoices Dataset.csv` | `clear_date` | **LEAKAGE_RISK** | Contains timestamp when invoice was cleared. In real-time decisioning, `clear_date` occurs AFTER payment/recovery. | Mask completely during feature extraction. Only use to construct historical target label. |
| `customer_churn_business_dataset.csv` | `churn_date` | **LEAKAGE_RISK** | Future timestamp recorded after churn occurs. | Exclude from feature set. Use only as observation window endpoint. |
| `customer_churn_business_dataset.csv` | `churn_reason` | **LEAKAGE_RISK** | Post-hoc exit interview feedback collected after customer cancels. | Exclude completely from predictive models. |
| `WA_Fn-UseC_-Accounts-Receivable.csv` | `DaysLate` | **CAUTION** | Static field in raw CSV representing total final late days. | Must be dynamically computed at inference time as `(as_of_date - DueDate)`. |
| `WA_Fn-UseC_-Accounts-Receivable.csv` | `DaysToPay` | **CAUTION** | Final total days to payment. Known only after payment clears. | Use as historical target variable, NOT as a predictive feature. |
| `online_shoppers_intention.csv` | `Revenue` | **LEAKAGE_RISK** | True target variable indicating session conversion. | Remove from session feature matrix; use as training label `y`. |
| `synthetic_fraud_data.csv` | `is_fraud` | **SAFE / N/A** | Dataset excluded from revenue recovery pipeline. | Exclude entire dataset. |

---

## Point-in-Time Temporal Segregation Architecture

```
Timeline of an At-Risk Revenue Event:

  [Invoice / Checkout Date] -------> [Due Date / Payment Failure] -------> [Intervention Decision T_0] -------> [Resolution / Payment Date]
  |---------------------------- FEATURE OBSERVATION WINDOW ----------------------------|  |--- DO NOT LEAK INTO FEATURES ---|
  Allowed Features:                                                                      Forbidden Leakage Columns:
  - Historical payment delay                                                               - clear_date
  - Account health score                                                                  - DaysToPay
  - Current open balance                                                                  - churn_date
  - Session exit rate                                                                     - churn_reason
```