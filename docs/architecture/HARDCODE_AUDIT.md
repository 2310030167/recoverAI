# RecoverAI Architecture — Hardcode Audit & Data Grounding

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Discovered Values & Classifications

| Parameter / Discovered Value | Module / File Location | Classification | Source / Grounding |
|---|---|---|---|
| **Natural Recovery $P(R \mid X, A=0)$** | `ml/pipeline.py`, `data_loader.py` | **A. EMPIRICALLY DERIVED** | Derived from non-censored decile historical payment settlement rates in `Customer Invoices Dataset.csv` |
| **Historical Customer Late Rate & Delay** | `ml/features/pipeline.py` | **A. EMPIRICALLY DERIVED** | Point-in-time calculation from customer invoice payment history |
| **Observation End Cutoff $T_{\text{obs\_end}}$ (2020-05-22)** | `ml/pipeline.py` | **A. EMPIRICALLY DERIVED** | Derived from max dataset payment snapshot date to eliminate right-censoring leakage |
| **Cooldown Hours (24.0h)** | `app/core/config.py`, `PolicyEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.cooldown_hours`. Replaces inline literals. |
| **Max Retry Attempts (3 retries)** | `app/core/config.py`, `PolicyEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.max_retry_attempts`. Replaces inline literals. |
| **Max Total Interventions (5 cap)** | `app/core/config.py`, `PolicyEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.max_interventions`. Replaces inline literals. |
| **Macro Horizon Days (30d)** | `app/core/config.py`, `SimulatorEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.macro_horizon_days`. Replaces inline literals. |
| **Primary Operational Window (3d)** | `app/core/config.py`, `SimulatorEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.primary_window_days`. Replaces inline literals. |
| **Secondary Operational Window (7d)** | `app/core/config.py`, `SimulatorEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.secondary_window_days`. Replaces inline literals. |
| **Escalation Thresholds (₹100k, 14d)** | `app/core/config.py`, `PolicyEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.escalation_amount_threshold`. |
| **Intervention Direct Costs (₹0.50, ₹2.00, ₹50.00)** | `app/core/config.py`, `EconomicEngine` | **B. DATA-CONFIGURED** | Centralized setting `settings.recovery.action_costs`. Based on Indian SaaS vendor rates. |
| **NO_ACTION Safety Exemption** | `PolicyEngine`, `ActionValidator` | **C. SYSTEM SAFETY** | NO_ACTION baseline is always permitted; zero cost, zero risk. |
| **Provider Timeout (3000ms)** | `app/core/config.py`, `provider.py` | **C. SYSTEM SAFETY** | Infrastructure safeguard setting `settings.execution.provider_timeout_ms`. |
| **Action Treatment Multipliers (1.20x, 1.35x, 1.15x)** | `app/core/config.py`, `TreatmentEstimator` | **D. SIMULATION ASSUMPTION** | Centralized setting `settings.recovery.action_multipliers`. Tagged explicitly as `SIMULATION_ASSUMPTION`. |
| **Inline Magic Literals** | *Various (REMOVED)* | **E. INVALID HARDCODE** | Removed inline literals in `PolicyEngine`, `EconomicEngine`, `SimulatorEngine`. Centralized in `config.py`. |

---

## 2. Data Lineage Metadata System

Every economic, policy, or treatment calculation returns explicit data lineage metadata:
- `EMPIRICAL`: Directly computed from dataset records.
- `DERIVED`: Computed via mathematical formulas from empirical inputs.
- `CONFIGURED`: Resolved from centralized application settings `settings.recovery`.
- `SIMULATION_ASSUMPTION`: Clearly labeled simulation parameters for treatment uplift.
- `SYSTEM_SAFETY`: Built-in safety rules (e.g., NO_ACTION exemption).

---

## 3. Explicit Error Statuses (No Silent Fallbacks)

If required empirical inputs are missing or invalid, system modules return explicit statuses rather than silent fallbacks:
- `DATA_UNAVAILABLE`
- `TREATMENT_ESTIMATE_UNAVAILABLE`
- `CONFIGURATION_REQUIRED`
