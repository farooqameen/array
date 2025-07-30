"""
Controller module for handling CSV analysis and chat logic.

This includes uploading CSV files, generating summaries,
chart suggestions, and enabling chat-like querying over data.
"""

import asyncio
import json
import shutil
from pathlib import Path

import pandas as pd
from config.settings import settings
from core.session_store import (
    append_message,
    get_engine,
    get_session_history,
    set_engine,
)
from fastapi import UploadFile
from logger import logger
from models.api_models import CSVUploadResponse, PDFUploadResponse
from services.csv import csv_chart_service, csv_chat_service, csv_pdf_parser
from utils.file_utils import get_file_hash, save_uploaded_file


async def upload_csv(file: UploadFile, session_id: str) -> CSVUploadResponse:
    """
    Upload a CSV file, build its index, and generate summary and chart suggestions.

    Args:
        file (UploadFile): The uploaded CSV file.
        session_id (str): The session identifier.

    Returns:
        CSVUploadResponse: Response with summary and chart suggestions.
    """
    file_path = await save_uploaded_file(file, settings.UPLOAD_DIR)
    file_hash = get_file_hash(file_path)
    index_path = settings.CSV_INDEX_DIR / session_id / file_hash
    index_path.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file_path, index_path / "original.csv")
    df = pd.read_csv(file_path)
    if not (index_path / "index.faiss").exists():
        csv_chat_service.build_csv_index(df, index_path)
    engine = csv_chat_service.load_csv_query_engine(index_path)
    set_engine(session_id, engine)
    summary, chart_suggestions = await asyncio.gather(
        csv_chat_service.summarize_csv(file_path),
        csv_chart_service.get_all_chart_suggestions(file_path),
    )

    logger.info(
        "Chart Suggestions:\n%s", json.dumps(chart_suggestions, indent=2, default=str)
    )

    return CSVUploadResponse(
        filename=file.filename or "",
        message="CSV file uploaded, summarized, and indexed successfully.",
        path=str(file_path),
        summary=summary,
        chart_suggestions=chart_suggestions,
    )


async def upload_pdf(file: UploadFile, session_id: str) -> PDFUploadResponse:
    """
    Upload a PDF file, extract tables, build index, and generate summary and chart suggestions.

    Args:
        file (UploadFile): The uploaded PDF file.
        session_id (str): The session identifier.

    Returns:
        PDFUploadResponse: Response with summary, chart suggestions, and extracted data.
    """
    file_path = await save_uploaded_file(file, settings.UPLOAD_DIR)
    file_hash = get_file_hash(file_path)
    index_path = settings.CSV_INDEX_DIR / session_id / file_hash
    index_path.mkdir(parents=True, exist_ok=True)
    tables = await asyncio.to_thread(csv_pdf_parser.extract_tables, file_path)
    if not tables:
        raise ValueError("No tables found in the PDF.")
    df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
    csv_path = index_path / "original.csv"
    df.to_csv(csv_path, index=False)
    if not (index_path / "index.faiss").exists():
        csv_chat_service.build_csv_index(df, index_path)
    engine = csv_chat_service.load_csv_query_engine(index_path)
    set_engine(session_id, engine)
    summary, chart_suggestions = await asyncio.gather(
        csv_chat_service.summarize_csv(csv_path),
        csv_chart_service.get_all_chart_suggestions(csv_path),
    )
    return PDFUploadResponse(
        filename=file.filename or "",
        message="PDF file extracted, summarized, and indexed successfully.",
        path=str(file_path),
        summary=summary,
        chart_suggestions=chart_suggestions,
        data=df.to_dict(orient="records"),
    )


async def query_csv_data_stream(query: str, session_id: str):
    """
    Stream query results from the CSV data using the session's query engine.

    Args:
        query (str): The query string.
        session_id (str): The session identifier.

    Returns:
        generator: Async generator streaming query results.
    """
    engine = get_engine(session_id)
    if engine is None:
        index_path = Path(settings.CSV_INDEX_DIR) / session_id
        try:
            engine = csv_chat_service.load_csv_query_engine(index_path)
            set_engine(session_id, engine)
        except (FileNotFoundError, OSError, ValueError) as e:
            logger.error(
                "Failed to load engine for session %s: %s", session_id, e, exc_info=True
            )
            return None

    chat_history = get_session_history(session_id).messages

    async def stream():
        full_response = ""
        try:
            async for chunk in engine.astream(
                {
                    "input": query.strip(),
                    "chat_history": chat_history,
                }
            ):
                content = getattr(chunk, "content", chunk)
                full_response += content
                yield content
        except (RuntimeError, ValueError, IOError) as e:
            logger.error(
                "Engine streaming failed for session %s: %s",
                session_id,
                e,
                exc_info=True,
            )
        else:
            append_message(session_id, "human", query.strip())
            append_message(session_id, "assistant", full_response)

    return stream()
