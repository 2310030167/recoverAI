# RecoverAI Simulator — Operational Timeline & Recovery Windows

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  

---

## 1. Configurable Operational Horizons

The simulator progresses daily from $T_0$ (Due Date) up to 30 days, reporting recovery status across three distinct operational horizons:

1. **3-Day Horizon (Primary Operational Recovery Window)**: Early intervention window capturing fast self-cures and immediate reminder responses.
2. **7-Day Horizon (Secondary Operational Recovery Window)**: Mid-stage follow-up window.
3. **30-Day Horizon (Macro Recovery Horizon)**: Long-term macro resolution horizon.

---

## 2. Deterministic Stopping Rules

Intervention attempts for an opportunity immediately cease when:
- **Recovery Occurs**: Invoice paid ($S_{	ext{status}} = 	ext{RECOVERED}$).
- **Window Expiry**: 30-day macro horizon reached ($T > T_0 + 30$).
- **Policy Cap**: Retry limit (3 retries) or total intervention cap (5 interventions) reached.
- **Customer Protection**: Invoice disputed or customer opted out.
- **Negative EV**: Expected incremental revenue $\Delta E \le 0.00$.
