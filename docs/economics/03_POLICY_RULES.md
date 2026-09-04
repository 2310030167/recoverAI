# RecoverAI Economics — Deterministic Policy Rules & Constraints

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Policy vs ML Separation

- **ML & Economics**: Predict probabilities and evaluate expected net financial value $\Delta E$.
- **Policy Engine**: Enforces hard business constraints, regulatory rules, and customer protection.

---

## 2. Policy Constraint Taxonomy

1. **Disputed Invoice Protection**: `is_disputed == True` $ightarrow$ Blocks automated `REMINDER` and `RETRY`. Permits `ESCALATE` or `NO_ACTION`.
2. **Customer Opt-Out Protection**: `is_opted_out == True` $ightarrow$ Blocks `REMINDER` and `RETRY`.
3. **Intervention Cooldown**: `hours_since_last_intervention < 24.0h` $ightarrow$ Blocks all active actions during active cooldown.
4. **Retry Cap**: `retry_count >= 3` $ightarrow$ Blocks further automated `RETRY`.
5. **Total Interventions Cap**: `total_interventions >= 5` $ightarrow$ Blocks further interventions.
6. **Minimum Value Threshold**: Requires $\Delta E > 0.00$ for non-`NO_ACTION` interventions.
