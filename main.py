#!/usr/bin/env python3
"""
ABM Content Marketing Engine - Main Application
Version: 08-09-2025
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.api.routes import accounts, content, engagement, sequences
from app.utils.logging import setup_logging
from app.integrations.hubspot_client import HubSpotABMClient

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting ABM Content Marketing Engine...")
    
    # Initialize HubSpot client
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    if not hubspot_api_key:
        logger.warning("HubSpot API key not found - some features will be disabled")
    
    yield
    
    logger.info("Shutting down ABM Content Marketing Engine...")

# Create FastAPI application
app = FastAPI(
    title="ABM Content Marketing Engine",
    description="Intelligent automation for enterprise B2B content marketing",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ABM Content Marketing Engine",
        "version": "1.0.0"
    }

# Include API routes
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(engagement.router, prefix="/api/v1/engagement", tags=["engagement"])
app.include_router(sequences.router, prefix="/api/v1/sequences", tags=["sequences"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
