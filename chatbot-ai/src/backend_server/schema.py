from pydantic import BaseModel
from typing import Optional

class InputType(BaseModel):
    question: str
    session_id: str
    user_id: str
    generate_title: Optional[bool] = False
    volume_display_name:Optional[list[str]] = None
    subvolume_display_name:Optional[list[str]] = None
    category_display_name:Optional[list[str]] = None
    module_display_name:Optional[list[str]] = None
    chapter_display_name:Optional[list[str]] = None
    section_display_name:Optional[list[str]] = None

class RequestBody(BaseModel):
    input: InputType