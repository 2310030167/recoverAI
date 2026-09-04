# RecoverAI ML — Corrected Model Evaluation & Base Rate Analysis

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Empirical Model Performance Comparison

### Validation Set Performance (`2019-12-01` to `2020-01-31`)
- **Majority-Class Baseline Accuracy**: **98.89%**

| Model Architecture | Accuracy | Precision | Recall | F1 Score | ROC-AUC | PR-AUC | Brier Score Loss | Log Loss |
|---|---|---|---|---|---|---|---|---|
| **Logistic Regression Baseline** | 0.3000 | **1.0000** | 0.2921 | 0.4522 | **0.9646** | **0.9996** | 0.3643 | 1.0077 |
| **HistGradientBoosting (Tabular)** | **0.6971** | 0.9990 | **0.6944** | **0.8193** | 0.9409 | 0.9990 | **0.1878** | **0.5484** |

---

### Test Set Performance (`2020-02-01` to `2020-06-07`)
- **Majority-Class Baseline Accuracy**: **61.23%**

| Model Architecture | Accuracy | Precision | Recall | F1 Score | ROC-AUC | PR-AUC | Brier Score Loss |
|---|---|---|---|---|---|---|---|
| **Logistic Regression Baseline** | **0.5675** | 0.3588 | 0.1469 | 0.2085 | 0.4173 | 0.3546 | **0.2843** |
| **HistGradientBoosting (Tabular)** | 0.4498 | **0.3767** | **0.6403** | **0.4743** | **0.4562** | **0.3496** | 0.3895 |
