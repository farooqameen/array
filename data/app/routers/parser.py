# app/routers/parser.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import os
import uuid

from models.schemas import ParseResponse, ChunkElement, ParsedData
from services.parser import parse_pdf_advanced
from settings import settings

router = APIRouter()

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/parse", response_model=ParseResponse)
async def parse_pdf(file: UploadFile = File(...)) -> ParseResponse:
    """
    Accepts a PDF file, parses it, and returns structured chunk data.
    """
    # Save to a temp file
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as f:
            content = await file.read()
            f.write(content)

        chunks = parse_pdf_advanced(file_path)

        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks returned from parsing.")

        chunk_data = [
            ChunkElement(
                text=str(chunk), 
                page_number=chunk.metadata.page_number or 1,
                element_type=chunk.category,
            )
            for chunk in chunks
        ]

        return ParseResponse(
            success=True,
            message="Parsed PDF successfully.",
            data=ParsedData(chunks=chunk_data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}") from e

    finally:
        if file_path.exists():
            os.remove(file_path)
