"""
Controller module for handling document-related API logic.

This includes uploading documents and querying indexed rulebooks
via a global query engine instance.
"""

from fastapi import UploadFile, HTTPException, status
from utils.file_utils import save_uploaded_file
from models.api_models import QueryResponse, UploadResponse
from logger import logger
from config.settings import settings
from prompts.query_prompt import rulebook_query_prompt, traditional_rag_query_prompt

# Global query engine variable
_hrag_query_engine = None
_trad_rag_query_engine = None

def set_hrag_query_engine(engine):
    """
    Set the hrag query engine used for querying documents.

    Args:
        engine: A query engine instance (e.g., LlamaIndex query engine).
    """
    global _hrag_query_engine
    _hrag_query_engine = engine
    logger.info("Hrag global query engine has been set.")

def set_trag_query_engine(engine):
    """
    Set the traditional rag query engine used for querying documents.

    Args:
        engine: A query engine instance (e.g., LlamaIndex query engine).
    """
    global _trad_rag_query_engine
    _trad_rag_query_engine = engine
    logger.info("Trad rag global query engine has been set.")



async def upload_document(file: UploadFile) -> UploadResponse:
    """
    Upload a document to the server.

    Saves the uploaded file to the configured upload directory.
    Re-indexing logic may be added in future enhancements.

    Args:
        file (UploadFile): The file to upload.

    Returns:
        UploadFileResponse: Metadata confirming successful upload.

    Raises:
        HTTPException: If no filename is provided or an error occurs while saving.
    """
    if not file.filename:
        logger.warning("Attempted to upload a file with no filename.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
        )

    try:
        file_location = await save_uploaded_file(file, settings.UPLOAD_DIR)
        logger.info(f"File '{file.filename}' successfully saved to {file_location}")
        # TODO: Trigger re-indexing or incremental updates
        # Example: index_service.update_index(file_location)
        return UploadFileResponse(
            filename=file.filename, message="File uploaded successfully"
        )
    except Exception as e:
        logger.error(f"Failed to upload file '{file.filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload file: {e}",
        )


async def query_hrag(query: str) -> QueryResponse:
    """
    Query the indexed rulebook using the global query engine.

    Adds structured guidance to the prompt for precise referencing in answers.

    Args:
        query (str): The user question or prompt.

    Returns:
        QueryResponse: The LLM-generated answer to the query.

    Raises:
        HTTPException: If the query engine is not initialized or an error occurs during querying.
    """
    global _hrag_query_engine

    if _hrag_query_engine is None:
        logger.error("Query engine is not ready. Index might not be built or loaded.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Query engine not ready. Please ensure documents are indexed.",
        )

    # Use the HRAG prompt
    formatted_prompt = rulebook_query_prompt.format(query=query)
    logger.debug(f"Querying rulebook with: {formatted_prompt}")

    try:
        response = _hrag_query_engine.query(formatted_prompt)
        logger.debug("Received response from query engine.")
        return QueryResponse(response=str(response))
    except Exception as e:
        logger.error(f"Error querying rulebook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {e}",
        )

async def query_trad_RAG(query: str) -> QueryResponse:
    """
    Query the indexed rulebook using the global query engine.

    Adds structured guidance to the prompt for precise referencing in answers.

    Args:
        query (str): The user question or prompt.

    Returns:
        QueryResponse: The LLM-generated answer to the query.

    Raises:
        HTTPException: If the query engine is not initialized or an error occurs during querying.
    """
    global _trad_rag_query_engine

    if _trad_rag_query_engine is None:
        logger.error("Query engine is not ready. Index might not be built or loaded.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Query engine not ready. Please ensure documents are indexed.",
        )

    # Use the traditional RAG prompt
    formatted_prompt = traditional_rag_query_prompt.format(query=query)
    logger.debug(f"Querying rulebook with: {formatted_prompt}")

    try:
        response = _trad_rag_query_engine.query(formatted_prompt)
        logger.debug("Received response from query engine.")
        return QueryResponse(response=str(response))
    except Exception as e:
        logger.error(f"Error querying rulebook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {e}",
        )