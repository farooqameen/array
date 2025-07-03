from pydantic import BaseModel
from typing import Optional

class InputType(BaseModel):
    question: str
    session_id: str
    user_id: str
    generate_title: Optional[bool] = False

class RequestBody(BaseModel):
    input: InputType