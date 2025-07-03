from pydantic import BaseModel
from typing import Any, Optional
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import JSONResponse, StreamingResponse
from collections.abc import AsyncIterable, Iterable
import json
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.documents import Document


def serialize_model(obj: Any) -> dict:
    """
    Serialize different types of model objects to a dictionary.

    Converts HumanMessage, AIMessage, and Document objects 
    into a standardized dictionary format.

    Args:
        obj (Any): The object to be serialized.

    Returns:
        dict: A dictionary representation of the input object.

    Raises:
        TypeError: If the object type is not supported for serialization.
    """
    if isinstance(obj, HumanMessage):
        return {"content": obj.content, "example": obj.example, "id": obj.id,"name": obj.name,"response_metadata": obj.response_metadata, "type":obj.type}
    elif isinstance(obj, AIMessage):
        return {"content": obj.content, "example": obj.example, "id": obj.id,"name": obj.name,"usage_metadata": obj.usage_metadata, "type":obj.type}
    elif isinstance(obj, Document):
        return {"metadata": obj.metadata, "type":obj.type}
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class JSONStreamingResponse(StreamingResponse, JSONResponse):
    """
    A streaming response that renders content in JSON format.

    Extends StreamingResponse and JSONResponse to provide 
    a streaming JSON response with custom serialization.
    """

    def render(self, content: Any) -> bytes:
        """
        Render the content as a JSON-encoded byte string.

        Args:
            content (Any): The content to be rendered.

        Returns:
            bytes: JSON-encoded representation of the content.
        """
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=serialize_model
        ).encode("utf-8") + b'\n'
    
    def __init__(
        self,
        content: Iterable | AsyncIterable,
        status_code: int = 200,
        headers: Optional[dict[str, str]]= None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
    ):
        """
        Initialize a JSON streaming response.

        Args:
            content (Iterable or AsyncIterable): The content to be streamed.
            status_code (int, optional): HTTP status code. Defaults to 200.
            headers (dict, optional): Response headers. Defaults to None.
            media_type (str, optional): Media type of the response. Defaults to None.
            background (BackgroundTask, optional): Background task to run. Defaults to None.
        """
        if isinstance(content, AsyncIterable):
            self._content_iterable: AsyncIterable = content
        else:
            self._content_iterable = iterate_in_threadpool(content)

        async def body_iterator() -> AsyncIterable[bytes]:
            async for content_ in self._content_iterable:
                if isinstance(content_, BaseModel):
                    content_ = content_.model_dump()
                yield self.render(content_)

        self.body_iterator = body_iterator()
        self.status_code = status_code
        if media_type is not None:
            self.media_type = media_type
        self.background = background
        self.init_headers(headers)


def chunk_to_json(chunk: dict, encoded: str, ignore_key:str =None) -> str:
    """
    Convert a chunk of data to a JSON-like string representation.

    Recursively converts dictionaries, lists, and primitive types 
    to a JSON-like string.

    Args:
        chunk (dict): The data chunk to convert.
        encoded (str): The initial encoded string.
        ignore_key (str, optional): A key to ignore during encoding. Defaults to None.

    Returns:
        str: A JSON-like string representation of the input chunk.
    """
    encoded = encoded + "{"
    def value_mapper(val: Any, encoded: str) -> str:
        """
        Map different value types to their string representations.

        Args:
            val (Any): The value to map.
            encoded (str): Current encoded string.

        Returns:
            str: Updated encoded string with the value.
        """
        if val is None:
            return f'{encoded}null'
        elif isinstance(val, int) or isinstance(val, float) or isinstance(val, str):
            return f'{encoded}"{val}"' 
        elif isinstance(val, bool):
            return f"{encoded}{'true' if val else 'false'}"
        else:
            return chunk_to_json(val, encoded, ignore_key)
    items = chunk.items() if isinstance(chunk, dict) else chunk.__dict__.items()
    for i, (atter, value) in enumerate(items):
        if atter == ignore_key:
            continue
        encoded = encoded + f'"{atter}":'
        if isinstance(value, list):
            encoded = encoded + "["
            for i, elem in enumerate(value):
                encoded = value_mapper(elem, encoded)
                if i < len(value) - 1:
                    encoded = f"{encoded},"
            encoded = f"{encoded}]"
        else:
            encoded = value_mapper(value, encoded)
        if i < len(items) - 1:
            encoded = f'{encoded},'
    return encoded + "}"
