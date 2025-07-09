from contextlib import asynccontextmanager
from fastapi import FastAPI
from logger import logger
from startup import initialize_application
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application lifecycle management.
    Initializes services on startup and handles cleanup on shutdown.
    """
    logger.info("Application startup sequence initiated.")
    await initialize_application(app) 
    logger.info("Application startup sequence completed.")
    yield
    logger.info("Application shutdown sequence initiated.")
    logger.info("Application shutdown sequence completed.")
