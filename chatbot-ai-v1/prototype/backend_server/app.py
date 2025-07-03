from time import sleep
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from contextlib import asynccontextmanager
from backend_server.auth import auth
import logging, dotenv, uvicorn, os
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import (DynamoDBChatMessageHistory,)
from .schema import RequestBody
from common.utils import validate_credential, Credential, load_config
from fastapi.middleware.cors import CORSMiddleware
from common.chain_generator import generate_chain
from sse_starlette import EventSourceResponse
from typing import AsyncIterator, Any
from .utils import serialize_model
import json, orjson


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend_server")

# Hard-coded values
PORT = 8000
HOST = "0.0.0.0"

# Fetched from AWS SecretsS
DEPLOYMENT_CONFIG_NAME = None
CHAT_HISTORY_DB_NAME = None
HISTORY_SIZE = None

# dynamic globals
g_solution = None
g_title_chain = None


# will ensure required creds are available in env (YOU CAN OVERRIDE VALUES FETCHED FROM SECRETS BY SETTING ENV VARIABLES INSIDE .env)
@asynccontextmanager
@validate_credential(creds=[Credential.CHAT_PARAMS_AWS, Credential.AUTH_AWS])
async def lifespan(app: FastAPI):
    '''
    startup function [NOTE: If any unacaught exception occurs, the server will not startup]

    '''
    # startup logic
    global PORT
    global HOST
    global CHAT_HISTORY_DB_NAME
    global DEPLOYMENT_CONFIG_NAME
    global HISTORY_SIZE
    global g_solution
    global g_title_chain
    

    if 'PORT' in os.environ:
        PORT = os.environ.get('PORT')
    if 'HOST' in os.environ:
        HOST = os.environ.get('HOST')
    if 'CHAT_HISTORY_DB_NAME' in os.environ:
        CHAT_HISTORY_DB_NAME = os.environ.get('CHAT_HISTORY_DB_NAME')
    if 'DEPLOYMENT_CONFIG_NAME' in os.environ:
        DEPLOYMENT_CONFIG_NAME = os.environ.get('DEPLOYMENT_CONFIG_NAME')
    if 'HISTORY_SIZE' in os.environ:
        try:
            HISTORY_SIZE = int(os.environ.get('HISTORY_SIZE'))
        except Exception as e:
            logger.error(f"Failed to convert HISTORY_SIZE to int, setting default to 10: {e}")
            HISTORY_SIZE = 10
            pass


    # load default chain
    logger.info(f"default config file: {DEPLOYMENT_CONFIG_NAME}")
    chain_config, _ = load_config(DEPLOYMENT_CONFIG_NAME)
    if chain_config:
        logger.info(f" default config chain: {chain_config}")
        g_solution = generate_chain(chain_config)
        g_title_chain = g_solution.get_chain_title()
    else:
        logger.error(f"chain config not found in default config file {DEPLOYMENT_CONFIG_NAME}")
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
    '''
    ping endpoint to check on server's health during deployment

    '''
    return {"health": "OK!"}


async def stream_generator_esr(
            chain_with_history,
            question: str,
            session_id: str,
            user_id: str,
            chain_title,
            generate_title: bool,
    ) -> AsyncIterator[dict]:
        '''Generates response stream'''

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


def configure_chain_with_history(chain_with_history, _session_id:str, user_id:str):
    '''finalize chain with history'''

    return RunnableWithMessageHistory(
        chain_with_history,
        lambda session_id: DynamoDBChatMessageHistory(
            table_name=CHAT_HISTORY_DB_NAME, 
            session_id=_session_id,
            history_size= HISTORY_SIZE,
            key={"SessionId":_session_id, "UserId":user_id}
        ),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


def configure_chain_title(chain_title, _session_id:str, user_id:str):
    '''finalize chain for title'''

    return RunnableWithMessageHistory(
        chain_title,
        lambda session_id: DynamoDBChatMessageHistory(
            table_name=CHAT_HISTORY_DB_NAME, 
            session_id=_session_id,
            history_size= HISTORY_SIZE,
            key={"SessionId":_session_id, "UserId":user_id}
        ),
        input_messages_key="input",
        history_messages_key="chat_history",
    )

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
    '''
    stream a response in json chunks. Provides context, answer, and optional conversation title.
    Data-events will contain context, answer or title individually and in json-parsable format. No more than one key will be provided per a single chunk
    '''

    """Handle a request."""
    question = request_body.input.question
    session_id = request_body.input.session_id
    user_id = request_body.input.user_id
    generate_title = request_body.input.generate_title

    rag_chain = g_solution.get_chain_with_history(question=question)
    
    ready_chain_with_history = configure_chain_with_history(chain_with_history=rag_chain,
                                _session_id=session_id,
                                user_id=user_id
                            )
    
    ready_chain_title = configure_chain_title(
                                chain_title=g_title_chain,
                                _session_id=session_id,
                                user_id=user_id
                            )
    
    return EventSourceResponse(stream_generator_esr(question= question,
                                                    session_id= session_id,
                                                    user_id= user_id,
                                                    generate_title= generate_title,
                                                    chain_with_history= ready_chain_with_history,
                                                    chain_title= ready_chain_title
                                                    ))



if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)