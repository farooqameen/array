# chat-bot-v2


### .env
```
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_APP_ID=
DEFAULT_AWS_REGION="me-south-1"
DEFAULT_BEDROCK_REGION="us-west-2"
DATASET_S3_BUCKET="cbb-chatbot-dataset"
PINECONE_API_KEY=
CHAT_HISTORY_DB_NAME="chatbot-chat-history"
OPENAI_API_KEY=
HISTORY_SIZE="10"
DEPLOYMENT_CONFIG_NAME="src/config/config_BedrockOpensearch.json"
PINECONE_COHERE_EMBED_KEY=
LOG_LEVEL = "INFO"
LANGSMITH_TRACING_V2=false
ENV=LOCAL
PORT = 8000
HOST = "0.0.0.0"
OPENSEARCH_ENDPOINT=
OPENSEARCH_USER="admin"
OPENSEARCH_PASSWORD=
OPENSEARCH_INDEX="cbb_v2_0"
```

### Execute: run following command in devcontainer
`aws configure sso` -- follow prompt
`aws sso login`
`pipenv run python -m src.backend_server.app`