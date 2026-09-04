# RecoverAI Data Engineering — Data Quality & Integrity Audit

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Audit Target**: All 10 raw datasets inside `data/raw/`
> **Rule Enforcement**: Raw files are un-modified. All data quality defects are cataloged below.

## Executive Data Quality Assessment Summary

| Dataset Name | Missing Data Issues | Duplicate Rows | Format Inconsistencies | Negative / Zero Amounts | Target Leakage Risk | Overall Quality Grade |
|---|---|---|---|---|---|---|
| `WA_Fn-UseC_-Accounts-Receivable.csv` | **0 missing values (0%)** | **0 duplicates** | Clean numeric & text | 0 negative, 0 zero | Low (Point-in-time calculation required) | **A+ (PRISTINE)** |
| `customer_churn_business_dataset.csv` | **0 missing values (0%)** | **0 duplicates** | Clean structured B2B | 0 negative, 0 zero | High (`churn_reason`, `churn_date`) | **A (HIGH QUALITY)** |
| `Customer Invoices Dataset.csv` | `clear_date` missing 20% (10,000 open), `area_business` 100% missing | **1,161 duplicate rows** | `due_in_date` float YYYYMMDD, `document_create_date` epoch | 0 negative, 0 zero | High (`clear_date` reveals resolution) | **B (GOOD WITH REMEDIATION)** |
| `online_shoppers_intention.csv` | **0 missing values (0%)** | **117 duplicate rows** | Clean checkout session stats | N/A (Session metrics) | High (`Revenue` is target) | **A (HIGH QUALITY)** |
| `UPI_transactions.csv` | **0 missing values (0%)** | **0 duplicates** | Clean Indian UPI transaction log | 0 negative, 0 zero | Low | **A+ (PRISTINE SIMULATOR DATA)** |
| `Online Retail.xlsx` | `CustomerID` missing 24.93% (135,080 rows) | **5,268 duplicate rows** | `InvoiceNo` contains 'C' prefixes | **10,624 negative quantities**, **2 negative prices** | Low | **B- (REQUIRES CLEANING IN PIPELINE)** |
| `online_retail_II.xlsx` | `Customer ID` missing 22.8% (243,007 rows) | **34,717 duplicate rows** | `Invoice` contains 'C' prefixes | **22,950 negative quantities**, **5 negative prices** | Low | **B- (REQUIRES CLEANING IN PIPELINE)** |
| `customer_churn_dataset.csv` | **0 missing values (0%)** | **0 duplicates** | Generic telecom tabular | 0 negative | Low | **B (GENERIC SYNTHETIC)** |
| `customer_subscription_churn_usage_patterns.csv` | **0 missing values (0%)** | **0 duplicates** | Generic consumer subscription | 0 negative | Low | **B (GENERIC SYNTHETIC)** |
| `synthetic_fraud_data.csv` | **0 missing values (0%)** | **0 duplicates (sample)** | Velocity column contains stringified JSON | 0 negative, 0 zero | High (Post-transaction fraud flag) | **C (UNSUITABLE FOR REVENUE RECOVERY)** |

---

## Detailed Category Breakdown of Data Quality Issues

### 1. Missing Data Problems
> [!WARNING]
> Raw files contain critical missingness patterns that reflect business domain states (e.g. uncollected open invoices) rather than random data loss.

- **`Customer Invoices Dataset.csv`**:
  - `clear_date`: Missing **10,000 out of 50,000 values (20.0%)**. *Analysis*: This is **not random missing data**. Rows with missing `clear_date` correspond exactly to `isOpen == 1` (uncollected open invoices). In ML feature engineering, missing `clear_date` must be handled as open invoices undergoing active collection.
  - `area_business`: Missing **50,000 out of 50,000 values (100.0%)**. *Analysis*: Unusable constant null column. Must be dropped during feature extraction.
- **`Online Retail.xlsx` & `online_retail_II.xlsx`**:
  - `CustomerID` / `Customer ID`: Missing **135,080 values (24.93%)** in `Online Retail.xlsx` and **243,007 values (22.8%)** in `online_retail_II.xlsx` across 1,067,371 total rows.
  - *Analysis*: Missing Customer IDs represent guest checkout sessions where users purchased without creating an account. Customer-level aggregation pipelines must segregate registered vs guest checkout transactions.
  - `Description`: Missing **1,454 values (0.27%)** in `Online Retail.xlsx` and **4,382 values** in `online_retail_II.xlsx` (mostly admin adjustments and lost stock entries).

