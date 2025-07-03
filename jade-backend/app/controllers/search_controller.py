# controllers/search_controller.py
import os
import uuid
from typing import List, Dict
from fastapi import UploadFile
from anyio import to_thread
from services.search.pdf_parser import parse_pdf
from services.search.opensearch import index_chunks, create_index, search_chunks


from logger import logger


# Define the directory for temporary PDF uploads.
UPLOAD_DIR = "/tmp/pdf_uploads"
# Ensure the upload directory exists.
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def process_single_pdf(file: UploadFile, index_name: str) -> Dict:
    """
    Handles the complete process of saving, parsing, and indexing a single PDF file.
    This is an internal helper for handle_pdf_upload.
    """
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, unique_filename)

    logger.info(f"Attempting to save uploaded file '{file.filename}' to '{filepath}'.")
    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File '{file.filename}' successfully saved.")
    except Exception as e:
        logger.error(f"Error saving uploaded file '{file.filename}': {e}")
        return {
            "filename": file.filename,
            "status": "failed",
            "reason": f"Could not save uploaded file: {e}",
        }

    logger.info(f"Starting PDF parsing for '{unique_filename}' in background thread.")
    chunks = []
    try:
        chunks = await to_thread.run_sync(parse_pdf, filepath)
    except Exception as e:
        logger.error(f"PDF parsing failed for '{file.filename}': {e}")
        # Ensure temporary file is removed even if parsing fails
        try:
            os.remove(filepath)
            logger.info(f"Temporary file '{filepath}' removed after parsing failure.")
        except OSError as oe:
            logger.warning(
                f"Error removing temporary file '{filepath}' after parsing failure: {oe}"
            )
        return {
            "filename": file.filename,
            "status": "failed",
            "reason": f"PDF parsing error: {e}",
        }

    try:
        os.remove(filepath)
        logger.info(f"Temporary file '{filepath}' removed.")
    except OSError as e:
        logger.warning(f"Error removing temporary file '{filepath}': {e}")

    if not chunks:
        logger.warning(
            f"No text chunks extracted from '{file.filename}'. Skipping indexing."
        )
        return {
            "filename": file.filename,
            "status": "failed",
            "reason": "No valid text extracted from the PDF.",
        }

    logger.info(
        f"Extracted {len(chunks)} chunks from '{file.filename}'. Proceeding to index in '{index_name}'."
    )
    try:
        # The index creation happens once before processing all files
        index_chunks(index_name, chunks)
        logger.info(f"Indexing of '{file.filename}' is Done")
        return {
            "filename": file.filename,
            "status": "success",
            "indexed_chunks": len(chunks),
        }
    except Exception as e:
        logger.error(f"Indexing failed for '{file.filename}' into '{index_name}': {e}")
        return {
            "filename": file.filename,
            "status": "failed",
            "reason": f"Failed to index chunks into OpenSearch: {e}",
        }


async def handle_pdf_upload(files: List[UploadFile], index_name: str) -> Dict:
    """
    Handles the complete process of uploading, parsing, and indexing multiple PDF files.

    Steps:
        1. Create the OpenSearch index (if it doesn't exist) once for all files.
        2. Process each file: save, parse asynchronously, remove temp file, index.
        3. Aggregate results for all files.

    Args:
        files (List[UploadFile]): The list of uploaded PDF files.
        index_name (str): The OpenSearch index name to store parsed chunks.

    Returns:
        dict: A dictionary indicating the overall status and results for each file.
    """
    if not files:
        return {"status": "failed", "reason": "No files provided for upload."}

    logger.info(
        f"Received upload request for {len(files)} files for index: '{index_name}'"
    )

    # Create the index once for all files
    try:
        create_index(index_name)
    except Exception as e:
        logger.error(
            f"Failed to create index '{index_name}' before file processing: {e}"
        )
        return {"status": "failed", "reason": f"Failed to prepare index: {e}"}

    results_per_file: List[Dict] = []
    for file in files:
        file_result = await process_single_pdf(file, index_name)
        results_per_file.append(file_result)

    overall_status = (
        "success"
        if all(r["status"] == "success" for r in results_per_file)
        else "partially_successful"
    )
    if overall_status == "partially_successful":
        logger.warning(f"Some files failed to upload for index '{index_name}'.")
    else:
        logger.info(f"All files processed successfully for index '{index_name}'.")

    return {
        "status": overall_status,
        "results": results_per_file,
    }


def handle_search(index_name: str, query: str) -> dict:
    """
    Processes a search request by validating inputs and invoking the OpenSearch search service.

    Args:
        index_name (str): Name of the OpenSearch index to query.
        query (str): The search query string.

    Returns:
        dict: A dictionary containing the status, query, and search results or failure reason.
    """
    if not query or not index_name:
        logger.warning(
            "Search request failed: 'index_name' or 'query' parameter is missing."
        )
        return {"status": "failed", "reason": "Missing index_name or query parameters."}

    logger.info(f"Processing search in index '{index_name}' for query: '{query}'.")
    results = search_chunks(index_name, query)

    if results is None:
        logger.error(
            f"Search operation for query '{query}' in '{index_name}' returned an error or no data."
        )
        return {"status": "failed", "reason": "Search operation failed."}

    logger.info(f"Search successful for '{query}'. Found {len(results)} results.")
    return {"status": "success", "query": query, "results": results}
