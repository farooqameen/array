from fastapi import FastAPI
from config.cors import configure_cors
from core.lifespan import lifespan
from routes import chat_routes, search_routes


def create_app() -> FastAPI:
    """
    Factory function to initialize and return a FastAPI application instance.
    Applies middleware, lifespan handler, and routes.
    """
    app = FastAPI(lifespan=lifespan)
    configure_cors(app)
    app.include_router(chat_routes.router)
    app.include_router(search_routes.router)
    return app
