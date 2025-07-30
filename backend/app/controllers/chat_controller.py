"""
Controller module for handling document-related API logic.

This includes uploading documents and querying indexed rulebooks
via a global query engine instance.
"""

import os
import shutil

from config.settings import settings
from fastapi import HTTPException, UploadFile, status
from logger import logger
from models.api_models import (
    ClearRAGResponse,
    FileUploadResult,
    QueryResponse,
    UploadResponse,
)
from services.bot.index_service import (
    build_hierarchical_index,
    build_traditional_index,
    get_hrag_query_engine,
    get_traditional_query_engine,
)
from services.bot.volume_selector import score_volumes_with_llm
from utils.file_utils import save_uploaded_file

from app.prompts.queries import RULEBOOK_QUERY_PROMPT, TRADITIONAL_RAG_QUERY_PROMPT

# Global query engine variable
_hrag_query_engine = None
_trad_rag_query_engine = None

VOLUME_NAME_TO_NUMBER = {
    "Volume 1: Conventional Banks": "1",
    "Volume 2: Islamic Banks": "2",
    "Volume 3: Insurance": "3",
    "Volume 4: Investment Business": "4",
    "Volume 5: Specialised Licensees": "5",
    "Volume 6: Capital Markets": "6",
    "Volume 7: Collective Investment Undertakings": "7",
}

COMMON_VOLUME_FILE = "rulebook_commonvol.pdf"


def set_query_engine(engine, engine_type):
    """
    Sets the global query engine variable for the specified type.

    Args:
        engine: The query engine instance to set.
        engine_type (str): Either 'HRAG' or 'TradRAG'.

    Raises:
        ValueError: If engine_type is not valid.
    """
    global _hrag_query_engine, _trad_rag_query_engine
    if engine_type == "HRAG":
        _hrag_query_engine = engine
        logger.info("HRAG global query engine has been set.")
    elif engine_type == "TradRAG":
        _trad_rag_query_engine = engine
        logger.info("Traditional RAG global query engine has been set.")
    else:
        logger.error("Invalid engine type for set_query_engine: %s", engine_type)
        raise ValueError(f"Invalid engine type: {engine_type}")


async def upload_document(file: UploadFile, rag_type: str) -> UploadResponse:
    """
    Upload a document to the server and (re)build the selected RAG index.

    Saves the uploaded file to the configured upload directory,
    then builds the selected index and sets the global query engine.

    Args:
        file (UploadFile): The file to upload.
        rag_type (str): The type of RAG index to build ("HRAG" or "TradRAG").

    Returns:
        UploadFileResponse: Metadata confirming successful upload and indexing.

    Raises:
        HTTPException: If no filename is provided or an error occurs
        while saving or indexing.
    """
    if not file.filename:
        logger.warning("Attempted to upload a file with no filename.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
        )

    try:
        file_location = await save_uploaded_file(file, settings.UPLOAD_DIR)
        logger.info("File '%s' successfully saved to %s", file.filename, file_location)

        if rag_type == "HRAG":
            if os.path.exists(settings.HRAG_INDEX_PATH):
                shutil.rmtree(settings.HRAG_INDEX_PATH)
            build_hierarchical_index(settings.DATA_DIR, settings.HRAG_INDEX_PATH)
            query_engine = get_hrag_query_engine(settings.HRAG_INDEX_PATH)
            set_query_engine(query_engine, "HRAG")
            logger.info("HRAG index built and query engine set.")
        elif rag_type == "TradRAG":
            if os.path.exists(settings.TRAD_RAG_INDEX_PATH):
                shutil.rmtree(settings.TRAD_RAG_INDEX_PATH)
            build_traditional_index(settings.DATA_DIR, settings.TRAD_RAG_INDEX_PATH)
            query_engine = get_traditional_query_engine(settings.TRAD_RAG_INDEX_PATH)
            set_query_engine(query_engine, "TradRAG")
            logger.info("Traditional RAG index built and query engine set.")
        else:
            logger.error("Invalid RAG type: %s", rag_type)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid RAG type. Must be 'HRAG' or 'TradRAG'.",
            )

        return UploadResponse(
            status="success",
            results=[
                FileUploadResult(
                    filename=file.filename,
                    status="success",
                    indexed_chunks=None,
                    reason=None,
                )
            ],
        )
    except Exception as e:
        logger.error("Failed to upload file '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload file or build index: {e}",
        ) from e


async def _query_engine(engine, prompt_template, query: str) -> QueryResponse:
    if engine is None:
        logger.error("Query engine is not ready. Index might not be built or loaded.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query engine is not initialized. Please upload documents first.",
        )

    top_volumes = score_volumes_with_llm(query, 3)
    logger.info("Selected volumes for query: %s", [v[0]["name"] for v in top_volumes])
    volumes = []
    for v in top_volumes:
        volumes.append(v[0]["name"])

    file_names = []
    for vol in volumes:
        if vol != "Common Volume":
            file_names.append("rulebook_vol" + vol[7] + ".pdf")
        else:
            file_names.append(COMMON_VOLUME_FILE)

    formatted_prompt = prompt_template.format(query=query, filters=file_names)
    logger.debug("Querying rulebook with: %s", formatted_prompt)
    try:
        response = engine.query(formatted_prompt)
        logger.debug("Received response from query engine.")
        return QueryResponse(response=str(response))
    except Exception as e:
        logger.error("Error querying rulebook: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {e}",
        ) from e


async def query_hrag(query: str) -> QueryResponse:
    return await _query_engine(_hrag_query_engine, RULEBOOK_QUERY_PROMPT, query)


async def query_trad_rag(query: str) -> QueryResponse:
    return await _query_engine(
        _trad_rag_query_engine, TRADITIONAL_RAG_QUERY_PROMPT, query
    )


async def clear_docs() -> ClearRAGResponse:
    """Delete all files in the HRAG index directory."""
    try:
        if os.path.exists(settings.DATA_DIR):
            shutil.rmtree(settings.DATA_DIR)
            logger.info("Cleared HRAG index at %s", settings.DATA_DIR)
        os.makedirs(settings.DATA_DIR, exist_ok=True)

        response = ClearRAGResponse(
            status="success", message="RAG index cleared successfully."
        )
        return response
    except Exception as e:
        logger.error("Failed to clear HRAG storage: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not clear HRAG index: {e}",
        ) from e
