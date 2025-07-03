import pytest
import os
from unittest.mock import patch, MagicMock
from prototype.common.chain_generator import BedrockSolution, GPTPineconeSolution, ResultChunk


# Test for BedrockSolution class
@pytest.mark.parametrize("list_context", [(True), (False)])
@patch("boto3.session.Session")
@patch("prototype.common.chain_generator.AmazonKnowledgeBasesRetriever")
def test_bedrock_solution_init_chain(
    fx_amazon_knowledge_bases_retriever, fx_mock_boto3_session_good_response, list_context
):
    # Mock the necessary objects and methods
    fx_mock_boto3_session_good_response.return_value.client.return_value = MagicMock()
    BedrockSolution._profile_session = fx_mock_boto3_session_good_response
    fx_amazon_knowledge_bases_retriever.return_value = MagicMock()

    # Initialize BedrockSolution
    bedrock_solution = BedrockSolution(
        list_context=list_context, knowledge_base_id="TEST_ID"
    )

    # Assert that the AWS client was created correctly
    fx_mock_boto3_session_good_response.return_value.client.assert_called_once_with()

    # Assert that the retriever was created correctly
    fx_amazon_knowledge_bases_retriever.assert_called_once()

    # Assert the chain was set up correctly
    assert bedrock_solution.chain is not None


def test_invoke_internal_bedrock_sol(fx_mock_boto3_session_good_response, fx_amazon_knowledge_bases_retriever, fx_chain):
    # Initialize the BedrockSolution with a dummy knowledge base ID
    bedrock_solution = BedrockSolution(list_context=True, knowledge_base_id="dummy-id")    
    bedrock_solution.chain = fx_chain
    
    # Call the invoke_internal method with a test prompt
    result = bedrock_solution._invoke("test prompt")
    
    # Assert that the result is an instance of ResultChunk and that it has response and context
    assert isinstance(result, ResultChunk)
    assert result.has_response
    assert result.has_context

def test_test_internal_bedrock_sol(fx_mock_boto3_session_good_response, fx_amazon_knowledge_bases_retriever, fx_citation, fx_chain):
    bedrock_solution = BedrockSolution(list_context=True, knowledge_base_id="dummy-id")    
    bedrock_solution.chain = fx_chain
    
    # initialize input and call method to be tested
    inputs = {"question": "What is the rule?"}
    result = bedrock_solution._test(inputs)
    
    # Assert that the result contains the expected keys
    assert "answer" in result
    assert "context" in result


def test_stream_bedrock_sol(fx_mock_boto3_session_good_response, fx_amazon_knowledge_bases_retriever, fx_chain):
    bedrock_solution = BedrockSolution(list_context=True, knowledge_base_id="dummy-id")    
    bedrock_solution.chain = fx_chain
    
    result = bedrock_solution.stream("test_prompt")
    
    # Assert that the result is an instance of ResultChunk and that it has response and context
    assert isinstance(result, ResultChunk)
    assert result.has_response
    assert result.has_context


# Test for GPTPineconeSolution class
@pytest.mark.parametrize(
    "list_context, pinecone_key",
    [(True, "dummy_key"), (False, "dummy_key"), (True, None), (False, None)],
)
def test_gptpineconesolution_init_chain(fx_set_key, fx_load_dotenv, fx_find_dotenv, fx_store_env_var, fx_chat_openai, fx_pinecone_vectorstore, fx_openai_embeddings, list_context, pinecone_key,):
    # Mock the return values
    fx_chat_openai.return_value = MagicMock()
    fx_pinecone_vectorstore.return_value = MagicMock()
    fx_openai_embeddings.return_value = MagicMock()
    mock_index_instance = fx_pinecone_vectorstore.return_value
    mock_index_instance.query.return_value = MagicMock()

    # Mock the store_env_var to use the mocked set_key
    fx_store_env_var.side_effect = lambda key, value: os.environ.setdefault(
        key, value
    )

    # Call the constructor to test the initialization
    pinecone_solution = GPTPineconeSolution(
        list_context=list_context, pinecone_key=pinecone_key
    )

    # Assert the chain was set up correctly
    assert pinecone_solution.chain is not None

    
def test_test_internal_gpt_pinecone_sol(fx_set_key, fx_load_dotenv, fx_find_dotenv, fx_store_env_var, fx_chat_openai, fx_pinecone_vectorstore, fx_openai_embeddings):
    # Initialize the GPTPineconeSolution with a dummy Pinecone key
    gpt_pinecone_solution = GPTPineconeSolution(list_context=True, pinecone_key="dummy key")
    
    # Create a mock chain and mock the process_question method to return this mock chain
    mock_chain = MagicMock()
    
    with patch.object(gpt_pinecone_solution, 'process_question', return_value=mock_chain):
        # Initialize input and call the _test method
        inputs = {"question": "What is the rule?"}
        result = gpt_pinecone_solution._test(inputs)
    
    # Assert that the result contains the key "answer" and has an answer
    assert "answer" in result
    assert result["answer"]


def test_invoke_internal_gpt_pinecone_sol(fx_set_key, fx_load_dotenv, fx_find_dotenv, fx_store_env_var, fx_chat_openai, fx_pinecone_vectorstore, fx_openai_embeddings):
    gpt_pinecone_solution = GPTPineconeSolution(list_context=True, pinecone_key="dummy key")
    
    mock_chain = MagicMock()
    
    # Mock the process_question method to return the mock_chain
    with patch.object(gpt_pinecone_solution, 'process_question', return_value=mock_chain):
        result = gpt_pinecone_solution._invoke("test prompt")

    # assert that the result is an instance of ResultChunk and that it has response and context
    assert isinstance(result, ResultChunk)
    assert result.has_response
    assert result.has_context


def test_stream_gpt_pinecone_sol(fx_set_key, fx_load_dotenv, fx_find_dotenv, fx_store_env_var, fx_chat_openai, fx_pinecone_vectorstore, fx_openai_embeddings):
    gpt_pinecone_solution = GPTPineconeSolution(list_context=True, pinecone_key="dummy key")
    
    mock_chain = MagicMock()
    
    # Mock the process_question method to return the mock_chain
    with patch.object(gpt_pinecone_solution, 'process_question', return_value=mock_chain):
        result = gpt_pinecone_solution.stream("test prompt")
    
    # assert that the result is an instance of ResultChunk and that it has response and context
    assert isinstance(result, ResultChunk)
    assert result.has_response
    assert result.has_context