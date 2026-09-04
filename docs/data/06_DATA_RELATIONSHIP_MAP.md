# RecoverAI Data Engineering — Entity Relationship & Data Linkage Map

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)
> **Objective**: Map entity keys across datasets to construct unified RecoverAI customer feature store.

## Dataset Entity Key Compatibility Matrix

| Dataset Name | Entity Keys Available | Primary Key Type | Linkage Compatibility |
|---|---|---|---|
| `WA_Fn-UseC_-Accounts-Receivable.csv` | `customerID`, `invoiceNumber` | B2B Customer / Invoice Key | Joinable with `Customer Invoices Dataset.csv` on customer ID hashing or domain matching |
| `customer_churn_business_dataset.csv` | `customer_id`, `company_name` | B2B SaaS Customer Key | Primary anchor for B2B customer state and subscription health features |
| `Customer Invoices Dataset.csv` | `cust_number`, `invoice_id`, `doc_id` | SAP Enterprise Invoice Key | Joins invoice amounts, payment terms, and open balances to customer profile |
| `online_shoppers_intention.csv` | Session Index (Implicit) | E-commerce Session Key | Maps session funnel behavior (Bounce, Exit) to checkout risk simulator |
| `UPI_transactions.csv` | `Transaction ID`, `Sender Name` | Indian UPI Transaction Key | Maps UPI payment failure modes to Indian payment context simulator |
| `Online Retail.xlsx` | `CustomerID`, `InvoiceNo` | Retail Customer / Order Key | Aggregates historical transaction sequence & order size per customer |

---

## Unified RecoverAI Architecture Diagram

```
                        +---------------------------------------+
                        |       RecoverAI Customer Feature      |
                        |            Store / Entity             |
                        +-------------------+-------------------+
                                            |
         +------------------+---------------+---------------+------------------+
         |                  |                               |                  |
  +------v------+    +------v------+                 +------v------+    +------v------+
  | Accounts    |    | B2B SaaS    |                 | Checkout    |    | Indian UPI  |
  | Receivables |    | Subscription|                 | Session Log |    | Payment Log |
  | (IBM AR /   |    | (Churn &    |                 | (UCI        |    | (UPI Trans) |
  | SAP Inv)    |    | Health)     |                 | Shoppers)   |    |             |
  +-------------+    +-------------+                 +-------------+    +-------------+
```