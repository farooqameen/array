"""
Application configuration settings.

Loads environment variables and defines project-wide constants for:
- OpenSearch connection
- File storage paths
- Logging configuration
- LLM and chunking behavior
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from opensearchpy import OpenSearch
from pydantic_settings import BaseSettings

# Load environment variables from a .env file
load_dotenv()


class AppSettings:
    """
    General application settings including file paths, logging,
    and document processing configurations.
    """

    PROJECT_NAME: str = "InvestigatorMind API"
    DESCRIPTION: str = (
        "Backend service for uploading PDFs and performing searches using OpenSearch."
    )
    VERSION: str = "1.0.0"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # Directory paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = PROJECT_ROOT / "documents"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    HRAG_INDEX_PATH: Path = PROJECT_ROOT / "storage/hrag_index"
    TRAD_RAG_INDEX_PATH: Path = PROJECT_ROOT / "storage/trad_rag_index"

    # LLM configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CHUNK_SIZES: List[int] = [2048, 512, 256]
    CHUNK_OVERLAP: int = 20

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: Path = PROJECT_ROOT / "logs" / "app.log"

    # AWS bedrock configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    AWS_SESSION_TOKEN: str = os.getenv("AWS_SESSION_TOKEN")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)
        self.HRAG_INDEX_PATH.mkdir(parents=True, exist_ok=True)
        self.TRAD_RAG_INDEX_PATH.mkdir(parents=True, exist_ok=True)


class OpenSearchSettings:
    """
    OpenSearch client configuration loaded from environment variables.
    """

    HOST: str = os.getenv("OPENSEARCH_HOST", "localhost")
    PORT: int = int(os.getenv("OPENSEARCH_PORT", 9200))
    USER: str = os.getenv("OPENSEARCH_USER")
    PASS: str = os.getenv("OPENSEARCH_PASS", "")
    USE_SSL: bool = os.getenv("OPENSEARCH_USE_SSL", "False").lower() == "true"
    VERIFY_CERTS: bool = os.getenv("OPENSEARCH_VERIFY_CERTS", "False").lower() == "true"
    ENDPOINT: str = os.getenv("OPENSEARCH_ENDPOINT", None)

    def get_client(self) -> OpenSearch:
        """
        Initializes and returns an OpenSearch client using provided credentials.
        """

    def get_client(self) -> OpenSearch:
        connection_args = {
            "http_auth": (self.USER, self.PASS),
            "use_ssl": self.USE_SSL,
            "verify_certs": self.VERIFY_CERTS,
            "ssl_assert_hostname": False,
            "ssl_show_warn": False,
        }

        if self.ENDPOINT:
            return OpenSearch(hosts=[self.ENDPOINT], **connection_args)
        else:
            return OpenSearch(
                hosts=[{"host": self.HOST, "port": self.PORT}], **connection_args
            )


# Global instances to be used throughout the app
settings = AppSettings()
opensearch_config = OpenSearchSettings()
