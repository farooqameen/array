from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, status
from typing import List
from controllers.search_controller import handle_search, handle_pdf_upload
from logger import logger
from models.api_models import QueryResponse, UploadResponse

router = APIRouter()


@router.post(
    "/search/upload/",
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
        description="The PDF files to be uploaded and indexed (max 10 files, 10MB total).",
    ),
) -> UploadResponse:
    """
    Handles asynchronous PDF upload, parses the files, and indexes their content into OpenSearch.

    Args:
        index_name (str): The name of the OpenSearch index where the PDF contents will be stored.
        files (List[UploadFile]): The PDF files to upload.

    Returns:
        UploadResponse: Status and metadata about the upload operation for each file.
    """
    logger.info(
        f"Received upload request for index: '{index_name}' with {len(files)} files."
    )

    # Basic server-side validation for number of files and total size (redundant if frontend validates, but good practice)
    MAX_FILES = 10
    MAX_TOTAL_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    if not (1 <= len(files) <= MAX_FILES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of files must be between 1 and {MAX_FILES}.",
        )

    total_size = sum(file.size for file in files)
    if total_size > MAX_TOTAL_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total file size exceeds {MAX_TOTAL_SIZE_BYTES / (1024 * 1024)}MB. Current total: {total_size / (1024 * 1024):.2f}MB.",
        )

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' is not a PDF. Only PDF files are allowed.",
            )

    try:
        result = await handle_pdf_upload(files, index_name)
        if result.get("status") in ["success", "partially_successful"]:
            logger.info(
                f"Completed processing upload for index '{index_name}'. Overall status: {result.get('status')}"
            )
            return UploadResponse(**result)
        else:
            logger.error(
                f"Failed to process upload for index '{index_name}': {result.get('reason', 'Unknown error')}"
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
            f"An unhandled error occurred during PDF upload for index '{index_name}'."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during upload: {e}",
        )


@router.get(
    "/search",
    summary="Search within a specific OpenSearch index",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
def search(
    index_name: str = Query(
        ..., description="Name of the OpenSearch index to search within."
    ),
    query: str = Query(..., description="The search query string."),
) -> QueryResponse:
    """
    Performs a search on a specified OpenSearch index using the provided query string.

    Args:
        index_name (str): The OpenSearch index to search.
        query (str): The query string to search for.

    Returns:
        SearchResponse: Contains the search status and list of matching document chunks.
    """
    logger.info(
        f"Received search request for index: '{index_name}' with query: '{query}'"
    )
    try:
        result = handle_search(index_name, query)
        if result.get("status") == "success":
            logger.info(
                f"Search completed for '{query}' in '{index_name}'. Found {len(result.get('results', []))} results."
            )
            return SearchResponse(**result)
        else:
            logger.warning(
                f"Search failed for '{query}' in '{index_name}': {result.get('reason', 'Unknown error')}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("reason", "Failed to perform search."),
            )
    except Exception as e:
        logger.exception(
            f"An unhandled error occurred during search for query '{query}'."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during search: {e}",
        )
