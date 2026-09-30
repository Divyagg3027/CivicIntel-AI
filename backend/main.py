"""
CivicIntel AI - Backend Application
Tagline: Turning Citizen Voices into Development Intelligence

FastAPI entrypoint orchestrating:
- Request Ingestion & AI/NLP Analysis
- Civic Need Index & Hotspot Detection
- Aggregate Civic Analytics
- OpenAPI / Swagger Documentation
- CORS Configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import requests, analytics, hotspots

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CivicIntel AI API",
    description="Multilingual AI-powered civic intelligence engine that converts citizen requests into structured development intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(requests.router)
app.include_router(analytics.router)
app.include_router(hotspots.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "CivicIntel AI",
        "tagline": "Turning Citizen Voices into Development Intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint verifying application and database connectivity.
    """
    return {
        "status": "healthy",
        "service": "CivicIntel AI"
    }