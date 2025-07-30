from config.cors import configure_cors
from core.lifespan import lifespan
from fastapi import FastAPI

from app.router import chat_router, csv_chat_router, health_router, search_router


def create_app() -> FastAPI:
    """
    Factory function to initialize and return a FastAPI application instance.
    Applies middleware, lifespan handler, and routes.
    """
    app = FastAPI(lifespan=lifespan, root_path="/api")
    configure_cors(app)
    app.include_router(chat_router.router)
    app.include_router(search_router.router)
    app.include_router(csv_chat_router.router)
    app.include_router(health_router.router)
    return app
