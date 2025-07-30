# controllers/search_controller.py

import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import httpx
from anyio import to_thread
from config.settings import settings
from fastapi import UploadFile
from logger import logger
from services.stores.opensearch import OpenSearchStore
from services.stores.s3 import upload_file_to_s3
from utils.file_utils import save_uploaded_file

from app.services.bot.metadata_extractor import generate_structured_data_from_chunk

# Create a single OpenSearchStore instance
opensearch_store = OpenSearchStore()


async def process_single_pdf(
    file: UploadFile, index_name: str, batch_number: int
) -> Dict:
    """
    Handles the advanced processing of a single PDF file.
    Flow: Save -> Upload to S3 -> Parse & Chunk -> Enhance with LLM -> Index -> Cleanup.
    """
    temp_filepath: Path | None = None
    try:
        temp_filepath = await save_uploaded_file(file, settings.UPLOAD_DIR)

        insertion_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        s3_object_key = f"{index_name}/{insertion_date}/{temp_filepath.name}"
        s3_link = await upload_file_to_s3(temp_filepath, s3_object_key)

        logger.info("Connecting to PDF parser")
        async with httpx.AsyncClient() as client:
            with temp_filepath.open("rb") as f:
                response = await client.post(
                    settings.PDF_PARSER_SERVICE_URL,
                    files={"file": (file.filename, f, file.content_type)},
                    timeout=settings.PDF_PARSER_TIMEOUT,
                )
                logger.info("PDF parser response received")

        if response.status_code != 200:
            raise ValueError(f"Parser service failed: {response.text}")

        chunks_raw = response.json()["data"]["chunks"]
        if not chunks_raw:
            raise ValueError("No chunks returned from parser service.")

        logger.info("Trying to generate structured data for chunks.")
        processing_tasks = [
            generate_structured_data_from_chunk(str(chunk)) for chunk in chunks_raw
        ]

        logger.info("Awaiting LLM results.")
        llm_results = await asyncio.gather(*processing_tasks)

        logger.info(
            "Generated structured data for %d chunks from '%s'.",
            len(llm_results),
            file.filename,
        )

        opensearch_docs = []
        for i, chunk_element in enumerate(chunks_raw):
            structured_data = llm_results[i]

            # Use the page number from the first element in the composite chunk
            page_number = chunk_element.get("page_number") or 1

            # The markdown content is now the primary text source
            content_markdown = structured_data.get("content_markdown", "")

            # Assemble the final, non-redundant document
            doc = {
                "chunk_id": str(uuid.uuid4()),
                # The 'text' field is the searchable, markdown-formatted content
                "text": content_markdown,
                # Add the structured fields for display and filtering
                "title": structured_data.get("title"),
                "chapter": structured_data.get("chapter"),
                "section": structured_data.get("section"),
                "header": structured_data.get("header"),
                # Metadata
                "page_number": page_number,
                "batch_number": batch_number,
                "original_pdf_filename": file.filename,
                "word_count": len(content_markdown.split()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "s3_link": s3_link,
            }
            opensearch_docs.append(doc)

        await to_thread.run_sync(
            opensearch_store.index_chunks, index_name, opensearch_docs
        )

        return {
            "filename": file.filename,
            "status": "success",
            "indexed_chunks": len(opensearch_docs),
        }
    except Exception as e:
        logger.error("Failed to process file '%s': %s", file.filename, e, exc_info=True)
        return {"filename": file.filename, "status": "error", "reason": str(e)}
    finally:
        if temp_filepath and temp_filepath.exists():
            os.remove(temp_filepath)


# ... (handle_pdf_upload and handle_search functions remain the same as before) ...
async def handle_pdf_upload(files: List[UploadFile], index_name: str) -> Dict:
    if not files:
        return {"status": "failed", "reason": "No files provided for upload."}
    logger.info(
        "Received upload request for %d files for index: '%s'", len(files), index_name
    )
    try:
        await to_thread.run_sync(opensearch_store.create_index, index_name)
        batch_number = await to_thread.run_sync(
            opensearch_store.get_next_batch_number, index_name
        )
        logger.info(
            "Processing upload as batch number: %d for index '%s'.",
            batch_number,
            index_name,
        )
    except Exception as e:
        logger.error(
            "Failed to prepare index '%s' or get batch number: %s",
            index_name,
            e,
            exc_info=True,
        )
        return {"status": "failed", "reason": f"Failed to prepare index: {e}"}
    processing_tasks = [
        process_single_pdf(file, index_name, batch_number) for file in files
    ]
    results_per_file = await asyncio.gather(*processing_tasks)
    overall_status = (
        "success"
        if all(r["status"] == "success" for r in results_per_file)
        else "partial_success"
    )
    if any(r["status"] == "error" for r in results_per_file):
        logger.warning("Some files failed to process for index '%s'.", index_name)
    logger.info(
        "All files processed for index '%s' with status: %s.",
        index_name,
        overall_status,
    )
    return {"status": overall_status, "results": results_per_file}


def handle_search(index_name: str, query: str) -> dict:
    if not query or not index_name:
        logger.warning(
            "Search request failed: 'index_name' or 'query' parameter is missing."
        )
        return {"status": "failed", "reason": "Missing index_name or query parameters."}
    logger.info("Processing search in index '%s' for query: '%s'.", index_name, query)
    results = opensearch_store.search_chunks(index_name, query)
    if results is None:
        logger.error(
            "Search operation for query '%s' in '%s' returned an error.",
            query,
            index_name,
        )
        return {"status": "failed", "reason": "Search operation failed."}
    logger.info("Search successful for '%s'. Found %d results.", query, len(results))
    return {"status": "success", "query": query, "results": results}
