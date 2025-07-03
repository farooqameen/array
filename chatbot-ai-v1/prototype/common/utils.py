from __future__ import annotations
import dotenv, logging, functools, os, json, sys, re
from enum import Enum, auto
from os.path import exists
import boto3
import pandas as pd
from io import StringIO
from langchain_core.language_models import LanguageModelLike
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import RetrieverLike, RetrieverOutputLike
from langchain_core.runnables import RunnableLambda


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Prototype")


class Credential(Enum):
    """
    Enum for various service credentials used in the application.
    """
    OPENAI = auto()
    LANGSMITH = auto()
    AWS = auto()
    HUGGINGFACE = auto()
    PINECONE = auto()
    CHAT_PARAMS_AWS = auto()
    AUTH_AWS = auto()
    DATASET_S3_BUCKET = auto()
    PINECONE_COHERE = auto()


# Mapping of credentials to their respective environment variable names
CRED_ENV_MAP = {Credential.LANGSMITH:['LANGCHAIN_API_KEY'],
                Credential.OPENAI:['OPENAI_API_KEY'],
                Credential.HUGGINGFACE:['HUGGINGFACE_API_WRITE_TOKEN', 'HUGGINGFACEHUB_API_TOKEN'],
                Credential.AWS:[],
                Credential.PINECONE:['PINECONE_API_KEY'],
                Credential.CHAT_PARAMS_AWS: ['CHAT_HISTORY_DB_NAME', 'HISTORY_SIZE', 'DEPLOYMENT_CONFIG_NAME'],
                Credential.DATASET_S3_BUCKET: ['DATASET_S3_BUCKET'],
                Credential.AUTH_AWS: ['API_AUTH_KEY'],
                Credential.PINECONE_COHERE:['PINECONE_COHERE_EMBED_KEY']} 

def store_env_var(name:str, value):
    """
    Stores the given value as an environment variable and updates the .env file.
    
    Args:
        name (str): The name of the environment variable.
        value (str): The value to be stored in the environment variable.
    """
    os.environ[name] = value
    # try:
    #     dotenv_file = dotenv.find_dotenv()
    #     dotenv.load_dotenv(dotenv_file)
    #     dotenv.set_key(dotenv_file, name, os.environ.get(name))
    # except Exception as e:
    #     pass

    
    
def validate_credential(creds: list[Credential]):
    """
    Decorator to validate the presence of required credentials.
    
    This decorator checks if the required credentials are stored in the environment variables.
    If any credential is missing, it prompts the user to input the missing credential and 
    stores it in the .env file.
    
    Args:
        creds (list[Credential]): A list of Credential enums to be validated.
        
    Returns:
        function: The decorated function with credential validation.
    """
    def validate_credential_inner(function):
        @functools.wraps(validate_credential)

        def wrapper(*args, **kwargs):
            # first load env variables if available (useful during local testing)
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            for cred in creds:
                # LOCAL_RUN must be set as env var in dockerfile during build time
                if 'LOCAL_RUN' in os.environ and Credential.AWS in creds: # check for existing AWS config and cred files
                    if not (exists(os.environ.get("AWS_SHARED_CREDENTIALS_FILE")) and exists(os.environ.get("AWS_CONFIG_FILE"))):
                        logger.error("One or more AWS credential files missing. Please ensure you have all .aws inside prototype dir. Refer to the wiki for more info.")
                        break
                for var in CRED_ENV_MAP[cred]:
                    # fetch variables from secrets manager ONLY IF not available in environment
                    if var not in os.environ:
                        if not fetch_from_secret_manager(var):
                            logger.error(f"Missing credentials. Please ensure ({var}) is fetched from SecretManager or available in .env")
            result = function(*args, **kwargs)
            return result
        
        return wrapper
    return validate_credential_inner

# Global variable to cache secrets
secrets_cache = {}

