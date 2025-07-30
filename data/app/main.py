"""
FastAPI entry point.
"""

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import parser
from settings import settings


# Create FastAPI instance
app = FastAPI(
    root_path="/api",
    title=settings.app_name,
    version=settings.app_version,
    description=settings.description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)
# Include routers
app.include_router(parser.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
