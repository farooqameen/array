from typing import List, Optional
from pydantic import BaseModel


class ChunkElement(BaseModel):
    text: str
    page_number: int
    element_type: Optional[str] = None


class ParsedData(BaseModel):
    chunks: List[ChunkElement]


class ParseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ParsedData] = None
