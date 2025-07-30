"""
Application configuration settings.

Loads environment variables and defines project-wide constants for:
- OpenSearch connection
- File storage paths
- Logging configuration
- LLM and chunking behavior
"""

from pathlib import Path
from typing import List, Optional

from opensearchpy import OpenSearch
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    General application settings including file paths, logging,
    and document processing configurations.
    """

    PROJECT_NAME: str = Field(
        default="Universal Search Backend", description="Application name"
    )
    DESCRIPTION: str = Field(
        default="Backend service for uploading PDFs and performing searches using OpenSearch.",
        description="Application description",
    )
    VERSION: str = Field(default="1.0.0", description="Application version")
    FRONTEND_ORIGIN: str = Field(
        default="http://localhost:3000", description="Frontend URL for CORS"
    )

    PDF_PARSER_SERVICE_URL: str = Field(
        default="http://localhost:8001/api/parse", description="PDF parser service URL"
    )
    PDF_PARSER_TIMEOUT: int = Field(
        default=30, gt=0, le=300, description="PDF parser timeout in seconds"
    )

    # LLM configuration
    LLM_MODEL: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="LLM model identifier",
    )
    CHUNK_SIZES: List[int] = Field(
        default=[1024, 512, 256], description="Text chunking sizes"
    )
    CHUNK_OVERLAP: int = Field(
        default=100, ge=0, description="Overlap between text chunks"
    )

    # LLM runtime parameters
    LLM_MAX_TOKENS: int = Field(
        default=2048, description="Maximum tokens for LLM responses"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.1, description="Temperature for LLM generation"
    )
    LLM_CONTEXT_SIZE: int = Field(default=200000, description="Context size for LLM")

    # Different embedding models for LlamaIndex and LangChain
    LLAMAINDEX_EMBEDDING_MODEL: str = Field(
        default="cohere.embed-multilingual-v3",
        description="Embedding model identifier for LlamaIndex",
    )

    LANGCHAIN_EMBEDDING_MODEL: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="Embedding model identifier for LangChain",
    )

    AWS_REGION: str = Field(default="us-west-2", description="AWS region for services")

    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    # If the computed_field decorator is applied to a bare function (e.g. a function without the @property or @cached_property decorator)
    # it will wrap the function in property itself. Although this is more concise, you will lose IntelliSense in your IDE,
    # and confuse static type checkers, thus explicit use of @property is recommended.
    # See: https://docs.pydantic.dev/2.3/usage/computed_fields/

    @computed_field
    @property
    def PROJECT_ROOT(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @computed_field
    @property
    def UPLOAD_DIR(self) -> Path:
        path = self.PROJECT_ROOT / "documents"
        path.mkdir(exist_ok=True)
        return path

    @computed_field
    @property
    def DATA_DIR(self) -> Path:
        path = self.PROJECT_ROOT / "documents"
        path.mkdir(exist_ok=True)
        return path

    @computed_field
    @property
    def HRAG_INDEX_PATH(self) -> Path:
        path = self.PROJECT_ROOT / "storage/hrag_index"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @computed_field
    @property
    def TRAD_RAG_INDEX_PATH(self) -> Path:
        path = self.PROJECT_ROOT / "storage/trad_rag_index"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @computed_field
    @property
    def CSV_INDEX_DIR(self) -> Path:
        path = self.PROJECT_ROOT / "storage/csv_index"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @computed_field
    @property
    def LOG_FILE(self) -> Path:
        path = self.PROJECT_ROOT / "logs" / "app.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class S3Settings(BaseSettings):
    """
    S3 storage configuration.
    """

    BUCKET_NAME: str = Field(
        default="universal-search-uploads",
        description="S3 bucket name for file uploads",
    )

    model_config = {
        "extra": "ignore",
        "env_prefix": "S3_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


class OpenSearchSettings(BaseSettings):
    """
    OpenSearch client configuration loaded from environment variables.
    """

    HOST: str = Field(default="localhost", description="OpenSearch host")
    PORT: int = Field(default=9200, gt=0, le=65535, description="OpenSearch port")
    USER: Optional[str] = Field(default=None, description="OpenSearch username")
    PASS: str = Field(default="", description="OpenSearch password")
    USE_SSL: bool = Field(default=False, description="Use SSL connection")
    VERIFY_CERTS: bool = Field(default=False, description="Verify SSL certificates")
    ENDPOINT: Optional[str] = Field(
        default=None, description="Full OpenSearch endpoint URL"
    )

    model_config = {
        "extra": "ignore",
        "env_prefix": "OPENSEARCH_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def get_client(self) -> OpenSearch:
        """
        Initializes and returns an OpenSearch client using provided credentials.
        """
        connection_args = {
            "use_ssl": self.USE_SSL,
            "verify_certs": self.VERIFY_CERTS,
            "ssl_assert_hostname": False,
            "ssl_show_warn": False,
        }

        # Only add authentication if both user and password are provided
        if self.USER and self.PASS:
            connection_args["http_auth"] = (self.USER, self.PASS)  # type: ignore

        if self.ENDPOINT:
            return OpenSearch(hosts=[self.ENDPOINT], **connection_args)  # type: ignore
        else:
            return OpenSearch(
                hosts=[{"host": self.HOST, "port": self.PORT}],
                **connection_args,  # type: ignore
            )


# Global instances to be used throughout the app
settings = AppSettings()
s3_config = S3Settings()
opensearch_config = OpenSearchSettings()
