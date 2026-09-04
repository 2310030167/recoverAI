# RecoverAI Data Engineering — Candidate Feature Taxonomy

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Purpose**: Standardize candidate ML features across Customer State, Payment Risk, Checkout Funnel, Receivables Overdue, and Intervention Selection.

## RecoverAI Feature Catalog

### 1. Customer State Features
| Feature Name | Source Dataset | Formula / Extraction Logic | ML Purpose |
|---|---|---|---|
| `cust_tenure_months` | `customer_churn_business_dataset.csv` | `(current_date - contract_start_date) / 30.4` | Measures customer longevity and baseline retention stability |
| `license_utilization_pct` | `customer_churn_business_dataset.csv` | `license_utilization_rate` | Identifies under-utilization driving risk of abandonment |
| `account_health_score` | `customer_churn_business_dataset.csv` | Composite score (0-100) | Directly indicates account distress prior to payment failure |
| `paperless_billing_active` | `WA_Fn-UseC_-Accounts-Receivable.csv` | Binary indicator (`PaperlessBill == 'Electronic'`) | Correlates with faster digital payment adoption |
| `dispute_history_ratio` | `WA_Fn-UseC_-Accounts-Receivable.csv` | `count(Disputed == 'Yes') / total_invoices` | Strongest predictor of intentional payment withholding |

### 2. Payment & Failure Risk Features
| Feature Name | Source Dataset | Formula / Extraction Logic | ML Purpose |
|---|---|---|---|
| `failed_payment_attempts_cnt` | `customer_churn_business_dataset.csv` | Count of payment failure events in last 30d | Primary trigger for hard vs soft dunning interventions |
| `avg_payment_delay_days` | `WA_Fn-UseC` / `customer_churn_business` | Rolling mean of `DaysLate` or `payment_delay_days` | Establishes customer baseline payment punctuality |
| `bank_failure_rate` | `UPI_transactions.csv` | `count(Status == 'FAILED' per Sender Bank) / total` | Indian context: Identifies bank downtime vs user error |
| `open_invoice_exposure` | `Customer Invoices Dataset.csv` | `sum(total_open_amount where isOpen == 1)` | Total monetary value currently at risk for the merchant |

### 3. Checkout Funnel & Abandonment Features
| Feature Name | Source Dataset | Formula / Extraction Logic | ML Purpose |
|---|---|---|---|
| `session_exit_rate` | `online_shoppers_intention.csv` | `ExitRates` | Measures probability of user leaving checkout step |
| `session_bounce_rate` | `online_shoppers_intention.csv` | `BounceRates` | Identifies landing page disconnects during payment |
| `page_value_score` | `online_shoppers_intention.csv` | `PageValues` | Quantifies economic intent of current user session |
| `product_time_engagement` | `online_shoppers_intention.csv` | `ProductRelated_Duration / (ProductRelated + 1)` | Higher duration signals high-intent hesitation |

### 4. Natural Recovery & Intervention Selection Features
| Feature Name | Source Dataset | Formula / Extraction Logic | ML Purpose |
|---|---|---|---|
| `p_natural_recovery` | Synthetic/Historical | Probability customer pays without merchant intervention | Prevents wasting intervention budget on customers who self-cure |
| `p_assisted_recovery` | Synthetic/Historical | Probability customer pays given specific intervention $k$ | Used in economic optimization equation |
| `net_expected_recovery_gain` | Derived | `p_assisted * Invoice_Amount - Intervention_Cost - (p_natural * Invoice_Amount)` | Core decision metric: execute intervention iff gain > 0 |