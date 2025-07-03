"""
Application startup initialization module.

Handles the setup of LLM configurations, data directory validation,
hierarchical index building/loading, and global query engine setup
for the FastAPI application.
"""

import os
import shutil
from fastapi import FastAPI
from services.bot.index_service import (
    build_hierarchical_index,
    get_hrag_query_engine,
    build_traditional_index,
    get_traditional_query_engine,
)
from services.bot.llm_service import initialize_llm_settings
from controllers.chat_controller import set_hrag_query_engine, set_trag_query_engine
from config.settings import settings
from logger import logger


async def initialize_application(app: FastAPI):
    """
    Initializes the application on startup.

    Steps:
    - Initialize LLM and embedding models.
    - Verify that the data directory exists and contains documents.
    - Build or load the hierarchical index for document retrieval.
    - Load the query engine and set it globally for controllers.

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

    # Check that the data directory exists and is not empty
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        logger.error(
            f"Error: The directory '{data_dir}' does not exist or is empty. Please place documents in this directory."
        )
        return

    logger.info("Indexing the following files:")
    for fname in os.listdir(data_dir):
        logger.info(f"- {fname}")

    # Prompt user for RAG type
    print("Select RAG type to use:")
    print("1. Hierarchical RAG (HRAG)")
    print("2. Traditional RAG (Trad RAG)")
    rag_choice = input("Enter 1 for HRAG or 2 for Trad RAG: ").strip()

    if rag_choice == "1":
        # HRAG pipeline
        if os.path.exists(hrag_index_path) and os.listdir(hrag_index_path):
            logger.info(f"Existing HRAG index found at {hrag_index_path}. Loading index.")
        else:
            logger.info(
                f"No existing HRAG index found at {hrag_index_path} or it's empty. Building new hierarchical index."
            )
            if os.path.exists(hrag_index_path):
                shutil.rmtree(hrag_index_path)
                logger.info(f"Cleaned up existing directory {hrag_index_path}.")
            build_hierarchical_index(data_dir, hrag_index_path)
            logger.info("Hierarchical index built successfully.")

        query_engine = get_hrag_query_engine(hrag_index_path)
        set_hrag_query_engine(query_engine)
        logger.info("HRAG query engine loaded and set.")

    elif rag_choice == "2":
        # Traditional RAG pipeline
        if os.path.exists(trad_rag_index_path) and os.listdir(trad_rag_index_path):
            logger.info(f"Existing Trad RAG index found at {trad_rag_index_path}. Loading index.")
        else:
            logger.info(
                f"No existing Trad RAG index found at {trad_rag_index_path} or it's empty. Building new traditional index."
            )
            if os.path.exists(trad_rag_index_path):
                shutil.rmtree(trad_rag_index_path)
                logger.info(f"Cleaned up existing directory {trad_rag_index_path}.")
            build_traditional_index(data_dir, trad_rag_index_path)
            logger.info("Traditional index built successfully.")

        query_engine = get_traditional_query_engine(trad_rag_index_path)
        set_trag_query_engine(query_engine)
        logger.info("Traditional RAG query engine loaded and set.")

    else:
        logger.error("Invalid RAG type selection. Please restart and choose 1 or 2.")
        print("Invalid selection. Exiting initialization.")
        return

    logger.info("Application initialization complete.")
