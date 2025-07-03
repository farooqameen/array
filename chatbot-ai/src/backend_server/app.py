from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import uvicorn, json, orjson
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from typing import AsyncIterator, Any
from src.backend_server.utils import serialize_model
from src.logs import logger
from src.settings import settings
from src.common.chain_generator import generate_chain
from src.common.utils import load_config
from src.backend_server.auth import auth
from src.backend_server.schema import RequestBody

# dynamic globals
g_solution = None

# will ensure required creds are available in env (YOU CAN OVERRIDE VALUES FETCHED FROM SECRETS BY SETTING ENV VARIABLES INSIDE .env)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifecycle of the FastAPI application during startup.

    This async context manager is responsible for initializing the global solution
    by loading the default chain configuration. If any uncaught exception occurs 
    during initialization, the server will not start up.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        Exception: If there's an error loading the configuration file.

    Yields:
        None: Allows the application to continue its startup process.
    """
    global g_solution
    # load default chain
    try:
        logger.info(f"default config file: {settings.deployment_config_name}")
        chain_config, _ = load_config(settings.deployment_config_name)
    except Exception as e:
        logger.info(f"failed to load config file {settings.deployment_config_name}")
        raise
    logger.info(f" default config chain: {chain_config}")
    g_solution = generate_chain(chain_config)
    yield


app=FastAPI(
    title="Langserve chatbot server",
    version="1.0",
    decsription="chatbot server",
    lifespan=lifespan
)


# enable CORS
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )


@app.get("/health")
async def health():
    """
    Health check endpoint to verify server status during deployment.

    Returns:
        dict: A dictionary indicating the server's health status.
    """
    return {"health": "OK!"}


async def stream_generator_esr(
            chain_with_history,
            question: str,
            session_id: str,
            user_id: str,
            chain_title,
            generate_title: bool,
    ) -> AsyncIterator[dict]:
        """
        Generate a streaming response for the chatbot.

        This asynchronous generator yields tokens from the chain response, 
        including context and answer. Optionally generates a conversation title.

        Args:
            chain_with_history: The language chain with conversation history.
            question (str): The user's input question.
            session_id (str): Unique identifier for the conversation session.
            user_id (str): Unique identifier for the user.
            chain_title: The chain responsible for generating conversation titles.
            generate_title (bool): Flag to determine if a title should be generated.

        Yields:
            dict: Streaming response tokens containing context, answer, or title.
                Includes error handling for stream generation.
        """
        logger.info("started streaming a response")
        try:
            async for token in chain_with_history.astream({"input": question},
                config={
                    "configurable": {"session_id": session_id, "user_id":user_id}
                }):
                if 'context' in token or 'answer' in token:
                    yield {
                        "data": orjson.dumps(
                            g_solution.parse_context(token) if 'context' in token else token,
                            default=serialize_model).decode("utf-8"),
                        "event": "data",
                    }
                #await asyncio.sleep(CHUNK_BUFFER_TIME_S)
            if generate_title:
                async for token in chain_title.astream({"input": "."},
                    config={
                        "configurable": {"session_id": session_id, "user_id":user_id}
                    }):
                    yield {
                        "data": orjson.dumps(
                                {"title":token},
                                default=serialize_model).decode("utf-8"),
                        "event": "data",
                    }

        except Exception as e:
            logger.error(f"Caught exception: {e}")
            yield {
                "event": "error",
                "data": json.dumps(
                    {"status_code": 500, "message": "Internal Server Error"}
                ),
            }
        finally:
            logger.info("finished streaming a response")
            yield {"event": "end"}




@app.post(f"/stream", responses={
    200:{
        "description": "streaming successful",
        "content": {
            "text/event-stream": {
                "example": (
                    "data: {\n"
                        "\"context\": [\n"
                        "     {\n"
                        "       \"metadata\": {\n"
                        "         \"link\": \"https://example.com\",\n"
                        "         \"name\": \"page.md\",\n"
                        "         \"path\": \"book/Part A/Title1/subfolder/subfolder/page.html\"\n"
                        "       },\n"
                        "       \"type\": \"Document\"\n"
                        "     }\n"
                        "   ],\n"
                        "   \"answer\": \"answer chunk\",\n"
                        "   \"title\": \"title chunk\"\n"
                    "},\n"
                    "error : {\"error\": \"answer generator error\"},\n"
                    "end: {\"null\": \"event: stream ended\"}\n"
                )
            }
        }
    }
})
async def stream(request_body: RequestBody,
                 _ = Depends(auth)
        ) -> EventSourceResponse:
    """
    Request handler: Stream a response in JSON chunks with context, answer, and optional conversation title.

    This endpoint provides a server-sent events (SSE) stream of response data. 
    Each data event will contain either context, answer, or title in a JSON-parsable format.
    Only one key will be provided per chunk.

    Args:
        request_body (RequestBody): The input request containing query parameters.
        _ (Any, optional): Authentication dependency. Defaults to auth check.

    Returns:
        EventSourceResponse: A streaming response with JSON-formatted data events.
    """
    input = request_body.input

    ready_chain_with_history = g_solution.get_history_aware_chain(
        user_id=input.user_id,
        volume_display_name=input.volume_display_name,
        subvolume_display_name=input.subvolume_display_name,
        category_display_name=input.category_display_name,
        module_display_name=input.module_display_name,
        chapter_display_name=input.chapter_display_name,
        section_display_name=input.section_display_name
        )

    ready_chain_title = g_solution.get_title_chain(
                                _session_id=input.session_id,
                                user_id=input.user_id
                            )
    
    return EventSourceResponse(
        stream_generator_esr(
            question= input.question,
            session_id= input.session_id,
            user_id= input.user_id,
            generate_title= input.generate_title,
            chain_with_history= ready_chain_with_history,
            chain_title= ready_chain_title,
        )
    )

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)