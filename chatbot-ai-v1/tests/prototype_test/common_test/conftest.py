import json
from unittest.mock import MagicMock, patch
import pytest

from prototype.common.chain_generator import (
    Citation,
    ResultChunk,
)
from langchain_core.documents import Document

from tests.prototype_test.conftest import MockSolution


@pytest.fixture
def fx_citation():
    with patch("prototype.common.chain_generator.Citation") as mock:
        yield mock


@pytest.fixture
def fx_amazon_knowledge_bases_retriever():
    with patch("prototype.common.chain_generator.AmazonKnowledgeBasesRetriever") as mock:
        yield mock

@pytest.fixture
def fx_mock_s3_client_good_response():
    mock_s3_client = MagicMock()

    mock_response = {
        "Body": MagicMock(
            read=MagicMock(
                return_value=json.dumps(
                    {
                        "metadataAttributes": {
                            "attribute1": "value1",
                            "attribute2": "value2",
                        }
                    }
                ).encode("utf-8")
            )
        )
    }
    mock_s3_client.get_object.return_value = mock_response
    return mock_s3_client


@pytest.fixture
def fx_mock_boto3_session_good_response(fx_mock_s3_client_good_response):
    with patch("boto3.session.Session") as mock_session:
        mock_session.return_value.client.return_value = fx_mock_s3_client_good_response
        yield mock_session


@pytest.fixture
def fx_mock_s3_client_bad_response():
    mock_s3_client = MagicMock()
    # mock_s3_client.get_object.return_value = {}
    mock_s3_client.get_object.side_effect = Exception("no key found")
    return mock_s3_client


@pytest.fixture
def fx_mock_boto3_session_bad_response(fx_mock_s3_client_bad_response):
    with patch("boto3.session.Session") as mock_session:
        mock_session.return_value.client.return_value = fx_mock_s3_client_bad_response
        yield mock_session


@pytest.fixture
def fx_set_env_vars(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "test-profile")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("PINECONE_API_KEY", "dummy-key")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")


# ResultChunk Samples
@pytest.fixture
def fx_result_chunk_with_response_and_context():
    result = {
        "response": {"key": "value"},
        "context": [
            Document(
                page_content="sample content",
                metadata={
                    "location": {
                        "s3Location": {"uri": '"s3://cbb-rulebook/sample-key"'}
                    }
                },
            )
        ],
    }
    return ResultChunk(result)


@pytest.fixture
def fx_result_chunk_with_only_response():
    result = {"response": {"key": "value"}}
    return ResultChunk(result)


@pytest.fixture
def fx_result_chunk_with_only_context():
    result = {
        "context": [
            Document(
                page_content="sample content",
                metadata={"location": {"s3Location": {"uri": "s3://bucket/key"}}},
            )
        ]
    }
    return ResultChunk(result)


@pytest.fixture
def fx_result_chunk_empty():
    result = {}
    return ResultChunk(result)


@pytest.fixture
def fx_result_chunk_with_multiple_doc_in_context():
    result = {
        "response": {"key": "value"},
        "context": [
            Document(
                page_content="sample content",
                metadata={
                    "location": {
                        "s3Location": {"uri": '"s3://cbb-rulebook/sample-key"'}
                    }
                },
            ),
            Document(
                page_content="sample content2",
                metadata={},
            ),
            Document(
                page_content="sample content3",
                metadata={
                    "location": {
                        "s3Location": {"uri": '"s3://cbb-rulebook/sample-key"'}
                    }
                },
            ),
        ],
    }
    return ResultChunk(result)


@pytest.fixture
def fx_result_chunk_with_no_doc_in_context():
    result = {
        "response": {"key": "value"},
        "context": [],
    }
    return ResultChunk(result)


# Citation Samples
@pytest.fixture
def fx_sample_citation():
    page_content = "sample content"
    metadata = {"location": {"s3Location": {"uri": "s3://sample-bucket/sample-key"}}}
    return Citation(page_content, metadata)


@pytest.fixture
def fx_sample_citation_empty_metadata():
    page_content = "sample content"
    metadata = {}
    return Citation(page_content, metadata)


@pytest.fixture
def fx_sample_citation_null_metadata():
    page_content = "sample content"
    metadata = None
    return Citation(page_content, metadata)

@pytest.fixture
def fx_openai_embeddings():
    with patch("prototype.common.chain_generator.OpenAIEmbeddings") as mock:
        yield mock

@pytest.fixture
def fx_pinecone_vectorstore():
    with patch("prototype.common.chain_generator.PineconeVectorStore") as mock:
        yield mock

@pytest.fixture
def fx_chat_openai():
    with patch("prototype.common.chain_generator.ChatOpenAI") as mock:
        yield mock

@pytest.fixture
def fx_store_env_var():
    with patch("prototype.common.utils.store_env_var") as mock:
        yield mock

@pytest.fixture
def fx_find_dotenv():
    with patch("dotenv.find_dotenv", return_value=".env") as mock:
        yield mock

@pytest.fixture
def fx_load_dotenv():
    with patch("dotenv.load_dotenv") as mock:
        yield mock

@pytest.fixture
def fx_set_key():
    with patch("dotenv.set_key") as mock:
        yield mock


