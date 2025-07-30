"""
File utility functions.

Includes asynchronous file saving and file hash generation.
"""

import hashlib
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from logger import logger


async def save_uploaded_file(file: UploadFile, destination_dir: Path) -> Path:
    """
    Save an uploaded file to the specified destination directory.

    Args:
        file (UploadFile): The uploaded file.
        destination_dir (Path): Directory to save the file.

    Returns:
        Path: Path to the saved file.

    Raises:
        Exception: If file saving fails.
    """
    if not destination_dir.exists():
        destination_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created directory: %s", destination_dir)

    file_location = destination_dir / file.filename
    try:
        async with aiofiles.open(file_location, "wb") as f:
            while content := await file.read(1024 * 1024):
                await f.write(content)
        logger.info(
            "File '%s' saved successfully to '%s'", file.filename, file_location
        )
        return file_location
    except Exception as e:
        logger.error(
            "Error saving file '%s' to '%s': %s",
            file.filename,
            file_location,
            e,
            exc_info=True,
        )
        raise


def get_file_hash(file_path: Path) -> str:
    """
    Generate a short MD5 hash for a file's contents.

    Args:
        file_path (Path): Path to the file.

    Returns:
        str: First 10 characters of the file's MD5 hash.
    """
    content = file_path.read_bytes()
    return hashlib.md5(content).hexdigest()[:10]
