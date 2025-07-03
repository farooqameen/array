from langchain_core.documents import Document
import logging
from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import JSONResponse, StreamingResponse
from collections.abc import AsyncIterable, Iterable
import json, typing
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.documents import Document


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend_server")


def serialize_model(obj):
    if isinstance(obj, HumanMessage):
        return {"content": obj.content, "example": obj.example, "id": obj.id,"name": obj.name,"response_metadata": obj.response_metadata, "type":obj.type}
    elif isinstance(obj, AIMessage):
        return {"content": obj.content, "example": obj.example, "id": obj.id,"name": obj.name,"usage_metadata": obj.usage_metadata, "type":obj.type}
    elif isinstance(obj, Document):
        return {"metadata": obj.metadata, "type":obj.type}
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class JSONStreamingResponse(StreamingResponse, JSONResponse):
    """StreamingResponse that also render with JSON."""

    def render(self, content: typing.Any) -> bytes:
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
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
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


def chunk_to_json(chunk, encoded, ignore_key:str =None):
    encoded = encoded + "{"
    def value_mapper(val, encoded):
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
