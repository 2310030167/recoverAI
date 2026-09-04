# RecoverAI Data Engineering — Final Strategic Recommendation

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Core Objective**: Bounded, economically optimal intervention execution to maximize net recovered revenue.

## Final Dataset Ranking & Selection for Track 03

### 1. PRIMARY DATASETS (CORE - Receivables & B2B Revenue Recovery)
1. **`WA_Fn-UseC_-Accounts-Receivable.csv`** (IBM Watson AR Benchmark)
   - *Why Primary*: Pristine real-world B2B receivables dataset with explicit `DaysLate`, `Disputed` status, invoice amounts, and payment modes. Directly models invoice delinquency diagnosis and dispute risk.
2. **`customer_churn_business_dataset.csv`** (B2B SaaS Revenue At Risk)
   - *Why Primary*: Rich enterprise SaaS dataset containing payment delays, failed payment attempts, monthly recurring revenue (MRR), and account health scores. Perfect for modeling dunning interventions and churn prevention.
3. **`Customer Invoices Dataset.csv`** (SAP Enterprise Invoices)
   - *Why Primary*: 50,000 real SAP enterprise invoices with clear payment dates vs open unpaid invoices (`isOpen == 1`). Provides large-scale empirical training data for expected resolution window modeling.
4. **`online_shoppers_intention.csv`** (Checkout Abandonment)
   - *Why Primary*: Benchmark UCI dataset for real-time checkout funnel analysis. Essential for modeling payment drop-off at checkout and exit-intent intervention timing.

### 2. SIMULATOR INPUT DATA (SECONDARY - Indian Payment Ecosystem)
1. **`UPI_transactions.csv`**
   - *Why Simulator*: Contains Indian UPI transaction statuses (`SUCCESS`, `FAILED`), bank handles, and INR monetary amounts. Used to tune RecoverAI's Razorpay-specific payment failure simulator (NPCI bank downtime vs user authorization failure).

### 3. SECONDARY DATASETS (Customer Lifetime History)
1. **`Online Retail.xlsx` & `online_retail_II.xlsx`**
   - *Role*: Provides multi-year customer purchasing history to derive customer LTV and repeat purchase cadence features.

### 4. OPTIONAL DATASETS
1. **`customer_churn_dataset.csv`** & **`customer_subscription_churn_usage_patterns.csv`**
   - *Role*: Generic consumer B2C churn sets. Useful for cross-domain baseline validation if needed.

### 5. EXCLUDE
1. **`synthetic_fraud_data.csv`** (2.93 GB)
   - *Reason for Exclusion*: Exclusively focuses on credit card fraud detection (unauthorized transactions, stolen cards). Track 03 is **AI Revenue Recovery** (failed legitimate payments, checkout friction, invoice delinquency). Fraud filtering belongs to core gateway security, not revenue recovery.

---

## RecoverAI Data Engineering Execution Roadmap

1. **Step 1: Point-in-Time Feature Pipeline Construction**
   - Implement clean ETL loaders for the 4 Primary datasets and 1 Simulator input dataset.
   - Enforce temporal masking on `clear_date` and `churn_date` to prevent target leakage.
2. **Step 2: Natural Recovery vs Assisted Recovery Estimator**
   - Train baseline survival / time-to-pay models to estimate $P(\text{Natural Recovery})$ vs $P(\text{Assisted Recovery} \mid \text{Intervention}_k)$.
3. **Step 3: Economically Bounded Intervention Engine**
   - Integrate intervention costs (e.g. WhatsApp notification fee $c_{wa} = \text{\₹}0.50$, SMS fee $c_{sms} = \text{\₹}0.12$, Discount offer $c_{disc} = 5\% \times \text{Amount}$).
   - Compute Expected Net Recovery Gain: $\Delta E(\text{Rev}) = P_{\text{assisted}} \cdot A - c_{\text{interv}} - P_{\text{natural}} \cdot A$. Trigger intervention iff $\Delta E(\text{Rev}) > 0$.