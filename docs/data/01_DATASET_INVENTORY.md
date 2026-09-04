# RecoverAI Data Engineering — Dataset Inventory Report

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Status**: Complete Raw Dataset Audit
> **Total Datasets Audited**: 10 files | **Total Records**: 9,221,642 rows | **Total Size**: 2876.58 MB

## Executive Dataset Inventory Table

| Filename | Format | Size (MB) | Sheets | Total Rows | Total Cols | Provenance | Track 03 Tier |
|---|---|---|---|---|---|---|---|
| [`Customer Invoices Dataset.csv`](file:///d:/recoverai/data/raw/Customer%20Invoices%20Dataset.csv) | `.csv` | 7.43 MB | 1 | 50,000 | 19 | **REAL** | **CORE** |
| [`Online Retail.xlsx`](file:///d:/recoverai/data/raw/Online%20Retail.xlsx) | `.xlsx` | 22.62 MB | 1 | 541,909 | 8 | **REAL** | **SECONDARY** |
| [`UPI_transactions.csv`](file:///d:/recoverai/data/raw/UPI_transactions.csv) | `.csv` | 0.13 MB | 1 | 1,000 | 8 | **SYNTHETIC** | **SECONDARY (SIMULATOR)** |
| [`WA_Fn-UseC_-Accounts-Receivable.csv`](file:///d:/recoverai/data/raw/WA_Fn-UseC_-Accounts-Receivable.csv) | `.csv` | 0.21 MB | 1 | 2,466 | 12 | **REAL** | **CORE** |
| [`customer_churn_business_dataset.csv`](file:///d:/recoverai/data/raw/customer_churn_business_dataset.csv) | `.csv` | 1.69 MB | 1 | 10,000 | 32 | **REAL** | **CORE** |
| [`customer_churn_dataset.csv`](file:///d:/recoverai/data/raw/customer_churn_dataset.csv) | `.csv` | 1.55 MB | 1 | 50,000 | 7 | **SYNTHETIC** | **OPTIONAL** |
| [`customer_subscription_churn_usage_patterns.csv`](file:///d:/recoverai/data/raw/customer_subscription_churn_usage_patterns.csv) | `.csv` | 0.12 MB | 1 | 2,800 | 10 | **SYNTHETIC** | **OPTIONAL** |
| [`online_retail_II.xlsx`](file:///d:/recoverai/data/raw/online_retail_II.xlsx) | `.xlsx` | 43.51 MB | 2 | 1,067,371 | 8 | **REAL** | **SECONDARY** |
| [`online_shoppers_intention.csv`](file:///d:/recoverai/data/raw/online_shoppers_intention.csv) | `.csv` | 1.02 MB | 1 | 12,330 | 18 | **REAL** | **CORE** |
| [`synthetic_fraud_data.csv`](file:///d:/recoverai/data/raw/synthetic_fraud_data.csv) | `.csv` | 2798.3 MB | 1 | 7,483,766 | 24 | **SYNTHETIC** | **EXCLUDE** |

---

## Detailed File-by-File Technical Profiles

### Dataset: `Customer Invoices Dataset.csv`
- **Path**: `data/raw/Customer Invoices Dataset.csv`
- **File Size**: 7.43 MB (7,790,548 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 50,000 | **Max Columns**: 19
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **CORE**

#### Sheet/Table: `default` (50,000 rows, 19 cols, Duplicate Rows: 1161)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `business_code` | `str` | `categorical` | 0 | 0.0% | 6 | No | Yes | No |
| `cust_number` | `str` | `categorical` | 0 | 0.0% | 1425 | No | Yes | No |
| `name_customer` | `str` | `categorical` | 0 | 0.0% | 4197 | No | Yes | No |
| `clear_date` | `str` | `datetime` | 10,000 | 20.0% | 404 | No | No | No |
| `buisness_year` | `float64` | `numerical` | 0 | 0.0% | 2 | No | No | No |
| `doc_id` | `float64` | `numerical` | 0 | 0.0% | 48839 | No | Yes | No |
| `posting_date` | `str` | `datetime` | 0 | 0.0% | 506 | No | No | No |
| `document_create_date` | `int64` | `datetime` | 0 | 0.0% | 507 | No | No | No |
| `document_create_date.1` | `int64` | `datetime` | 0 | 0.0% | 506 | No | No | No |
| `due_in_date` | `float64` | `monetary` | 0 | 0.0% | 547 | No | No | Yes |
| `invoice_currency` | `str` | `categorical` | 0 | 0.0% | 2 | No | Yes | No |
| `document type` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `posting_id` | `float64` | `numerical` | 0 | 0.0% | 1 | Yes | Yes | No |
| `area_business` | `float64` | `numerical` | 50,000 | 100.0% | 1 | Yes | No | No |
| `total_open_amount` | `float64` | `monetary` | 0 | 0.0% | 44349 | No | No | Yes |
| `baseline_create_date` | `float64` | `numerical` | 0 | 0.0% | 506 | No | No | No |
| `cust_payment_terms` | `str` | `categorical` | 0 | 0.0% | 74 | No | No | No |
| `invoice_id` | `float64` | `monetary` | 6 | 0.012% | 48834 | No | Yes | Yes |
| `isOpen` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `buisness_year` | 2019.00 | 2020.00 | 2019.31 | 2019.00 | 0.46 | 2019.00 | 2020.00 | 0 | 0 |
| `doc_id` | 1928501756.00 | 9500000133.00 | 2012238145.97 | 1929963919.50 | 288523548.91 | 1928576687.63 | 2960621970.06 | 0 | 0 |
| `due_in_date` | 20181224.00 | 20200710.00 | 20193679.29 | 20190926.00 | 4470.61 | 20190121.00 | 20200522.00 | 0 | 0 |
| `posting_id` | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0 | 0 |
| `area_business` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 0 |
| `total_open_amount` | 0.72 | 668593.36 | 32337.02 | 17609.01 | 39205.98 | 70.80 | 163871.72 | 0 | 0 |
| `baseline_create_date` | 20181214.00 | 20200522.00 | 20193539.93 | 20190909.00 | 4482.70 | 20190105.00 | 20200505.00 | 0 | 0 |
| `invoice_id` | 1928501756.00 | 2960635652.00 | 2011339506.70 | 1929963780.50 | 276633494.12 | 1928576679.41 | 2960621932.89 | 0 | 0 |
| `isOpen` | 0.00 | 1.00 | 0.20 | 0.00 | 0.40 | 0.00 | 1.00 | 40,000 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `clear_date` | `2019-01-03 00:00:00` | `2020-05-22 00:00:00` | 505 days 00:00:00 |
| `posting_date` | `2018-12-30 00:00:00` | `2020-05-22 00:00:00` | 509 days 00:00:00 |
| `document_create_date` | `1970-01-01 00:00:00.020181226` | `1970-01-01 00:00:00.020200522` | 0 days 00:00:00.000019296 |
| `document_create_date.1` | `1970-01-01 00:00:00.020181230` | `1970-01-01 00:00:00.020200522` | 0 days 00:00:00.000019292 |

##### Categorical Column Distributions (Top 10 Values)

- **`business_code`** (6 unique): `U001`: 45,359, `CA02`: 3,917, `U013`: 573, `U002`: 135, `U005`: 11...
- **`cust_number`** (1425 unique): `0200769623`: 11,483, `0200726979`: 1,885, `0200762301`: 1,557, `0200759878`: 1,395, `0200794332`: 1,142...
- **`name_customer`** (4197 unique): `WAL-MAR trust`: 1,179, `WAL-MAR in`: 1,150, `WAL-MAR corp`: 1,136, `WAL-MAR `: 1,135, `WAL-MAR llc`: 1,123...
- **`invoice_currency`** (2 unique): `USD`: 46,081, `CAD`: 3,919...
- **`document type`** (2 unique): `RV`: 49,994, `X2`: 6...
- **`cust_payment_terms`** (74 unique): `NAA8`: 20,118, `NAH4`: 13,585, `CA10`: 3,800, `NAC6`: 1,743, `NAM4`: 1,385...

---

### Dataset: `Online Retail.xlsx`
- **Path**: `data/raw/Online Retail.xlsx`
- **File Size**: 22.62 MB (23,715,344 bytes)
- **Format**: `.xlsx` | **Sheets**: 1
- **Total Rows**: 541,909 | **Max Columns**: 8
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **SECONDARY**

#### Sheet/Table: `Online Retail` (541,909 rows, 8 cols, Duplicate Rows: 5268)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `InvoiceNo` | `object` | `categorical` | 0 | 0.0% | 25900 | No | Yes | No |
| `StockCode` | `object` | `categorical` | 0 | 0.0% | 4070 | No | Yes | No |
| `Description` | `object` | `categorical` | 1,454 | 0.2683% | 4224 | No | No | No |
| `Quantity` | `int64` | `numerical` | 0 | 0.0% | 722 | No | No | No |
| `InvoiceDate` | `datetime64[us]` | `datetime` | 0 | 0.0% | 23260 | No | Yes | No |
| `UnitPrice` | `float64` | `monetary` | 0 | 0.0% | 1630 | No | No | Yes |
| `CustomerID` | `float64` | `numerical` | 135,080 | 24.9267% | 4373 | No | Yes | No |
| `Country` | `str` | `categorical` | 0 | 0.0% | 38 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `Quantity` | -80995.00 | 80995.00 | 9.55 | 3.00 | 218.08 | -2.00 | 100.00 | 0 | 10,624 |
| `UnitPrice` | -11062.06 | 38970.00 | 4.61 | 2.08 | 96.76 | 0.19 | 18.00 | 2,515 | 2 |
| `CustomerID` | 12346.00 | 18287.00 | 15287.69 | 15152.00 | 1713.60 | 12415.00 | 18212.00 | 0 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `InvoiceDate` | `2010-12-01 08:26:00` | `2011-12-09 12:50:00` | 373 days 04:24:00 |

##### Categorical Column Distributions (Top 10 Values)

- **`InvoiceNo`** (25900 unique): `573585`: 1,114, `581219`: 749, `581492`: 731, `580729`: 721, `558475`: 705...
- **`StockCode`** (4070 unique): `85123A`: 2,313, `22423`: 2,203, `85099B`: 2,159, `47566`: 1,727, `20725`: 1,639...
- **`Description`** (4224 unique): `WHITE HANGING HEART T-LIGHT HOLDER`: 2,369, `REGENCY CAKESTAND 3 TIER`: 2,200, `JUMBO BAG RED RETROSPOT`: 2,159, `PARTY BUNTING`: 1,727, `LUNCH BAG RED RETROSPOT`: 1,638...
- **`Country`** (38 unique): `United Kingdom`: 495,478, `Germany`: 9,495, `France`: 8,557, `EIRE`: 8,196, `Spain`: 2,533...

---

### Dataset: `UPI_transactions.csv`
- **Path**: `data/raw/UPI_transactions.csv`
- **File Size**: 0.13 MB (137,073 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 1,000 | **Max Columns**: 8
- **Provenance**: **SYNTHETIC** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **SECONDARY (SIMULATOR)**

#### Sheet/Table: `default` (1,000 rows, 8 cols, Duplicate Rows: 0)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `Transaction ID` | `str` | `categorical` | 0 | 0.0% | 1000 | No | Yes | No |
| `Timestamp` | `str` | `datetime` | 0 | 0.0% | 1000 | No | Yes | No |
| `Sender Name` | `str` | `categorical` | 0 | 0.0% | 997 | No | No | No |
| `Sender UPI ID` | `str` | `categorical` | 0 | 0.0% | 1000 | No | Yes | No |
| `Receiver Name` | `str` | `categorical` | 0 | 0.0% | 996 | No | No | No |
| `Receiver UPI ID` | `str` | `categorical` | 0 | 0.0% | 1000 | No | Yes | No |
| `Amount (INR)` | `float64` | `monetary` | 0 | 0.0% | 999 | No | No | Yes |
| `Status` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `Amount (INR)` | 28.52 | 9993.06 | 4999.02 | 4951.43 | 2873.48 | 143.17 | 9913.94 | 0 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `Timestamp` | `2024-06-04 00:15:27` | `2024-07-03 23:15:06` | 29 days 22:59:39 |

##### Categorical Column Distributions (Top 10 Values)

- **`Transaction ID`** (1000 unique): `4d3db980-46cd-4158-a812-dcb77055d0d2`: 1, `099ee548-2fc1-4811-bf92-559c467ca792`: 1, `d4c05732-6b1b-4bab-90b9-efe09d252b99`: 1, `e8df92ee-8b04-4133-af5a-5f412180c8ab`: 1, `e7d675d3-04f1-419c-a841-7a04662560b7`: 1...
- **`Sender Name`** (997 unique): `Aayush Bakshi`: 2, `Prerak Lanka`: 2, `Ivan Ramesh`: 2, `Tiya Mall`: 1, `Mohanlal Bakshi`: 1...
- **`Sender UPI ID`** (1000 unique): `4161803452@okaxis`: 1, `8908837379@okaxis`: 1, `4633654150@okybl`: 1, `7018842771@okhdfcbank`: 1, `1977143985@okybl`: 1...
- **`Receiver Name`** (996 unique): `Samarth Gala`: 2, `Tarini Anand`: 2, `Ryan Varughese`: 2, `Purab Gandhi`: 2, `Mohanlal Golla`: 1...
- **`Receiver UPI ID`** (1000 unique): `7776849307@okybl`: 1, `7683454560@okaxis`: 1, `2598130823@okicici`: 1, `2246623650@okaxis`: 1, `5245672729@okybl`: 1...
- **`Status`** (2 unique): `SUCCESS`: 502, `FAILED`: 498...

---

### Dataset: `WA_Fn-UseC_-Accounts-Receivable.csv`
- **Path**: `data/raw/WA_Fn-UseC_-Accounts-Receivable.csv`
- **File Size**: 0.21 MB (220,150 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 2,466 | **Max Columns**: 12
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **CORE**

#### Sheet/Table: `default` (2,466 rows, 12 cols, Duplicate Rows: 0)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `countryCode` | `int64` | `numerical` | 0 | 0.0% | 5 | No | Yes | No |
| `customerID` | `str` | `categorical` | 0 | 0.0% | 100 | No | Yes | No |
| `PaperlessDate` | `str` | `datetime` | 0 | 0.0% | 91 | No | No | No |
| `invoiceNumber` | `int64` | `monetary` | 0 | 0.0% | 2466 | No | Yes | Yes |
| `InvoiceDate` | `str` | `datetime` | 0 | 0.0% | 681 | No | Yes | No |
| `DueDate` | `str` | `datetime` | 0 | 0.0% | 681 | No | No | No |
| `InvoiceAmount` | `float64` | `monetary` | 0 | 0.0% | 2098 | No | Yes | Yes |
| `Disputed` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `SettledDate` | `str` | `datetime` | 0 | 0.0% | 695 | No | No | No |
| `PaperlessBill` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `DaysToSettle` | `int64` | `numerical` | 0 | 0.0% | 67 | No | No | No |
| `DaysLate` | `int64` | `numerical` | 0 | 0.0% | 37 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `countryCode` | 391.00 | 897.00 | 620.45 | 770.00 | 215.93 | 391.00 | 897.00 | 0 | 0 |
| `invoiceNumber` | 611365.00 | 9990243864.00 | 4978430514.97 | 4964228313.50 | 2884271865.47 | 79569714.20 | 9882846564.85 | 0 | 0 |
| `InvoiceAmount` | 5.26 | 128.28 | 59.90 | 60.56 | 20.44 | 10.16 | 104.19 | 0 | 0 |
| `DaysToSettle` | 0.00 | 75.00 | 26.44 | 26.00 | 12.33 | 2.00 | 56.00 | 4 | 0 |
| `DaysLate` | 0.00 | 45.00 | 3.44 | 0.00 | 6.29 | 0.00 | 26.00 | 1,589 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `PaperlessDate` | `2012-01-09 00:00:00` | `2013-11-27 00:00:00` | 688 days 00:00:00 |
| `InvoiceDate` | `2012-01-03 00:00:00` | `2013-12-02 00:00:00` | 699 days 00:00:00 |
| `DueDate` | `2012-02-02 00:00:00` | `2014-01-01 00:00:00` | 699 days 00:00:00 |
| `SettledDate` | `2012-01-13 00:00:00` | `2014-01-09 00:00:00` | 727 days 00:00:00 |

##### Categorical Column Distributions (Top 10 Values)

- **`customerID`** (100 unique): `9149-MATVB`: 36, `8887-NCUZC`: 35, `4640-FGEJI`: 35, `9286-VLKMI`: 34, `0688-XNJRO`: 34...
- **`Disputed`** (2 unique): `No`: 1,905, `Yes`: 561...
- **`PaperlessBill`** (2 unique): `Paper`: 1,263, `Electronic`: 1,203...

---

### Dataset: `customer_churn_business_dataset.csv`
- **Path**: `data/raw/customer_churn_business_dataset.csv`
- **File Size**: 1.69 MB (1,769,457 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 10,000 | **Max Columns**: 32
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **CORE**

#### Sheet/Table: `default` (10,000 rows, 32 cols, Duplicate Rows: 0)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `customer_id` | `str` | `categorical` | 0 | 0.0% | 10000 | No | Yes | No |
| `gender` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `age` | `int64` | `numerical` | 0 | 0.0% | 57 | No | No | No |
| `country` | `str` | `categorical` | 0 | 0.0% | 7 | No | No | No |
| `city` | `str` | `categorical` | 0 | 0.0% | 7 | No | No | No |
| `customer_segment` | `str` | `categorical` | 0 | 0.0% | 3 | No | Yes | No |
| `tenure_months` | `int64` | `numerical` | 0 | 0.0% | 59 | No | No | No |
| `signup_channel` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `contract_type` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `monthly_logins` | `int64` | `numerical` | 0 | 0.0% | 53 | No | No | No |
| `weekly_active_days` | `int64` | `numerical` | 0 | 0.0% | 8 | No | No | No |
| `avg_session_time` | `float64` | `numerical` | 0 | 0.0% | 9777 | No | No | No |
| `features_used` | `int64` | `numerical` | 0 | 0.0% | 15 | No | No | No |
| `usage_growth_rate` | `float64` | `numerical` | 0 | 0.0% | 104 | No | No | No |
| `last_login_days_ago` | `int64` | `numerical` | 0 | 0.0% | 71 | No | No | No |
| `monthly_fee` | `int64` | `monetary` | 0 | 0.0% | 6 | No | No | Yes |
| `total_revenue` | `int64` | `monetary` | 0 | 0.0% | 221 | No | No | Yes |
| `payment_method` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `payment_failures` | `int64` | `numerical` | 0 | 0.0% | 6 | No | No | No |
| `discount_applied` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `price_increase_last_3m` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `support_tickets` | `int64` | `numerical` | 0 | 0.0% | 8 | No | No | No |
| `avg_resolution_time` | `float64` | `numerical` | 0 | 0.0% | 9883 | No | No | No |
| `complaint_type` | `str` | `categorical` | 2,045 | 20.45% | 4 | No | No | No |
| `csat_score` | `float64` | `numerical` | 0 | 0.0% | 5 | No | No | No |
| `escalations` | `int64` | `numerical` | 0 | 0.0% | 5 | No | No | No |
| `email_open_rate` | `float64` | `numerical` | 0 | 0.0% | 81 | No | No | No |
| `marketing_click_rate` | `float64` | `numerical` | 0 | 0.0% | 50 | No | No | No |
| `nps_score` | `int64` | `numerical` | 0 | 0.0% | 197 | No | No | No |
| `survey_response` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `referral_count` | `int64` | `numerical` | 0 | 0.0% | 8 | No | No | No |
| `churn` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `age` | 18.00 | 74.00 | 45.91 | 46.00 | 16.42 | 18.00 | 74.00 | 0 | 0 |
| `tenure_months` | 1.00 | 59.00 | 30.16 | 30.00 | 17.10 | 1.00 | 59.00 | 0 | 0 |
| `monthly_logins` | 0.00 | 54.00 | 19.67 | 20.00 | 9.84 | 0.00 | 43.00 | 299 | 0 |
| `weekly_active_days` | 0.00 | 7.00 | 3.48 | 3.00 | 2.30 | 0.00 | 7.00 | 1,322 | 0 |
| `avg_session_time` | 1.00 | 42.00 | 15.19 | 15.16 | 6.83 | 1.00 | 31.34 | 0 | 0 |
| `features_used` | 1.00 | 15.00 | 4.99 | 5.00 | 2.21 | 1.00 | 11.00 | 0 | 0 |
| `usage_growth_rate` | -0.58 | 0.54 | 0.02 | 0.02 | 0.15 | -0.33 | 0.38 | 291 | 4,345 |
| `last_login_days_ago` | 0.00 | 80.00 | 9.51 | 6.00 | 9.80 | 0.00 | 45.00 | 931 | 0 |
| `monthly_fee` | 10.00 | 100.00 | 34.93 | 30.00 | 23.79 | 10.00 | 100.00 | 0 | 0 |
| `total_revenue` | 10.00 | 5900.00 | 1057.02 | 720.00 | 1020.15 | 20.00 | 4800.00 | 0 | 0 |
| `payment_failures` | 0.00 | 5.00 | 0.50 | 0.00 | 0.71 | 0.00 | 3.00 | 6,084 | 0 |
| `support_tickets` | 0.00 | 7.00 | 1.21 | 1.00 | 1.10 | 0.00 | 4.00 | 3,012 | 0 |
| `avg_resolution_time` | 1.00 | 61.82 | 23.95 | 23.95 | 9.96 | 1.00 | 47.19 | 0 | 0 |
| `csat_score` | 1.00 | 5.00 | 3.49 | 4.00 | 0.98 | 1.00 | 5.00 | 0 | 0 |
| `escalations` | 0.00 | 4.00 | 0.29 | 0.00 | 0.54 | 0.00 | 2.00 | 7,445 | 0 |
| `email_open_rate` | 0.10 | 0.90 | 0.50 | 0.50 | 0.23 | 0.11 | 0.89 | 0 | 0 |
| `marketing_click_rate` | 0.01 | 0.50 | 0.25 | 0.25 | 0.14 | 0.02 | 0.49 | 0 | 0 |
| `nps_score` | -100.00 | 100.00 | 19.11 | 19.00 | 38.94 | -73.00 | 100.00 | 167 | 3,009 |
| `referral_count` | 0.00 | 7.00 | 0.99 | 1.00 | 0.99 | 0.00 | 4.00 | 3,704 | 0 |
| `churn` | 0.00 | 1.00 | 0.10 | 0.00 | 0.30 | 0.00 | 1.00 | 8,979 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
*No datetime columns found in this table.*

##### Categorical Column Distributions (Top 10 Values)

- **`customer_id`** (10000 unique): `CUST_00001`: 1, `CUST_00002`: 1, `CUST_00003`: 1, `CUST_00004`: 1, `CUST_00005`: 1...
- **`gender`** (2 unique): `Male`: 5,013, `Female`: 4,987...
- **`country`** (7 unique): `Bangladesh`: 1,494, `Canada`: 1,488, `USA`: 1,442, `India`: 1,427, `Australia`: 1,400...
- **`city`** (7 unique): `London`: 1,518, `Sydney`: 1,471, `Dhaka`: 1,459, `Delhi`: 1,402, `Berlin`: 1,386...
- **`customer_segment`** (3 unique): `Individual`: 5,984, `SME`: 3,029, `Enterprise`: 987...
- **`signup_channel`** (3 unique): `Web`: 5,036, `Mobile`: 2,960, `Referral`: 2,004...
- **`contract_type`** (3 unique): `Monthly`: 4,967, `Quarterly`: 3,050, `Yearly`: 1,983...
- **`payment_method`** (3 unique): `Card`: 5,955, `PayPal`: 2,557, `Bank Transfer`: 1,488...
- **`discount_applied`** (2 unique): `No`: 6,950, `Yes`: 3,050...
- **`price_increase_last_3m`** (2 unique): `No`: 8,055, `Yes`: 1,945...
- **`complaint_type`** (4 unique): `Technical`: 3,498, `Billing`: 2,427, `nan`: 2,045, `Service`: 2,030...
- **`survey_response`** (3 unique): `Satisfied`: 4,975, `Neutral`: 2,978, `Unsatisfied`: 2,047...

---

### Dataset: `customer_churn_dataset.csv`
- **Path**: `data/raw/customer_churn_dataset.csv`
- **File Size**: 1.55 MB (1,623,721 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 50,000 | **Max Columns**: 7
- **Provenance**: **SYNTHETIC** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **OPTIONAL**

#### Sheet/Table: `default` (50,000 rows, 7 cols, Duplicate Rows: 0)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `tenure_months` | `int64` | `numerical` | 0 | 0.0% | 59 | No | No | No |
| `monthly_usage_hours` | `float64` | `numerical` | 0 | 0.0% | 49998 | No | No | No |
| `has_multiple_devices` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |
| `customer_support_calls` | `int64` | `numerical` | 0 | 0.0% | 9 | No | Yes | No |
| `payment_failures` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |
| `is_premium_plan` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |
| `churn` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `tenure_months` | 1.00 | 59.00 | 30.03 | 30.00 | 17.00 | 1.00 | 59.00 | 0 | 0 |
| `monthly_usage_hours` | 0.00 | 38.73 | 20.00 | 20.03 | 5.00 | 8.37 | 31.60 | 3 | 0 |
| `has_multiple_devices` | 0.00 | 1.00 | 0.40 | 0.00 | 0.49 | 0.00 | 1.00 | 30,059 | 0 |
| `customer_support_calls` | 0.00 | 8.00 | 1.21 | 1.00 | 1.10 | 0.00 | 4.00 | 15,042 | 0 |
| `payment_failures` | 0.00 | 1.00 | 0.10 | 0.00 | 0.30 | 0.00 | 1.00 | 45,061 | 0 |
| `is_premium_plan` | 0.00 | 1.00 | 0.30 | 0.00 | 0.46 | 0.00 | 1.00 | 35,083 | 0 |
| `churn` | 0.00 | 1.00 | 0.02 | 0.00 | 0.14 | 0.00 | 1.00 | 48,967 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
*No datetime columns found in this table.*

##### Categorical Column Distributions (Top 10 Values)


---

### Dataset: `customer_subscription_churn_usage_patterns.csv`
- **Path**: `data/raw/customer_subscription_churn_usage_patterns.csv`
- **File Size**: 0.12 MB (126,307 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 2,800 | **Max Columns**: 10
- **Provenance**: **SYNTHETIC** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **OPTIONAL**

#### Sheet/Table: `default` (2,800 rows, 10 cols, Duplicate Rows: 0)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `user_id` | `int64` | `numerical` | 0 | 0.0% | 2800 | No | Yes | No |
| `signup_date` | `str` | `datetime` | 0 | 0.0% | 710 | No | No | No |
| `plan_type` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `monthly_fee` | `int64` | `monetary` | 0 | 0.0% | 3 | No | No | Yes |
| `avg_weekly_usage_hours` | `float64` | `numerical` | 0 | 0.0% | 246 | No | No | No |
| `support_tickets` | `int64` | `numerical` | 0 | 0.0% | 9 | No | No | No |
| `payment_failures` | `int64` | `numerical` | 0 | 0.0% | 6 | No | No | No |
| `tenure_months` | `int64` | `numerical` | 0 | 0.0% | 36 | No | No | No |
| `last_login_days_ago` | `int64` | `numerical` | 0 | 0.0% | 61 | No | No | No |
| `churn` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `user_id` | 1.00 | 2800.00 | 1400.50 | 1400.50 | 808.43 | 28.99 | 2772.01 | 0 | 0 |
| `monthly_fee` | 199.00 | 699.00 | 434.21 | 399.00 | 205.68 | 199.00 | 699.00 | 0 | 0 |
| `avg_weekly_usage_hours` | 0.50 | 25.00 | 12.89 | 12.80 | 7.11 | 0.70 | 24.70 | 0 | 0 |
| `support_tickets` | 0.00 | 8.00 | 3.89 | 4.00 | 2.61 | 0.00 | 8.00 | 345 | 0 |
| `payment_failures` | 0.00 | 5.00 | 2.49 | 2.00 | 1.69 | 0.00 | 5.00 | 442 | 0 |
| `tenure_months` | 1.00 | 36.00 | 18.61 | 18.00 | 10.37 | 1.00 | 36.00 | 0 | 0 |
| `last_login_days_ago` | 0.00 | 60.00 | 30.00 | 30.00 | 17.85 | 0.00 | 60.00 | 38 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `signup_date` | `2023-01-01 00:00:00` | `2024-12-31 00:00:00` | 730 days 00:00:00 |

##### Categorical Column Distributions (Top 10 Values)

- **`plan_type`** (3 unique): `Premium`: 944, `Standard`: 933, `Basic`: 923...
- **`churn`** (2 unique): `Yes`: 1,605, `No`: 1,195...

---

### Dataset: `online_retail_II.xlsx`
- **Path**: `data/raw/online_retail_II.xlsx`
- **File Size**: 43.51 MB (45,622,278 bytes)
- **Format**: `.xlsx` | **Sheets**: 2
- **Total Rows**: 1,067,371 | **Max Columns**: 8
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **SECONDARY**

#### Sheet/Table: `Year 2009-2010` (525,461 rows, 8 cols, Duplicate Rows: 6865)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `Invoice` | `object` | `categorical` | 0 | 0.0% | 28816 | No | Yes | No |
| `StockCode` | `object` | `categorical` | 0 | 0.0% | 4632 | No | Yes | No |
| `Description` | `object` | `categorical` | 2,928 | 0.5572% | 4682 | No | No | No |
| `Quantity` | `int64` | `numerical` | 0 | 0.0% | 825 | No | No | No |
| `InvoiceDate` | `datetime64[us]` | `datetime` | 0 | 0.0% | 25296 | No | Yes | No |
| `Price` | `float64` | `monetary` | 0 | 0.0% | 1606 | No | No | Yes |
| `Customer ID` | `float64` | `numerical` | 107,927 | 20.5395% | 4384 | No | Yes | No |
| `Country` | `str` | `categorical` | 0 | 0.0% | 40 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `Quantity` | -9600.00 | 19152.00 | 10.34 | 3.00 | 107.42 | -3.00 | 120.00 | 0 | 12,326 |
| `Price` | -53594.36 | 25111.09 | 4.69 | 2.10 | 146.13 | 0.21 | 19.95 | 3,687 | 3 |
| `Customer ID` | 12346.00 | 18287.00 | 15360.65 | 15311.00 | 1680.81 | 12435.00 | 18196.00 | 0 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `InvoiceDate` | `2009-12-01 07:45:00` | `2010-12-09 20:01:00` | 373 days 12:16:00 |

##### Categorical Column Distributions (Top 10 Values)

- **`Invoice`** (28816 unique): `537434`: 675, `538071`: 652, `537638`: 601, `537237`: 597, `536876`: 593...
- **`StockCode`** (4632 unique): `85123A`: 3,516, `22423`: 2,221, `85099B`: 2,057, `21212`: 1,933, `21232`: 1,843...
- **`Description`** (4682 unique): `WHITE HANGING HEART T-LIGHT HOLDER`: 3,549, `nan`: 2,928, `REGENCY CAKESTAND 3 TIER`: 2,212, `STRAWBERRY CERAMIC TRINKET BOX`: 1,843, `PACK OF 72 RETRO SPOT CAKE CASES`: 1,466...
- **`Country`** (40 unique): `United Kingdom`: 485,852, `EIRE`: 9,670, `Germany`: 8,129, `France`: 5,772, `Netherlands`: 2,769...

#### Sheet/Table: `Year 2010-2011` (541,910 rows, 8 cols, Duplicate Rows: 5268)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `Invoice` | `object` | `categorical` | 0 | 0.0% | 25900 | No | Yes | No |
| `StockCode` | `object` | `categorical` | 0 | 0.0% | 4070 | No | Yes | No |
| `Description` | `object` | `categorical` | 1,454 | 0.2683% | 4224 | No | No | No |
| `Quantity` | `int64` | `numerical` | 0 | 0.0% | 722 | No | No | No |
| `InvoiceDate` | `datetime64[us]` | `datetime` | 0 | 0.0% | 23260 | No | Yes | No |
| `Price` | `float64` | `monetary` | 0 | 0.0% | 1630 | No | No | Yes |
| `Customer ID` | `float64` | `numerical` | 135,080 | 24.9266% | 4373 | No | Yes | No |
| `Country` | `str` | `categorical` | 0 | 0.0% | 38 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `Quantity` | -80995.00 | 80995.00 | 9.55 | 3.00 | 218.08 | -2.00 | 100.00 | 0 | 10,624 |
| `Price` | -11062.06 | 38970.00 | 4.61 | 2.08 | 96.76 | 0.19 | 18.00 | 2,515 | 2 |
| `Customer ID` | 12346.00 | 18287.00 | 15287.68 | 15152.00 | 1713.60 | 12415.00 | 18212.00 | 0 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `InvoiceDate` | `2010-12-01 08:26:00` | `2011-12-09 12:50:00` | 373 days 04:24:00 |

##### Categorical Column Distributions (Top 10 Values)

- **`Invoice`** (25900 unique): `573585`: 1,114, `581219`: 749, `581492`: 731, `580729`: 721, `558475`: 705...
- **`StockCode`** (4070 unique): `85123A`: 2,313, `22423`: 2,203, `85099B`: 2,159, `47566`: 1,727, `20725`: 1,639...
- **`Description`** (4224 unique): `WHITE HANGING HEART T-LIGHT HOLDER`: 2,369, `REGENCY CAKESTAND 3 TIER`: 2,200, `JUMBO BAG RED RETROSPOT`: 2,159, `PARTY BUNTING`: 1,727, `LUNCH BAG RED RETROSPOT`: 1,638...
- **`Country`** (38 unique): `United Kingdom`: 495,478, `Germany`: 9,495, `France`: 8,558, `EIRE`: 8,196, `Spain`: 2,533...

---

### Dataset: `online_shoppers_intention.csv`
- **Path**: `data/raw/online_shoppers_intention.csv`
- **File Size**: 1.02 MB (1,072,063 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 12,330 | **Max Columns**: 18
- **Provenance**: **REAL** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **CORE**

#### Sheet/Table: `default` (12,330 rows, 18 cols, Duplicate Rows: 125)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `Administrative` | `int64` | `numerical` | 0 | 0.0% | 27 | No | No | No |
| `Administrative_Duration` | `float64` | `numerical` | 0 | 0.0% | 3335 | No | No | No |
| `Informational` | `int64` | `numerical` | 0 | 0.0% | 17 | No | No | No |
| `Informational_Duration` | `float64` | `numerical` | 0 | 0.0% | 1258 | No | No | No |
| `ProductRelated` | `int64` | `numerical` | 0 | 0.0% | 311 | No | No | No |
| `ProductRelated_Duration` | `float64` | `numerical` | 0 | 0.0% | 9551 | No | No | No |
| `BounceRates` | `float64` | `numerical` | 0 | 0.0% | 1872 | No | No | No |
| `ExitRates` | `float64` | `numerical` | 0 | 0.0% | 4777 | No | No | No |
| `PageValues` | `float64` | `monetary` | 0 | 0.0% | 2704 | No | No | Yes |
| `SpecialDay` | `float64` | `numerical` | 0 | 0.0% | 6 | No | No | No |
| `Month` | `str` | `categorical` | 0 | 0.0% | 10 | No | No | No |
| `OperatingSystems` | `int64` | `numerical` | 0 | 0.0% | 8 | No | No | No |
| `Browser` | `int64` | `numerical` | 0 | 0.0% | 13 | No | No | No |
| `Region` | `int64` | `numerical` | 0 | 0.0% | 9 | No | No | No |
| `TrafficType` | `int64` | `numerical` | 0 | 0.0% | 20 | No | No | No |
| `VisitorType` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `Weekend` | `bool` | `boolean` | 0 | 0.0% | 2 | No | No | No |
| `Revenue` | `bool` | `boolean` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `Administrative` | 0.00 | 27.00 | 2.32 | 1.00 | 3.32 | 0.00 | 14.00 | 5,768 | 0 |
| `Administrative_Duration` | 0.00 | 3398.75 | 80.82 | 7.50 | 176.78 | 0.00 | 830.59 | 5,903 | 0 |
| `Informational` | 0.00 | 24.00 | 0.50 | 0.00 | 1.27 | 0.00 | 6.00 | 9,699 | 0 |
| `Informational_Duration` | 0.00 | 2549.38 | 34.47 | 0.00 | 140.75 | 0.00 | 716.39 | 9,925 | 0 |
| `ProductRelated` | 0.00 | 705.00 | 31.73 | 18.00 | 44.48 | 1.00 | 221.00 | 38 | 0 |
| `ProductRelated_Duration` | 0.00 | 63973.52 | 1194.75 | 598.94 | 1913.67 | 0.00 | 8701.14 | 755 | 0 |
| `BounceRates` | 0.00 | 0.20 | 0.02 | 0.00 | 0.05 | 0.00 | 0.20 | 5,518 | 0 |
| `ExitRates` | 0.00 | 0.20 | 0.04 | 0.03 | 0.05 | 0.00 | 0.20 | 76 | 0 |
| `PageValues` | 0.00 | 361.76 | 5.89 | 0.00 | 18.57 | 0.00 | 85.50 | 9,600 | 0 |
| `SpecialDay` | 0.00 | 1.00 | 0.06 | 0.00 | 0.20 | 0.00 | 1.00 | 11,079 | 0 |
| `OperatingSystems` | 1.00 | 8.00 | 2.12 | 2.00 | 0.91 | 1.00 | 4.00 | 0 | 0 |
| `Browser` | 1.00 | 13.00 | 2.36 | 2.00 | 1.72 | 1.00 | 10.00 | 0 | 0 |
| `Region` | 1.00 | 9.00 | 3.15 | 3.00 | 2.40 | 1.00 | 9.00 | 0 | 0 |
| `TrafficType` | 1.00 | 20.00 | 4.07 | 2.00 | 4.03 | 1.00 | 20.00 | 0 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
*No datetime columns found in this table.*

##### Categorical Column Distributions (Top 10 Values)

- **`Month`** (10 unique): `May`: 3,364, `Nov`: 2,998, `Mar`: 1,907, `Dec`: 1,727, `Oct`: 549...
- **`VisitorType`** (3 unique): `Returning_Visitor`: 10,551, `New_Visitor`: 1,694, `Other`: 85...
- **`Weekend`** (2 unique): `False`: 9,462, `True`: 2,868...
- **`Revenue`** (2 unique): `False`: 10,422, `True`: 1,908...

---

### Dataset: `synthetic_fraud_data.csv`
- **Path**: `data/raw/synthetic_fraud_data.csv`
- **File Size**: 2798.3 MB (2,934,232,016 bytes)
- **Format**: `.csv` | **Sheets**: 1
- **Total Rows**: 7,483,766 | **Max Columns**: 24
- **Provenance**: **SYNTHETIC** (Verified from schema structures & published benchmark sources)
- **Track 03 Role**: **EXCLUDE**

#### Sheet/Table: `default` (7,483,766 rows, 24 cols, Duplicate Rows: Not computed for >1M rows)

| Column Name | Dtype | Inferred Type | Missing Count | Missing % | Unique Count | Constant? | Identifier? | Monetary? |
|---|---|---|---|---|---|---|---|---|
| `transaction_id` | `str` | `categorical` | 0 | 0.0% | >5000 | No | Yes | No |
| `customer_id` | `str` | `categorical` | 0 | 0.0% | 4869 | No | Yes | No |
| `card_number` | `int64` | `numerical` | 0 | 0.0% | >5000 | No | No | No |
| `timestamp` | `str` | `datetime` | 0 | 0.0% | >5000 | No | No | No |
| `merchant_category` | `str` | `categorical` | 0 | 0.0% | 8 | No | No | No |
| `merchant_type` | `str` | `categorical` | 0 | 0.0% | 17 | No | No | No |
| `merchant` | `str` | `categorical` | 0 | 0.0% | 105 | No | No | No |
| `amount` | `float64` | `monetary` | 0 | 0.0% | >5000 | No | No | Yes |
| `currency` | `str` | `categorical` | 0 | 0.0% | 11 | No | No | No |
| `country` | `str` | `categorical` | 0 | 0.0% | 12 | No | No | No |
| `city` | `str` | `categorical` | 0 | 0.0% | 11 | No | No | No |
| `city_size` | `str` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `card_type` | `str` | `categorical` | 0 | 0.0% | 5 | No | No | No |
| `card_present` | `bool` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `device` | `str` | `categorical` | 0 | 0.0% | 9 | No | No | No |
| `channel` | `str` | `categorical` | 0 | 0.0% | 3 | No | No | No |
| `device_fingerprint` | `str` | `categorical` | 0 | 0.0% | >5000 | No | No | No |
| `ip_address` | `str` | `categorical` | 0 | 0.0% | >5000 | No | No | No |
| `distance_from_home` | `int64` | `numerical` | 0 | 0.0% | 2 | No | No | No |
| `high_risk_merchant` | `bool` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `transaction_hour` | `int64` | `numerical` | 0 | 0.0% | 24 | No | No | No |
| `weekend_transaction` | `bool` | `categorical` | 0 | 0.0% | 2 | No | No | No |
| `velocity_last_hour` | `str` | `categorical` | 0 | 0.0% | >5000 | No | No | No |
| `is_fraud` | `bool` | `categorical` | 0 | 0.0% | 2 | No | No | No |

##### Numerical Column Summary Statistics

| Column Name | Min | Max | Mean | Median | Std | 1st %ile | 99th %ile | Zeros | Negatives |
|---|---|---|---|---|---|---|---|---|---|
| `card_number` | 370008611452264.00 | 6999728403598762.00 | 12048227375470.03 | 5003432175155325.00 | 0.00 | 370370684457780.00 | 6962814808072968.00 | 0 | 0 |
| `amount` | 0.01 | 6253152.62 | 47924.68 | 1176.32 | 177556.17 | 3.61 | 795111.34 | 0 | 0 |
| `distance_from_home` | 0.00 | 1.00 | 0.32 | 0.00 | 0.47 | 0.00 | 1.00 | 5,073,605 | 0 |
| `transaction_hour` | 0.00 | 23.00 | 12.15 | 12.00 | 6.54 | 0.00 | 23.00 | 155,759 | 0 |

##### Datetime Column Profile

| Column Name | Min Timestamp | Max Timestamp | Temporal Coverage |
|---|---|---|---|
| `timestamp` | `2024-09-30 00:00:03.149440+00:00` | `2024-10-06 06:25:29.021605+00:00` | 6 days 06:25:25.872165 |

##### Categorical Column Distributions (Top 10 Values)

- **`transaction_id`** (N/A unique): `TX_d1d57fce`: 1, `TX_66be7556`: 1, `TX_58a2a1fb`: 1, `TX_56517e39`: 1, `TX_d2ae57e6`: 1...
- **`customer_id`** (N/A unique): `CUST_64957`: 22, `CUST_24822`: 20, `CUST_71592`: 19, `CUST_37392`: 19, `CUST_98661`: 19...
- **`merchant_category`** (N/A unique): `Education`: 3,843, `Healthcare`: 3,809, `Travel`: 3,742, `Entertainment`: 3,740, `Gas`: 3,730...
- **`merchant_type`** (N/A unique): `online`: 5,714, `physical`: 3,618, `supplies`: 1,923, `major`: 1,911, `medical`: 1,910...
- **`merchant`** (N/A unique): `Barnes & Noble`: 663, `Chegg`: 639, `University Bookstore`: 621, `Highway Gas Stop`: 619, `Truck Stop`: 601...
- **`currency`** (N/A unique): `EUR`: 4,333, `NGN`: 3,446, `MXN`: 3,284, `RUB`: 3,241, `BRL`: 3,190...
- **`country`** (N/A unique): `Nigeria`: 3,446, `Mexico`: 3,284, `Russia`: 3,241, `Brazil`: 3,190, `Singapore`: 2,392...
- **`city`** (N/A unique): `Unknown City`: 28,007, `San Diego`: 231, `Chicago`: 214, `New York`: 208, `Phoenix`: 204...
- **`city_size`** (N/A unique): `medium`: 29,206, `large`: 794...
- **`card_type`** (N/A unique): `Premium Debit`: 6,326, `Basic Debit`: 6,183, `Platinum Credit`: 6,147, `Gold Credit`: 5,708, `Basic Credit`: 5,636...
- **`card_present`** (N/A unique): `False`: 27,273, `True`: 2,727...
- **`device`** (N/A unique): `Edge`: 4,665, `Safari`: 4,600, `Chrome`: 4,524, `iOS App`: 4,522, `Android App`: 4,483...
- **`channel`** (N/A unique): `web`: 18,268, `mobile`: 9,005, `pos`: 2,727...
- **`device_fingerprint`** (N/A unique): `707fe93fa58cfe069c0775dce47e811a`: 15, `5f6056a0d2987f2cd4aa97a97516041a`: 15, `fd06964cac93a4d2c8b10068d31d49f7`: 14, `ac293731aff6ec240f7c5e0356c44468`: 13, `edbf19047f219064dc01974a40f85536`: 12...
- **`ip_address`** (N/A unique): `147.196.157.131`: 1, `122.173.63.27`: 1, `96.111.215.125`: 1, `209.97.34.175`: 1, `58.142.250.43`: 1...
- **`high_risk_merchant`** (N/A unique): `False`: 22,518, `True`: 7,482...
- **`weekend_transaction`** (N/A unique): `False`: 24,131, `True`: 5,869...
- **`velocity_last_hour`** (N/A unique): `{'num_transactions': 676, 'total_amount': 40250796.4768046, 'unique_merchants': 102, 'unique_countries': 12, 'max_single_amount': 3085041.480786325}`: 1, `{'num_transactions': 653, 'total_amount': 16734481.101362588, 'unique_merchants': 104, 'unique_countries': 12, 'max_single_amount': 2242044.155787199}`: 1, `{'num_transactions': 613, 'total_amount': 22456818.6225144, 'unique_merchants': 104, 'unique_countries': 12, 'max_single_amount': 2122146.2045335835}`: 1, `{'num_transactions': 392, 'total_amount': 13634246.837629719, 'unique_merchants': 101, 'unique_countries': 12, 'max_single_amount': 3157907.895797551}`: 1, `{'num_transactions': 91, 'total_amount': 1676271.626143774, 'unique_merchants': 57, 'unique_countries': 12, 'max_single_amount': 486755.3649971946}`: 1...
- **`is_fraud`** (N/A unique): `False`: 23,699, `True`: 6,301...

---
