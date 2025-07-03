from botocore.config import Config

S3_DATA_SOURCE = "arn:aws:s3:::cbb-rulebook/"
BEDROCK_MODEL_IDS = {
    "Titan Text G1 - Express": "amazon.titan-text-express-v1",
    "Titan Text G1 - Lite": "amazon.titan-text-lite-v1",
    "Titan Text Premier": "amazon.titan-text-premier-v1:0",
    "Titan Embeddings G1 - Text": "amazon.titan-embed-text-v1",
    "Titan Embedding Text v2": "amazon.titan-embed-text-v2:0",
    "Titan Multimodal Embeddings G1": "amazon.titan-embed-image-v1",
    "Titan Image Generator G1": "amazon.titan-image-generator-v1",
    "Claude": "anthropic.claude-v2",
    "Claude": "anthropic.claude-v2:1",
    "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "Claude 3 Opus": "anthropic.claude-3-opus-20240229-v1:0",
    "Claude Instant": "anthropic.claude-instant-v1",
    "Jurassic-2 Mid": "ai21.j2-mid-v1",
    "Jurassic-2 Ultra": "ai21.j2-ultra-v1",
    "Command": "cohere.command-text-v14",
    "Command Light": "cohere.command-light-text-v14",
    "Command R": "cohere.command-r-v1:0",
    "Command R+": "cohere.command-r-plus-v1:0",
    "Embed English": "cohere.embed-english-v3",
    "Embed Multilingual": "cohere.embed-multilingual-v3",
    "Llama 2 Chat 13B": "meta.llama2-13b-chat-v1",
    "Llama 2 Chat 70B": "meta.llama2-70b-chat-v1",
    "Llama 3 8b Instruct": "meta.llama3-8b-instruct-v1:0",
    "Llama 3 70b Instruct": "meta.llama3-70b-instruct-v1:0",
    "Llama 3.1 405b Instruct": "meta.llama3-1-405b-instruct-v1:0",
    "Mistral 7B Instruct": "mistral.mistral-7b-instruct-v0:2",
    "Mixtral 8X7B Instruct": "mistral.mixtral-8x7b-instruct-v0:1",
    "Mistral Large": "mistral.mistral-large-2402-v1:0",
    "Mistral Small": "mistral.mistral-small-2402-v1:0",
    "Stable Diffusion XL": "stability.stable-diffusion-xl-v0",
    "Stable Diffusion XL": "stability.stable-diffusion-xl-v1",
    "Llama 3.2 3b Instruct":"us.meta.llama3-2-3b-instruct-v1:0"
}
LANGSMITH_SPLIT_TIME_BUFF = 15
CONFIG_VAR_NAME = "CONFIG"

BOTO_CONFIG = Config(
    max_pool_connections=50,
    retries = {
      'max_attempts': 10,
      'mode': 'standard'
   }
)