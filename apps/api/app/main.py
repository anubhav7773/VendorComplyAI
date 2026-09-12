# apps/api/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import statutory, payouts, sync, ocr

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Statutory Compliance and AP Automation Engine for Section 43B(h) MSME Dues"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Subsystem Routers
app.include_router(statutory.router, prefix="/api/v1")
app.include_router(payouts.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }
