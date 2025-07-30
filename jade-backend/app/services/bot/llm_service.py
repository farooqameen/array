"""
Service module for initializing LLM and embedding models.

This module configures the global LlamaIndex settings to use
AWS Bedrock models for both language and embedding tasks.
"""

from config.settings import settings
from llama_index.core.settings import Settings
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock
from logger import logger


def initialize_llm_settings():
    """
    Initialize global LLM and embedding models for use in LlamaIndex.

    Sets the default LLM and embedding model to use AWS Bedrock (Claude 3.7 sonnet),
    using the AWS credentials key configured in environment variables.

    Raises:
        ValueError: If AWS credentials are not set in the environment.
        RuntimeError: If initialization of LLM or embedding model fails.
    """

    try:
        llm = Bedrock(
            model=settings.LLM_MODEL,
            region_name=settings.AWS_REGION,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            context_size=settings.LLM_CONTEXT_SIZE,
        )
        embed_model = BedrockEmbedding(
            model=settings.LLAMAINDEX_EMBEDDING_MODEL,
            region_name=settings.AWS_REGION,
        )

        Settings.llm = llm
        Settings.embed_model = embed_model
        logger.info(
            "LlamaIndex LLM and Embedding models initialized successfully with AWS Bedrock."
        )

    except Exception as exc:
        logger.critical(
            "Failed to initialize LLM and embedding models: %s", exc, exc_info=True
        )
        raise RuntimeError(
            "Failed to initialize LLM services. Check AWS credentials and network."
        ) from exc