### 2. Duplicate Row Problems
- **`Customer Invoices Dataset.csv`**: Contains **1,161 exact duplicate rows**.
- **`Online Retail.xlsx`**: Contains **5,268 exact duplicate rows**.
- **`online_retail_II.xlsx`**: Contains **34,717 exact duplicate rows** across the 2 yearly sheets.
- **`online_shoppers_intention.csv`**: Contains **117 duplicate session rows**.
*Recommendation*: Deduplication must occur in the feature pre-processing pipeline before windowed aggregations.

### 3. Inconsistent Formats & Type Anomalies
- **`Customer Invoices Dataset.csv`**:
  - `due_in_date`: Stored as a floating-point integer representation of `YYYYMMDD.0` (e.g. `20190121.0`). Requires explicit parsing into standard `datetime64[ns]` ISO strings.
  - `document_create_date` and `document_create_date.1`: Stored as integer YYYYMMDD (e.g. `20181226`), which Pandas initially inferred as Unix epoch nanoseconds. Requires explicit date format string conversion (`%Y%m%d`).
- **`synthetic_fraud_data.csv`**:
  - `velocity_last_hour`: Stored as a raw string representation of a Python dictionary (e.g. `{'num_transactions': 676, 'total_amount': 40250796.47, ...}`). If parsed, requires JSON deserialization (`json.loads`).

### 4. Suspicious & Impossible Values
- **`Online Retail.xlsx` & `online_retail_II.xlsx`**:
  - **Negative Quantities**: `Quantity` ranges from **-80,995 to +80,995** in `Online Retail.xlsx` (10,624 negative rows) and **-80,995 to +19,152** in `online_retail_II.xlsx` (22,950 negative rows).
  - *Diagnosis*: Invoice numbers starting with `'C'` (e.g. `C536379`) indicate product returns or order cancellations. Negative quantities are valid cancellation records in retail data, but must be factored into net revenue recovery logic.
  - **Negative Unit Prices**: `UnitPrice` / `Price` contains negative entries (e.g., `-11062.06` for manual accounting debt adjustments `Adjust bad debt`).

### 5. Future Timestamps & Temporal Verification
Current System Date: **2026-08-23**.
- All historical dates across datasets are in the past:
  - `Customer Invoices Dataset.csv`: 2018-12-30 to 2020-05-22
  - `Online Retail.xlsx`: 2010-12-01 to 2011-12-09
  - `online_retail_II.xlsx`: 2009-12-01 to 2011-12-09
  - `synthetic_fraud_data.csv`: 2024-09-30 to 2024-10-06
- **No future dates relative to 2026 exist**.

### 6. Suspicious IDs & Data Provenance Verification
| Dataset | File Provenance | Verification Source & Method |
|---|---|---|
| `WA_Fn-UseC_-Accounts-Receivable.csv` | **REAL** | Verified standard IBM Watson Analytics B2B Accounts Receivable Dataset benchmark. |
| `customer_churn_business_dataset.csv` | **REAL** | Structured B2B SaaS Enterprise churn & payment failure benchmark dataset. |
| `Customer Invoices Dataset.csv` | **REAL** | Real SAP enterprise accounts receivable invoice dataset with genuine customer names (`WAL-MAR`, `TAGT`, `SUPE`). |
| `online_shoppers_intention.csv` | **REAL** | UCI Machine Learning Repository benchmark dataset from Turkish e-commerce session logs. |
| `Online Retail.xlsx` & `online_retail_II.xlsx` | **REAL** | UCI Machine Learning Repository benchmark dataset from UK-based online gift retailer. |
| `UPI_transactions.csv` | **SYNTHETIC** | Simulated dataset matching Indian UPI ecosystem fields (NPCI structure, bank handles, INR). |
| `customer_churn_dataset.csv` | **SYNTHETIC** | Generated synthetic consumer telecom churn dataset. |
| `customer_subscription_churn_usage_patterns.csv` | **SYNTHETIC** | Generated synthetic consumer subscription dataset. |
| `synthetic_fraud_data.csv` | **SYNTHETIC** | Synthetically generated high-volume card transaction log. |