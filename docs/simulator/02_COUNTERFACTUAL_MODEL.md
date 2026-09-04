# RecoverAI Simulator — 4-Way Counterfactual Trajectory Model

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Parallel Trajectory Simulation Engine

For each recovery opportunity, `CounterfactualEngine` evaluates 4 parallel potential trajectories from the **identical initial state $S_0$**:

1. **Trajectory A (`NO_ACTION`)**: Natural recovery baseline. Zero intervention cost.
2. **Trajectory B (`REMINDER`)**: Automated SMS/WhatsApp reminder. ₹0.50 cost.
3. **Trajectory C (`RETRY`)**: Payment gateway retry execution. ₹2.00 cost.
4. **Trajectory D (`ESCALATE`)**: Manual ops agent escalation. ₹50.00 cost.

---

## 2. Scientific Disclaimer

This counterfactual analysis evaluates simulated potential trajectories under controlled mathematical models. It is **NOT** an empirical causal inference claim derived from randomized A/B experiment logs.
