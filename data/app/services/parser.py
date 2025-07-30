from typing import List, cast
from pathlib import Path

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import CompositeElement
from logger import logger


def parse_pdf_advanced(file_path: Path) -> List[CompositeElement]:
    """
    Parses a PDF file using a multi-step 'unstructured' strategy.

    1.  Partitions the PDF into its smallest constituent elements.
    2.  Chunks those elements together based on document titles and headers,
        creating larger, more contextually complete chunks.

    This provides high-quality, meaningful chunks to the downstream LLM.
    """
    logger.info("Starting advanced PDF parsing and chunking for: %s", file_path.name)
    try:
        # Step 1: Get all the raw elements from the PDF.
        # Using hi_res strategy is best for layout-aware chunking.
        initial_elements = partition_pdf(
            filename=str(file_path),
            strategy="fast",  # originally "hi_res", fast to avoid dependency issues in dev
            infer_table_structure=True,
        )

        logger.info("Partitioned PDF into %d initial elements.", len(initial_elements))
        logger.info("Initial elements: %s", initial_elements)

        # Step 2: Group these elements into logical chunks.
        # This is the key to creating meaningful context for the LLM.
        chunks = chunk_by_title(
            elements=initial_elements,
            max_characters=2048,  # Max size of a chunk
            new_after_n_chars=1500,  # Start a new chunk if the current one is big
            combine_text_under_n_chars=500,  # Combine small elements together
        )

        logger.info(
            "Successfully chunked document into %d composite elements.", len(chunks)
        )
        return cast(List[CompositeElement], chunks)

    except Exception as e:
        logger.error("Error during advanced PDF parsing/chunking: %s", e, exc_info=True)
        return []
