"""
Application startup initialization module.

Handles the setup of LLM configurations, data directory validation,
hierarchical index building/loading, and global query engine setup
for the FastAPI application.
"""

import os

from config.settings import settings
from controllers.chat_controller import set_query_engine
from fastapi import FastAPI
from logger import logger
from services.bot.index_service import (
    get_hrag_query_engine,
    get_traditional_query_engine,
)
from services.bot.llm_service import initialize_llm_settings


async def initialize_application(_app: FastAPI):
    """
    Initializes the application on startup.

    Steps:
    - Initialize LLM and embedding models.
    - Verify that the data directory exists.
    - (Index creation is now handled during document upload.)
    - Load the query engine if index exists.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Initializing application...")

    # Initialize LLM and embedding settings
    initialize_llm_settings()
    logger.info("LLM settings initialized.")

    data_dir = settings.DATA_DIR
    hrag_index_path = settings.HRAG_INDEX_PATH
    trad_rag_index_path = settings.TRAD_RAG_INDEX_PATH

    # Check that the data directory exists
    if not os.path.exists(data_dir):
        logger.error(
            "Error: The directory %s does not exist. Please create this directory.",
            data_dir,
        )
        return

    logger.info("Data directory exists.")

    # Optionally, load existing indexes and query engines if present
    if os.path.exists(hrag_index_path) and os.listdir(hrag_index_path):
        query_engine = get_hrag_query_engine(hrag_index_path)
        set_query_engine(query_engine, "HRAG")
        logger.info("HRAG query engine loaded and set.")
    if os.path.exists(trad_rag_index_path) and os.listdir(trad_rag_index_path):
        query_engine = get_traditional_query_engine(trad_rag_index_path)
        set_query_engine(query_engine, "TradRAG")
        logger.info("Traditional RAG query engine loaded and set.")

    logger.info("Application initialization complete.")
