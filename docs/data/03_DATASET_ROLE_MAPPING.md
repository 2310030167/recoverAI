# RecoverAI Data Engineering — Dataset Role Mapping & Classification

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Objective**: Map raw datasets to functional revenue-recovery lifecycle roles and assign importance tiers.

## Functional Role Classification Matrix

| Dataset Filename | Primary Role(s) | Importance Tier | RecoverAI Pipeline Stage Support |
|---|---|---|---|
| `WA_Fn-UseC_-Accounts-Receivable.csv` | **E. RECEIVABLES**, **A. CUSTOMER_BEHAVIOR**, **J. RECOVERY_INTERVENTION** | **CORE** | Invoicing delay diagnosis, dispute detection, overdue risk scoring, payment terms optimization |
| `customer_churn_business_dataset.csv` | **E. RECEIVABLES**, **F. SUBSCRIPTION**, **D. PAYMENT_BEHAVIOR**, **G. CUSTOMER_LIFECYCLE** | **CORE** | B2B SaaS payment failure recovery, dunning strategy, health score risk triggers |
| `Customer Invoices Dataset.csv` | **E. RECEIVABLES**, **B. TRANSACTION_BEHAVIOR** | **CORE** | SAP enterprise AR collection, clear date estimation, overdue payment forecasting |
| `online_shoppers_intention.csv` | **C. CHECKOUT_BEHAVIOR**, **A. CUSTOMER_BEHAVIOR** | **CORE** | Real-time checkout abandonment detection, session intent scoring, exit-intent intervention |
| `UPI_transactions.csv` | **H. INDIAN_PAYMENT_CONTEXT**, **D. PAYMENT_BEHAVIOR** | **SECONDARY (SIMULATOR)** | Indian UPI retry optimization, NPCI bank failure diagnosis, instant retry routing |
| `Online Retail.xlsx` | **B. TRANSACTION_BEHAVIOR**, **A. CUSTOMER_BEHAVIOR** | **SECONDARY** | Historical purchase sequence, customer LTV, re-engagement windowing |
| `online_retail_II.xlsx` | **B. TRANSACTION_BEHAVIOR**, **A. CUSTOMER_BEHAVIOR** | **SECONDARY** | Long-term customer purchase history & repeat transaction frequency modeling |
| `customer_churn_dataset.csv` | **G. CUSTOMER_LIFECYCLE**, **D. PAYMENT_BEHAVIOR** | **OPTIONAL** | Generic consumer churn modeling baseline |
| `customer_subscription_churn_usage_patterns.csv` | **F. SUBSCRIPTION**, **A. CUSTOMER_BEHAVIOR** | **OPTIONAL** | Consumer subscription usage vs payment delinquency evaluation |
| `synthetic_fraud_data.csv` | **I. FRAUD / SAFETY** | **EXCLUDE** | Card fraud security filter (Outside Track 03 AI Revenue Recovery scope) |

---

## Semantic Field Alignment Audit

### 1. Customer Semantics
- `WA_Fn-UseC_-Accounts-Receivable.csv`: `customerID`, `countryCode`
- `customer_churn_business_dataset.csv`: `customer_id`, `company_name`, `industry`, `company_size`, `annual_revenue`
- `Customer Invoices Dataset.csv`: `cust_number`, `name_customer`, `business_code`
- `Online Retail.xlsx` & `online_retail_II.xlsx`: `CustomerID`, `Country`

### 2. Transaction & Invoicing Semantics
- `WA_Fn-UseC_-Accounts-Receivable.csv`: `invoiceNumber`, `InvoiceDate`, `invoiceAmount`
- `Customer Invoices Dataset.csv`: `invoice_id`, `doc_id`, `posting_date`, `total_open_amount`, `invoice_currency`
- `Online Retail.xlsx` & `online_retail_II.xlsx`: `InvoiceNo`, `StockCode`, `Quantity`, `UnitPrice`, `InvoiceDate`
- `synthetic_fraud_data.csv`: `transaction_id`, `amount`, `currency`, `timestamp`

### 3. Payment & Receivables Delay Semantics
- `WA_Fn-UseC_-Accounts-Receivable.csv`: `DueDate`, `DaysToPay`, `DaysLate`, `Disputed`, `PayMode`, `PaperlessBill`
- `customer_churn_business_dataset.csv`: `payment_delay_days`, `late_payment_count`, `failed_payment_attempts`, `billing_frequency`, `payment_method`
- `Customer Invoices Dataset.csv`: `due_in_date`, `clear_date`, `cust_payment_terms`, `isOpen`
- `UPI_transactions.csv`: `Status` (`SUCCESS`, `FAILED`), `Amount (INR)`, `Sender Bank`, `Receiver Bank`

### 4. Checkout Funnel & Session Semantics
- `online_shoppers_intention.csv`: `Administrative_Duration`, `Informational_Duration`, `ProductRelated_Duration`, `BounceRates`, `ExitRates`, `PageValues`, `SpecialDay`, `VisitorType`, `Weekend`, `Revenue`

### 5. Subscription Semantics
- `customer_churn_business_dataset.csv`: `subscription_tier`, `monthly_recurring_revenue`, `total_contract_value`, `auto_renew`, `contract_length_months`, `feature_usage_score`, `active_users`, `license_utilization_rate`
- `customer_subscription_churn_usage_patterns.csv`: `Subscription_Type`, `Monthly_Usage_GB`, `Subscription_Fee`, `Payment_Status`, `Days_Active`