def fetch_from_secret_manager(variable_name):
    """
    Fetch env variable from AWS Secrets Manager or return from cache if already fetched.
    All secrets are stored in a single secret with key-value pairs.
    Fetched variable will be stored in os.env.

    Returns:
     True if successful
    """
    global secrets_cache

    # If secrets are already cached, return the value from the cache
    if secrets_cache:
        secret_val = secrets_cache.get(variable_name)
        if secret_val is not None:
            store_env_var(variable_name, secret_val)
            return True
        else:
            logger.warning(f"Variable {variable_name} not found in cached secrets.")
            return False
    
    # Secret name for backend secrets
    if ("ENV" in os.environ and os.environ.get('ENV') == 'PROD'):
        secret_name = "prod/chat-bot/backend"
    else:
        secret_name = "dev/chat-bot/backend"
    
    
    # Secret manager client
    session = get_aws_session_w_region()
    client = session.client(service_name='secretsmanager')

    try:
        # Retrieve the entire secret (key-value pairs)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_keyval_str = get_secret_value_response['SecretString']
        
        # Parse the secret string into a dictionary
        secrets_cache = json.loads(secret_keyval_str)
        
        # Extract the specific variable value
        secret_val = secrets_cache.get(variable_name)

        if secret_val is None:
            logger.warning(f"Variable {variable_name} not found in secret {secret_name}")
            return False
    except Exception as e:
        logger.warning(f"Failed to fetch secret {secret_name} from Secrets Manager: {e}")
        return False

    # Store the fetched secret in environment variable
    store_env_var(variable_name, secret_val)

    return True

    

def load_config(path: str = None) -> dict:
    """
    Loads config file as parsed by the input flag
        
    Returns:
        dict: config file loaded as a dictionary.
    """
    config = {}
    with open(path, "r") as config_file:
        config = json.load(config_file)

    chain_config = config["chain_config"] if "chain_config" in config else None
    test_config = config["test_config"] if "test_config" in config else None
    return (chain_config, test_config)


@validate_credential(creds=[Credential.DATASET_S3_BUCKET])
def s3_csv_to_set(s3_key: str) -> set:
    """
    Downloads a CSV file from S3 and converts the first column into a set.

    Args:
        s3_uri (str): The S3 URI of the CSV file (e.g., 's3://bucket-name/key/path/to/file.csv').

    Returns:
        set: A set containing the unique values from the first column of the CSV file.
        
    Raises:
        ValueError: If the CSV file is empty or does not contain any data.
    """
    dotenv.load_dotenv()
    session = get_aws_session_w_region()
    s3_client = session.client(service_name='s3')
    s3_bucket = os.environ.get('DATASET_S3_BUCKET')


    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    # Read the CSV file into a DataFrame
    df = pd.read_csv(StringIO(response['Body'].read().decode('utf-8')))
    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("The CSV file is empty or does not contain any data.")
    # Create a set from the first column's values
    result_set = {str(value).lower() for value in df.iloc[:, 0]}
    return result_set


def search_set(value_set: set, search_value: str) -> bool:
    """
    Searches for a specific value in a set and returns whether it exists.

    Args:
        value_set (set): The set to search within, where all values are lowercase.
        search_value (str): The value to search for in the set.

    Returns:
        bool: True if the search value is found in the set, False otherwise.
    """
    # Check if the lowercase search_value exists in the set
    return search_value.lower() in value_set


def get_aws_session_w_region():
    ''' Generate correct boto3 session depending on whether AWS_REGION is set in env variables '''
    dotenv.load_dotenv()
    if 'AWS_REGION' in os.environ:
        return boto3.session.Session(region_name=os.environ.get('AWS_REGION'))
    
    return boto3.session.Session()

def create_history_aware_retriever(
    llm: LanguageModelLike,
    retriever: RetrieverLike,
    prompt: BasePromptTemplate,
) -> RetrieverOutputLike:
    """ Create a chain that takes conversation history and returns documents.
        The prompt and LLM will be used to generate a search query. That search query is 
        then passed to the retriever.

    Args:
        llm: Language model to use for generating a search term given chat history
        retriever: RetrieverLike object that takes a string as input and outputs
            a list of Documents.
        prompt: The prompt used to generate the search query for the retriever.

    Returns:
        An LCEL Runnable. The runnable input must take in `input`, and if there
        is chat history should take it in the form of `chat_history`.
        The Runnable output is a list of Documents
    """
    if "input" not in prompt.input_variables:
        raise ValueError(
            "Expected `input` to be a prompt variable, "
            f"but got {prompt.input_variables}"
        )

    retrieve_documents: RetrieverOutputLike = RunnableLambda(
        lambda _: prompt | llm | StrOutputParser() | retriever
    ).with_config(run_name="chat_retriever_chain")
    return retrieve_documents