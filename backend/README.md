# RecoverAI Backend API Service

RecoverAI is an AI Revenue Recovery platform built for the **Razorpay AI Buildathon Track 03 — AI Revenue Recovery**.

This repository contains the production-ready FastAPI backend foundation built using clean modular architecture.

---

## 🏗️ Architecture Stack

- **Framework**: Python 3.12+ / FastAPI
- **Database**: PostgreSQL 16+ with SQLAlchemy 2.x ORM & Alembic migrations
- **Caching & Messaging Infra**: Redis 7+
- **Configuration & Validation**: Pydantic v2 & Pydantic Settings
- **Testing**: pytest & HTTPX
- **Containerization**: Docker & Docker Compose

---

## ⚙️ Environment Variables

The backend relies on environment variables specified in `.env` (see `.env.example`):

```ini
APP_NAME=RecoverAI
APP_ENV=development
LOG_LEVEL=INFO
API_VERSION=v1

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/recoverai_db
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/recoverai_db
REDIS_URL=redis://localhost:6379/0
```

---

## 🚀 Quickstart & Local Setup

### 1. Start Infrastructure Services (PostgreSQL & Redis)

Use Docker Compose to launch database and cache containers:

```bash
docker-compose up -d postgres redis
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Application Server

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation will be available at:
- OpenAPI Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

---

## 🧪 Running Tests

Execute the unit tests using `pytest`:

```bash
pytest
```

---

## 🩺 Health Check Endpoints

- **Unversioned Root Health Check**: `GET http://localhost:8000/health`
  - Response:
    ```json
    {
      "status": "ok",
      "service": "recoverai-api",
      "version": "0.1.0"
    }
    ```
- **Versioned Health Check**: `GET http://localhost:8000/api/v1/health`
- **Detailed Infrastructure Health Check**: `GET http://localhost:8000/api/v1/health/detailed`
