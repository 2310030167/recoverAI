# RecoverAI Economics — Bounded Economic Model

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Incremental Economic Revenue Formula

RecoverAI evaluates interventions strictly on expected incremental financial value ($\Delta E$).

$$\Delta p = P(R \mid X, A=k) - P(R \mid X, A=0)$$

$$\Delta E = 	ext{Amount} 	imes \Delta p - 	ext{intervention\_cost}$$

Where:
- **$	ext{Amount}$**: Invoice / opportunity monetary exposure at risk (INR).
- **$P(R \mid X, A=0)$**: Natural recovery probability without intervention. `[OBSERVATIONAL / EMPIRICAL]`
- **$P(R \mid X, A=k)$**: Assisted recovery probability under candidate action $k$. `[CONFIGURED / SIMULATED]`
- **$\Delta p$**: Incremental recovery uplift.
- **$	ext{intervention\_cost}$**: Direct operational cost of executing action $k$. `[EMPIRICAL]`
- **$\Delta E$**: Expected net incremental revenue gain.

---

## 2. Decision Threshold Rule

Select action $A^*$ maximizing $\Delta E$ subject to deterministic policy constraints:

$$A^* = rg\max_{A_k \in 	ext{Eligible}(A)} \Delta E(A_k)$$

If no candidate action satisfies $\Delta E > 0$ and $	ext{PolicyPermitted}(A_k)$, the system selects **`NO_ACTION`**.
