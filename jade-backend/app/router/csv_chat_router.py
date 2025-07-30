"""
API routes for CSV and PDF uploads, summaries, chart suggestions, and natural language queries.

Defines FastAPI endpoints for uploading files, summarizing contents,
generating chart recommendations, and querying via LLM.
"""

from controllers import csv_chat_controller
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from logger import logger
from models.api_models import CsvQueryRequest, CSVUploadResponse, PDFUploadResponse
from utils.auth import extract_session_id

router = APIRouter(prefix="/csv", tags=["CSV"])


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """
    Upload a CSV file and return summary and chart suggestions.

    Args:
        request (Request): FastAPI request object.
        file (UploadFile): The uploaded CSV file.

    Returns:
        CSVUploadResponse: Response with summary and chart suggestions.
    """
    session_id = extract_session_id(request)

    if not session_id or not file.filename:
        detail = []
        if not session_id:
            detail.append("Session ID is required")
        if not file.filename:
            detail.append("No filename provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="; ".join(detail)
        )

    try:
        logger.info(session_id)
        response = await csv_chat_controller.upload_csv(file, session_id)
        return response
    except Exception as e:
        logger.error("Error uploading CSV: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        ) from e


@router.post("/pdf/upload", response_model=PDFUploadResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """
    Upload a PDF file, extract tables, and return summary and chart suggestions.

    Args:
        request (Request): FastAPI request object.
        file (UploadFile): The uploaded PDF file.

    Returns:
        PDFUploadResponse: Response with summary, chart suggestions, and extracted data.
    """
    session_id = extract_session_id(request)

    if not session_id or not file.filename:
        detail = []
        if not session_id:
            detail.append("Session ID is required")
        if not file.filename:
            detail.append("No filename provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="; ".join(detail)
        )

    try:
        logger.info("Session: %s", session_id)
        response = await csv_chat_controller.upload_pdf(file, session_id)
        return response
    except Exception as e:
        logger.error("Error uploading PDF: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        ) from e


@router.post("/query")
async def query_csv(request: Request, query_data: CsvQueryRequest):
    """
    Stream query response from uploaded CSV using LLM.
    """
    session_id = extract_session_id(request)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID is required",
        )

    try:
        stream = await csv_chat_controller.query_csv_data_stream(
            query_data.query, session_id
        )

        if stream is None:
            raise HTTPException(
                status_code=500,
                detail="Query engine could not be loaded",
            )

        return StreamingResponse(stream, media_type="text/plain")

    except Exception as e:
        logger.error("Streaming error during CSV query: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Streaming failed: {e}") from e
