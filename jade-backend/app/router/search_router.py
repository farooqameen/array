"""
API routes for OpenSearch document management and search functionality.

This module defines FastAPI endpoints for uploading PDF files to OpenSearch indexes
and performing search queries within those indexes.
"""

from typing import List

from controllers.search_controller import handle_pdf_upload, handle_search
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from logger import logger
from models.api_models import SearchResponse, UploadResponse

from router.constants import upload_settings

router = APIRouter(prefix="/opensearch", tags=["OpenSearch"])


@router.post(
    "/upload",
    summary="Upload multiple PDFs and index their content",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_pdfs(
    index_name: str = Form(
        ..., description="Name of the search engine index for the PDFs."
    ),
    files: List[UploadFile] = File(
        ...,
        description=(
            "The PDF files to be uploaded and indexed (max 10 files, 10MB total)."
        ),
    ),
) -> UploadResponse:
    """
    Handle asynchronous PDF upload, parse files, and index content into OpenSearch.

    Args:
        index_name (str): The name of the OpenSearch index where the PDF
            contents will be stored.
        files (List[UploadFile]): The PDF files to upload.

    Returns:
        UploadResponse: Status and metadata about the upload operation
            for each file.
    """
    logger.info(
        "Received upload request for index: '%s' with %d files.",
        index_name,
        len(files),
    )

    if not (1 <= len(files) <= upload_settings.MAX_FILES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Number of files must be between 1 and {upload_settings.MAX_FILES}."
            ),
        )

    total_size = sum(file.size for file in files)
    if total_size > upload_settings.MAX_TOTAL_SIZE_BYTES:
        max_size_mb = upload_settings.MAX_TOTAL_SIZE_BYTES / (1024 * 1024)
        current_size_mb = total_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Total file size exceeds {max_size_mb}MB. "
                f"Current total: {current_size_mb:.2f}MB."
            ),
        )

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File '{file.filename}' is not a PDF. Only PDF files are allowed."
                ),
            )

    try:
        result = await handle_pdf_upload(files, index_name)
        if result.get("status") in ["success", "partially_successful"]:
            logger.info(
                "Completed processing upload for index '%s'. Overall status: %s",
                index_name,
                result.get("status"),
            )
            return UploadResponse(**result)
        else:
            logger.error(
                "Failed to process upload for index '%s': %s",
                index_name,
                result.get("reason", "Unknown error"),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("reason", "Failed to process PDF upload."),
            )
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception(
            "An unhandled error occurred during PDF upload for index '%s'",
            index_name,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during upload: {e}",
        ) from e


@router.get(
    "/search",
    summary="Search within a specific OpenSearch index",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
)
def search(
    index_name: str = Query(
        ..., description="Name of the OpenSearch index to search within."
    ),
    query: str = Query(..., description="The search query string."),
) -> SearchResponse:
    """
    Performs a search on a specified OpenSearch index using the provided query string.

    Args:
        index_name (str): The OpenSearch index to search.
        query (str): The query string to search for.

    Returns:
        SearchResponse: Contains the search status and list of matching document chunks.
    """
    logger.info(
        "Received search request for index: '%s' with query: '%s'",
        index_name,
        query,
    )
    try:
        result = handle_search(index_name, query)
        if result.get("status") == "success":
            logger.info(
                "Search completed for '%s' in '%s'. Found %d results.",
                query,
                index_name,
                len(result.get("results", [])),
            )
            logger.info("%s\n", SearchResponse(**result))
            return SearchResponse(**result)
        else:
            logger.warning(
                "Search failed for '%s' in '%s': %s",
                query,
                index_name,
                result.get("reason", "Unknown error"),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("reason", "Failed to perform search."),
            )
    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception(
            "An unhandled error occurred during search for query '%s'",
            query,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during search: {e}",
        ) from e
