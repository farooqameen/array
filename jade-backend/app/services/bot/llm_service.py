"""
Service module for initializing LLM and embedding models.

This module configures the global LlamaIndex settings to use
Google Gemini models for both language and embedding tasks.
"""

import os
from llama_index.core.settings import Settings
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from config.settings import settings
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
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID
    aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
    aws_region = settings.AWS_REGION
    aws_session = settings.AWS_SESSION_TOKEN
    

    if not (aws_access_key_id and aws_secret_key):
        logger.critical(
            "AWS credentials not found in environment variables. Please set it in your .env file."
        )
        raise ValueError("AWS credentials not set.")

    try:
        llm = Bedrock(
            model = "anthropic.claude-3-5-sonnet-20241022-v2:0",
            region_name= aws_region,
            max_tokens = 200,
            temperature = 0.1,
            context_size = 200000,
            # aws_access_key_id = aws_access_key_id,
            # aws_secret_access_key = aws_secret_key,

        )
        embed_model = BedrockEmbedding(
            model = "cohere.embed-multilingual-v3",
            region_name= aws_region,
            # aws_access_key_id = aws_access_key_id,
            # aws_secret_access_key = aws_secret_key,
            # aws_session_token = aws_session,
        )


        Settings.llm = llm
        Settings.embed_model = embed_model
        logger.info(
            "LlamaIndex LLM and Embedding models initialized successfully with AWS Bedrock."
        )

    except Exception as e:
        logger.critical(
            f"Failed to initialize LLM and embedding models: {e}", exc_info=True
        )
        raise RuntimeError(
            "Failed to initialize LLM services. Check AWS credentials and network."
        )
