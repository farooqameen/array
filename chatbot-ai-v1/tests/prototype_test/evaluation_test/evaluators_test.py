import json
from numpy import empty
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from prototype.evaluation.evaluators import Evaluator, activate_evaluators, setup_evaluators
from langsmith.schemas import Example, Run
import numbers
from prototype.evaluation.deepeval_custom import ContextualRelevancyMetricCustom, ContextualRecallMetricCustom, ContextualPrecisionMetricCustom, HallucinationMetricCustom, FaithfulnessMetricCustom, GEvalCustom
from deepeval.metrics.contextual_relevancy import contextual_relevancy
from langchain_openai import ChatOpenAI
from openai._base_client import AsyncAPIClient
from prototype.common.utils import validate_credential
from openai import OpenAI 
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from openai import ChatCompletion
from langsmith.evaluation import LangChainStringEvaluator

@pytest.mark.logger_path_warning("evaluators")
def test_setup_evaluators_success(fx_logger_warning, fx_chat_openai, fx_langchain_string_evaluator):
    # mocked fixture values
    fx_logger_warning.return_value = MagicMock()
    fx_chat_openai.return_value = MagicMock()
    fx_langchain_string_evaluator.return_value = MagicMock()

    evaluators = setup_evaluators()

    assert len(evaluators) == 11
    assert evaluators[Evaluator.doc_relevance] is not None
    assert evaluators[Evaluator.hallucination] is not None
    
@pytest.mark.logger_path_warning("evaluators")
@patch("prototype.evaluation.evaluators.ChatOpenAI", autospec=True)    
def test_setup_evaluators_openai_failure(fx_chat_openai, fx_logger_warning, fx_langchain_string_evaluator):
    # mock a connection error when attempting to use ChatOpenAI
    fx_chat_openai.side_effect = Exception("Connection error")

    evaluators = setup_evaluators()

    # define the expected set of evaluators without the langchain evaluators
    expected_deep_eval_evaluators = {
        Evaluator.de_contextual_relevancy,
        Evaluator.de_contextual_recall,
        Evaluator.de_contextual_precision,
        Evaluator.de_hallucination,
        Evaluator.de_faithfulness,
        Evaluator.de_noise_awarness,
        Evaluator.de_correctness
    }

    # assertions
    assert len(evaluators) == len(expected_deep_eval_evaluators)
    assert all(evaluator in evaluators for evaluator in expected_deep_eval_evaluators)

    fx_logger_warning.assert_called_once_with("Failed to connect to open-ai, model gpt-4o for langchin evaulators. Other evaluators are unaffected")



@pytest.mark.logger_path_warning("evaluators")
@patch("deepeval.test_case.llm_test_case.LLMTestCase")
# parametrizing the test for the different custom evaluators
@pytest.mark.parametrize("evaluator_key, metric_class, expected_key", [
    ("de_correctness", GEvalCustom, "correctness(DE)"),
    ("de_noise_awarness", GEvalCustom, "noise_awareness(DE)"),
    ("de_faithfulness", FaithfulnessMetricCustom, "faithfulness(DE)"),
    ("de_hallucination", HallucinationMetricCustom, "hallucination(DE)"),
    ("de_contextual_precision", ContextualPrecisionMetricCustom, "contextual_precision(DE)"),
    ("de_contextual_recall", ContextualRecallMetricCustom, "contextual_recall(DE)"),
    ("de_contextual_relevancy", ContextualRelevancyMetricCustom, "contextual_relevancy(DE)")
])
def test_evaluator(mock_test_case, fx_chat_openai, fx_run, fx_example, evaluator_key, metric_class, expected_key):
    mock_metric = MagicMock(spec=metric_class)

    # setup the evaluators dictionary and assign the mock metric to the evaluator key
    evaluators_dict = setup_evaluators()
    evaluators_dict[evaluator_key] = mock_metric
    evaluator = getattr(Evaluator, evaluator_key)
    
    # mock the evaluator function and set its return value
    mock_evaluator_function = MagicMock(spec=evaluator)

    # call the mock evaluator function with the run and example fixtures
    result = mock_evaluator_function(fx_run, fx_example)
    score = result.measure()

    # assert that the result key and scores are returned
    assert result is not None 
    assert result['key'] is not None 
    assert result['score'] is not None 
    assert score is not None 


@pytest.mark.logger_path_warning("evaluators")
# different test cases to test activate_evaluators
@pytest.mark.parametrize("input_data, expected_log_warning", [
    ([], f"no evaluators were found in config file"),  
    (None, f"no evaluators were found in config file"), 
    (['de_contextual_recall','de_contextual_relevancy'], None),
    (['de_hallucination_metric', 'de_hallucination_m'], f"Some evaluators in config file were not activated") 
])
def test_activate_evaluators(fx_logger_warning, fx_langchain_string_evaluator, fx_chat_openai, input_data, expected_log_warning):
    fx_logger_warning.return_value = MagicMock()
    fx_chat_openai.return_value = MagicMock()
    fx_langchain_string_evaluator.return_value = MagicMock()

    activate_evaluators(input_data)
    if expected_log_warning:
        # for the parameters that will log an error
        fx_logger_warning.assert_any_call(expected_log_warning) 
    else:
        # ensure no warnings are logged for valid inputs
        fx_logger_warning.assert_not_called()
        
        