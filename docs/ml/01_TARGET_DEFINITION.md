# RecoverAI ML — Corrected Target Definition & Censoring Audit

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  
> **Phase**: Corrective ML Validation Phase  

---

## 1. Censoring Classification & Target Construction

To resolve right-censoring in revenue recovery data where late invoices have not completed their observation window, observations are classified as:

$$\text{Censoring Status} = \begin{cases} 
\text{OBSERVABLE\_POSITIVE} & \text{if } T_{\text{clear}} \text{ is present and } (T_{\text{clear}} - T_{\text{due}}) \le 30 \text{ days} \implies y = 1 \\
\text{OBSERVABLE\_NEGATIVE} & \text{if cleared after 30d OR } (T_{\text{clear}} \text{ is NaT AND } T_{\text{due}} + 30 \le T_{\text{obs\_end}}) \implies y = 0 \\
\text{RIGHT\_CENSORED} & \text{if } T_{\text{clear}} \text{ is NaT AND } T_{\text{due}} + 30 > T_{\text{obs\_end}} \implies y = \text{CENSORED } (-1)
\end{cases}$$

- **Effective Observation End Date ($T_{\text{obs\_end}}$)**: **2020-05-22** (Latest clearing event in dataset snapshot).
- **$y = 1$**: Cleared within 30 days of due date.
- **$y = 0$**: Full 30-day window observed without clearance.
- **$y = -1$**: Excluded from supervised training and test evaluation to eliminate right-censoring bias.
