# project_root/utils/file_utils.py
from fastapi import UploadFile
from pathlib import Path
import aiofiles
from logger import logger


async def save_uploaded_file(file: UploadFile, destination_dir: Path) -> Path:
    """
    Saves an uploaded file to the specified destination directory.
    """
    if not destination_dir.exists():
        destination_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {destination_dir}")

    file_location = destination_dir / file.filename
    try:
        # Use aiofiles for asynchronous file writing
        async with aiofiles.open(file_location, "wb") as f:
            while content := await file.read(1024 * 1024):  # Read in 1MB chunks
                await f.write(content)
        logger.info(f"File '{file.filename}' saved successfully to '{file_location}'")
        return file_location
    except Exception as e:
        logger.error(
            f"Error saving file '{file.filename}' to '{file_location}': {e}",
            exc_info=True,
        )
        raise
