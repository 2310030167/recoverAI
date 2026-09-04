# RecoverAI Economics — Decision Explanation Examples

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Example 1: Positive EV Reminder Selected

```json
{
  "opportunity_id": "OPP_INVOICE_9001",
  "selected_action": "REMINDER",
  "decision_reason": "Selected REMINDER: Highest policy-eligible expected incremental revenue (+₹1,999.50) after ₹0.50 cost.",
  "amount": 10000.0,
  "natural_probability": 0.30,
  "assisted_probability": 0.50,
  "incremental_probability": 0.20,
  "intervention_cost": 0.50,
  "expected_incremental_revenue": 1999.50,
  "policy_status": "ELIGIBLE",
  "candidate_evaluations": [
    {
      "action": "NO_ACTION",
      "treatment_source": "NATURAL_RECOVERY_BASELINE",
      "natural_probability": 0.30,
      "assisted_probability": 0.30,
      "incremental_probability": 0.0,
      "intervention_cost": 0.0,
      "expected_incremental_revenue": 0.0,
      "is_positive_ev": false,
      "policy_status": "ELIGIBLE",
      "policy_reasons": ["NO_ACTION baseline is always policy permitted."],
      "is_eligible": true
    },
    {
      "action": "REMINDER",
      "treatment_source": "CONFIGURED_BOUNDED_MULTIPLIER",
      "natural_probability": 0.30,
      "assisted_probability": 0.50,
      "incremental_probability": 0.20,
      "intervention_cost": 0.50,
      "expected_incremental_revenue": 1999.50,
      "is_positive_ev": true,
      "policy_status": "ELIGIBLE",
      "policy_reasons": ["All policy constraints satisfied."],
      "is_eligible": true
    }
  ],
  "timestamp": "2026-08-23T20:40:00Z"
}
```

---

## 2. Example 2: Disputed Invoice Policy Block -> NO_ACTION Fallback

```json
{
  "opportunity_id": "OPP_DISPUTED_102",
  "selected_action": "NO_ACTION",
  "decision_reason": "Selected NO_ACTION: No alternative intervention yielded positive policy-eligible incremental economic value.",
  "amount": 100.0,
  "natural_probability": 0.30,
  "assisted_probability": 0.30,
  "incremental_probability": 0.0,
  "intervention_cost": 0.0,
  "expected_incremental_revenue": 0.0,
  "policy_status": "ELIGIBLE"
}
```
