from fastapi import APIRouter
from app.api.v1.health import router as health_v1_router
from app.api.v1.opportunities import router as opportunities_v1_router
from app.api.v1.simulator import router as simulator_v1_router
from app.api.v1.execution import router as execution_v1_router
from app.api.v1.audit import router as audit_v1_router

api_router = APIRouter()

# Include versioned routers
api_router.include_router(health_v1_router)
api_router.include_router(opportunities_v1_router)
api_router.include_router(simulator_v1_router)
api_router.include_router(execution_v1_router)
api_router.include_router(audit_v1_router)
