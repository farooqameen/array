from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings management class.

    Loads environment variables from .env file and allows overriding 
    with injected environment variables. Provides type-safe configuration 
    for various application components including logging, AWS services, 
    authentication, and deployment settings.
    
    """
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8'
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        json_schema_extra={"env": "LOG_LEVEL"},
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    # Environment
    env: str = Field(json_schema_extra={"type": "string", "env": "ENV"})

    # Cognito
    cognito_user_pool_id: str = Field(json_schema_extra={"type": "string", "env": "COGNITO_USER_POOL_ID"})
    cognito_client_app_id: str = Field(json_schema_extra={"type": "string", "env": "COGNITO_CLIENT_APP_ID"})

    # AWS
    default_aws_region: str = Field(json_schema_extra={"type": "string", "env": "DEFAULT_AWS_REGION"})
    default_bedrock_region: str = Field(json_schema_extra={"type": "string", "env": "DEFAULT_BEDROCK_REGION"})

    # S3
    dataset_s3_bucket: str = Field(json_schema_extra={"type": "string", "env": "DATASET_S3_BUCKET"})

    # Pinecone
    pinecone_api_key: str = Field(json_schema_extra={"type": "string", "env": "PINECONE_API_KEY"})
    pinecone_cohere_embed_key: str = Field(json_schema_extra={"type": "string", "env": "PINECONE_COHERE_EMBED_KEY"})

    #langsmith
    langsmith_tracing_v2: bool = Field(json_schema_extra={"type": "bool", "env": "LANGSMITH_TRACING_V2"})

    # Chat History
    chat_history_db_name: str = Field(json_schema_extra={"type": "string", "env": "CHAT_HISTORY_DB_NAME"})

    # OpenAI
    openai_api_key: str = Field(json_schema_extra={"type": "string", "env": "OPENAI_API_KEY"})

    # API Auth
    api_auth_key: str = Field(json_schema_extra={"type": "string", "env": "API_AUTH_KEY"})

    #opensearch
    opensearch_endpoint: str = Field(json_schema_extra={"type": "string", "env": "OPENSEARCH_ENDPOINT"})
    opensearch_index: str = Field(json_schema_extra={"type": "string", "env": "OPENSEARCH_INDEX"})
    opensearch_user: str = Field(json_schema_extra={"type": "string", "env": "OPENSEARCH_USER"})
    opensearch_password: str = Field(json_schema_extra={"type": "string", "env": "OPENSEARCH_PASSWORD"})

    # Configuration
    host: str = Field(json_schema_extra={"type": "string", "env": "HOST"})
    port: int = Field(json_schema_extra={"type": "integer", "env": "PORT"})
    history_size: int = Field(json_schema_extra={"type": "integer", "env": "HISTORY_SIZE"})
    deployment_config_name: str = Field(json_schema_extra={"type": "string", "env": "DEPLOYMENT_CONFIG_NAME"})

settings = Settings()