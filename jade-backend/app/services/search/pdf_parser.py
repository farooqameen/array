import pdfplumber
import uuid
from logger import logger


def parse_pdf(file_path):
    """
    Parses a PDF file and extracts text content into discrete chunks.

    Each chunk corresponds to a cleaned paragraph of text extracted from each page.
    Each chunk is represented as a dictionary with a unique chunk ID, the page number,
    and the extracted text.

    Args:
        file_path (str): The filesystem path to the PDF file to parse.

    Returns:
        list of dict: A list of chunks extracted from the PDF. Each chunk dictionary
                      contains:
                        - 'chunk_id' (str): A unique UUID string identifier.
                        - 'page_number' (int): The page number where the text was found.
                        - 'text' (str): The cleaned paragraph text extracted.

    Logs info about the parsing process and errors if parsing fails.
    """
    logger.info(f"Parsing PDF file: {file_path}")
    chunks = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    for paragraph in text.split("\n\n"):
                        cleaned = paragraph.strip()
                        if cleaned:
                            chunk = {
                                "chunk_id": str(uuid.uuid4()),
                                "page_number": page_num,
                                "text": cleaned,
                            }
                            chunks.append(chunk)
        logger.info(f"Parsed {len(chunks)} chunks from {file_path}")
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")

    return chunks
