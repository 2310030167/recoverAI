# RecoverAI — Local Execution & Demonstration Guide

> **Project**: RecoverAI (Razorpay AI Buildathon Track 03 — AI Revenue Recovery)  
> **Repository Root**: `D:\recoverai`  

---

## 1. Prerequisites & Environment Verification

Before running RecoverAI locally, ensure the following verified tools are installed:

- **Python Version**: `Python 3.11.9 (64-bit)`
- **Node.js & npm**: `Node.js v25.3.0` | `npm v11.18.0`
- **Docker Desktop** *(Optional)*: Required only if running PostgreSQL & Redis in Docker containers.

---

## 2. Port Availability Verification

RecoverAI uses the following default local ports:
- **Backend API**: `http://127.0.0.1:8000`
- **Frontend SPA Command Center**: `http://127.0.0.1:5173`

### How to Check Port Occupancy (Windows PowerShell):
```powershell
Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess, State
```

### How to Identify Process Name by PID:
```powershell
Get-Process -Id <PID>
```

### How to Kill an Occupying Process (If Necessary):
```powershell
Stop-Process -Id <PID> -Force
```

---

## 3. Database & Redis Services (Optional Docker Setup)

RecoverAI operates out of the box in **standalone empirical dataset mode** without mandatory database containers.

If live PostgreSQL and Redis services are desired:
```powershell
cd D:\recoverai
docker-compose up -d postgres redis
```

---

## 4. Backend Startup Command

Open a new terminal at `D:\recoverai\backend` and run:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Frontend Startup Command

Open a second terminal at `D:\recoverai\frontend` and run:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 6. Health & Endpoint Verification Commands

Once both services are running, verify the backend endpoints:

### Power Shell / Command Line:
```powershell
# Root Health Check
curl http://127.0.0.1:8000/health

# API v1 Health Check
curl http://127.0.0.1:8000/api/v1/health

# Detailed Health Check (Database / Redis Status)
curl http://127.0.0.1:8000/api/v1/health/detailed

# Empirical Opportunity Queue Endpoint
curl http://127.0.0.1:8000/api/v1/opportunities
```

---

## 7. Service Shutdown Commands

To stop services:
- **Backend Terminal**: Press `Ctrl + C`
- **Frontend Terminal**: Press `Ctrl + C`
- **Docker Containers** *(If running)*: `docker-compose down`

---

## 8. Manual Demonstration Sequence (60–90 Second Pitch Flow)

1. Open `http://127.0.0.1:5173` in a web browser.
2. Observe the **Hero Money Section**: `TOTAL PORTFOLIO EXPOSURE` & `PROJECTED RECOVERABLE`.
3. Navigate to **Recovery Horizon** tab: Observe overdue opportunities grouped by `3d` (Primary), `7d` (Secondary), and `30d` (Macro) windows. Hover over any card for detailed inspection.
4. Navigate to **Recovery Universe** tab: Observe the **Map of Money at Risk** canvas (Node Size = Exposure Amount, Position = Overdue Age & Baseline Settlement P(R)).
5. Click any node in the Recovery Universe or an item in the **Opportunities Queue**: Inspect the **8-Step Decision Trace Pipeline** (`01 DETECT` $\to$ `08 CLOSE`) explaining why RecoverAI chose the optimal action.
6. Open **Economic What-If Simulator**: Drag sensitivity sliders to stress-test net EV $\Delta E$ and watch the waterfall bar chart update dynamically.
7. Open **Opportunity Detail Modal**: Click **Execute in TEST MODE** to call `RazorpayTestModeProvider` and observe the animated recovery outcome.
