"""
Controller module for handling document-related API logic.

This includes uploading documents and querying indexed rulebooks
via a global query engine instance.
"""

import os
import shutil
from fastapi import UploadFile, HTTPException, status
from utils.file_utils import save_uploaded_file
from models.api_models import QueryResponse, UploadResponse, FileUploadResult
from logger import logger
from config.settings import settings
from prompts.query_prompt import rulebook_query_prompt, traditional_rag_query_prompt
from services.bot.index_service import (
    build_hierarchical_index,
    get_hrag_query_engine,
    build_traditional_index,
    get_traditional_query_engine,
)

# Global query engine variable
_hrag_query_engine = None
_trad_rag_query_engine = None

def set_hrag_query_engine(engine):
    global _hrag_query_engine
    _hrag_query_engine = engine
    logger.info("HRAG global query engine has been set.")

def set_trad_rag_query_engine(engine):
    global _trad_rag_query_engine
    _trad_rag_query_engine = engine
    logger.info("Traditional RAG global query engine has been set.")

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
        HTTPException: If no filename is provided or an error occurs while saving or indexing.
    """
    if not file.filename:
        logger.warning("Attempted to upload a file with no filename.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
        )

    try:
        file_location = await save_uploaded_file(file, settings.UPLOAD_DIR)
        logger.info(f"File '{file.filename}' successfully saved to {file_location}")

        if rag_type == "HRAG":
            if os.path.exists(settings.HRAG_INDEX_PATH):
                shutil.rmtree(settings.HRAG_INDEX_PATH)
            build_hierarchical_index(settings.DATA_DIR, settings.HRAG_INDEX_PATH)
            query_engine = get_hrag_query_engine(settings.HRAG_INDEX_PATH)
            set_hrag_query_engine(query_engine)
            logger.info("HRAG index built and query engine set.")
        elif rag_type == "TradRAG":
            if os.path.exists(settings.TRAD_RAG_INDEX_PATH):
                shutil.rmtree(settings.TRAD_RAG_INDEX_PATH)
            build_traditional_index(settings.DATA_DIR, settings.TRAD_RAG_INDEX_PATH)
            query_engine = get_traditional_query_engine(settings.TRAD_RAG_INDEX_PATH)
            set_trad_rag_query_engine(query_engine)
            logger.info("Traditional RAG index built and query engine set.")
        else:
            logger.error(f"Invalid RAG type: {rag_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid RAG type. Must be 'HRAG' or 'TradRAG'."
            )

        return UploadResponse(
            status="success",
            results=[
                FileUploadResult(
                    filename=file.filename,
                    status="success",
                    indexed_chunks=None,
                    reason=None
                )
            ]
        )
    except Exception as e:
        logger.error(f"Failed to upload file '{file.filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload file or build index: {e}",
        )

async def _query_engine(engine, prompt_template, query: str) -> QueryResponse:
    if engine is None:
        logger.error("Query engine is not ready. Index might not be built or loaded.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Query engine not ready. Please ensure documents are indexed.",
        )
    formatted_prompt = prompt_template.format(query=query)
    logger.debug(f"Querying rulebook with: {formatted_prompt}")
    try:
        response = engine.query(formatted_prompt)
        logger.debug("Received response from query engine.")
        return QueryResponse(response=str(response))
    except Exception as e:
        logger.error(f"Error querying rulebook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {e}",
        )

async def query_hrag(query: str) -> QueryResponse:
    return await _query_engine(_hrag_query_engine, rulebook_query_prompt, query)

async def query_trad_RAG(query: str) -> QueryResponse:
    return await _query_engine(_trad_rag_query_engine, traditional_rag_query_prompt, query)