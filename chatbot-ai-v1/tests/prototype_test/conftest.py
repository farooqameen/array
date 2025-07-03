import pytest
from prototype.common.chain_generator import AbstractSolution, Citation, ResultChunk
import sys, os
from datetime import datetime
from uuid import uuid4
from langsmith.schemas import Example, Run
from unittest.mock import Mock, patch, MagicMock



# Ensure the package's root directory is added to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prototype"))
)


class MockSolution(AbstractSolution):
    def __init__(self, param1):
        self.param1 = param1

    def test(self, inputs, list_context, ans_key, cnt_key):
        pass
    
    def _test(self, inputs, list_context, ans_key, cnt_key):
        pass
    
    def invoke(self, prompt):
        pass
    
    def _invoke(self, prompt):
        pass
    
    def stream(self, prompt):
        pass
    
@pytest.fixture
def fx_solution():
    return MockSolution(param1="test_param")


@pytest.fixture
def fx_sample_citation():
    mock_cit = MagicMock(Citation)
    mock_cit.extract_citations.return_value = [
        MagicMock(page_content="Page content example 1", metadata="Source example 1"),
        MagicMock(page_content="Page content example 2", metadata="Source example 2")
    ]
    return mock_cit

@pytest.fixture
def fx_sample_citation_simple_test():
    return [
        MagicMock(page_content="Page content example 1", metadata="Source example 1"),
        MagicMock(page_content="Page content example 2", metadata="Source example 2")
    ]


@pytest.fixture
def fx_chain():
    return MagicMock()
    
@pytest.fixture(autouse=True)
def fx_set_env_vars(request,monkeypatch):
        
    monkeypatch.setenv("AWS_PROFILE", "test-profile")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("PINECONE_API_KEY", "dummy-key")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "testing")
    yield

@pytest.fixture
def fx_run():
    """Fixture for mock Run object."""
    return Run(
        id=str(uuid4()),
        name="mock_run",
        start_time=datetime.now(),
        run_type="test_run",
        trace_id=str(uuid4()),
        inputs={
            'question': 'dummy question,'
        },
        outputs={
            'context': ["This is the mock context.",],
            'answer': "This is the mock answer."
        }
    )
    
@pytest.fixture
def fx_chat_openai(request):
    with patch("langchain_openai.ChatOpenAI") as mock:
        yield mock

@pytest.fixture
def fx_langchain_string_evaluator():
    with patch('langsmith.evaluation.LangChainStringEvaluator') as mock:
        yield mock

@pytest.fixture
def fx_example():
    with patch("langsmith.schemas.Example") as mock:
        yield mock

@pytest.fixture
def fx_logger_error(request):
    marker = request.node.get_closest_marker("logger_path_error")
    path = None
    if marker:
        if marker.args[0] == "evaluators":
            path = "prototype.evaluation.evaluators.logger.error"
        elif marker.args[0] == "chain_generator":
            path = "prototype.common.chain_generator.logger.error"
        elif marker.args[0] == "test":
            path = "prototype.evaluation.test.logger.error"
    
    if path:
        with patch(path) as mock:
            yield mock
    else:
        yield None
        
@pytest.fixture
def fx_logger_warning(request):
    marker = request.node.get_closest_marker("logger_path_warning")
    path = None
    if marker:
        if marker.args[0] == "evaluators":
            path = "prototype.evaluation.evaluators.logger.warning"
        elif marker.args[0] == "chain_generator":
            path = "prototype.common.chain_generator.logger.warning"
    
    if path:
        with patch(path) as mock:
            yield mock
    else:
        yield None