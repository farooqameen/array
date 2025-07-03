from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings


def configure_cors(app: FastAPI):
    """
    Configures CORS middleware to allow frontend access.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
