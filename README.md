# RecoverAI — AI Revenue Recovery Platform

> Built for **Razorpay AI Buildathon Track 03 — AI Revenue Recovery**

RecoverAI is an intelligent revenue recovery engine designed to detect revenue at risk, diagnose root causes (checkout drop-off, payment failure, invoice delinquency), estimate natural vs intervention-assisted recovery probabilities, select economically bounded interventions, and measure incremental revenue recovered.

---

## 📂 Repository Structure

```
recoverai/
├── backend/            # FastAPI modular backend foundation
│   ├── app/            # Application core, API routers, models, schemas
│   ├── tests/          # Pytest suite
│   ├── alembic/        # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/           # Web UI application layer
├── data/               # Raw datasets, manifests & processed data stores
│   ├── raw/            # Audited raw datasets (Read-Only)
│   └── dataset_manifest.json
├── ml/                 # Machine Learning model training & feature pipelines
├── simulator/          # Payment retry & recovery simulation engine
├── docs/               # Data engineering audits & system documentation
│   └── data/           # 7 Data Audit Markdown Reports
├── scripts/            # Helper scripts & CLI utilities
├── tests/              # End-to-End test suites
├── docker/             # Docker infrastructure files
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
├── docker-compose.yml  # Multi-container orchestration (PostgreSQL + Redis + Backend)
└── README.md           # Project Root Overview
```

---

## ⚡ Quickstart

### 1. Launch Infrastructure Services

```bash
docker-compose up -d
```

This starts PostgreSQL 16 on port `5432` and Redis 7 on port `6379`.

### 2. Run Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Verify backend health at: `http://localhost:8000/health`

### 3. Run Automated Tests

```bash
cd backend
pytest
```
