"""
PDF table extraction utility.

Provides functions to extract tables from PDF files using pdfplumber.
"""

from pathlib import Path
from typing import List

import pdfplumber


def extract_tables(file_path: Path) -> List[List[List[str]]]:
    """
    Extract tables from all pages of a PDF file.

    Args:
        file_path (Path): Path to the PDF file.

    Returns:
        List[List[List[str]]]: List of tables, each table is a list of rows (each row is a list of strings).
    """
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:
                    tables.append(table)
    return tables
