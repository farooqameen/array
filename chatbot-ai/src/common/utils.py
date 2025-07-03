from __future__ import annotations
import json, boto3
import pandas as pd
from io import StringIO
from langchain_core.language_models import LanguageModelLike
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import RetrieverLike, RetrieverOutputLike
from langchain_core.runnables import RunnableLambda
from src.logs import logger
from src.settings import settings

def load_config(path: str = None) -> tuple[dict, dict]:
    """
    Load configuration from a JSON file.

    Args:
        path (str, optional): Path to the configuration file. 
            Defaults to None.

    Returns:
        tuple: A tuple containing two elements:
            - chain_config (dict or None): Configuration for the chain
            - test_config (dict or None): Configuration for testing
    """
    config = {}
    with open(path, "r") as config_file:
        config = json.load(config_file)

    chain_config = config["chain_config"] if "chain_config" in config else None
    test_config = config["test_config"] if "test_config" in config else None
    return (chain_config, test_config)


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
    # dotenv.load_dotenv()
    session = get_aws_session_w_region()
    s3_client = session.client(service_name='s3')
    s3_bucket = settings.dataset_s3_bucket

    try:
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    except Exception as e:
        logger.error(f"{e}")
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


def get_aws_session_w_region(region_name: str = settings.default_aws_region) -> boto3.Session:
    """
    Generate a boto3 session with the specified AWS region.

    Args:
        region_name (str, optional): AWS region name. 
            Defaults to the value of settings.default_aws_region.

    Returns:
        boto3.Session: A boto3 session configured with the specified region.
    """
    return boto3.session.Session(region_name=region_name)
    
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