import json
import os
import pytest
from unittest import mock
from unittest.mock import mock_open, patch, MagicMock, Mock
from prototype.common.chain_generator import Citation
from prototype.evaluation.test import run_test, main
from prototype.common.constants import CONFIG_VAR_NAME, LANGSMITH_SPLIT_TIME_BUFF
from tests.prototype_test.conftest import MockSolution, fx_sample_citation, fx_sample_citation_simple_test
from tests.prototype_test.evaluation_test.conftest import fx_config_bedrock


def test_run_test_no_split(fx_evaluate, fx_client, fx_config_bedrock):

    automated_test_config = fx_config_bedrock["automated_test_config"]

    dataset_name = automated_test_config["dataset_name"]
    evaluators = automated_test_config["evaluators"]
    split_data = False
    split_time_buff = automated_test_config["split_time_buff"]
    per_q_repeat = automated_test_config["per_q_repeat"]
    experiment_name = automated_test_config["experiment_name"]
    splits = automated_test_config["splits"]

    fx_client.return_value = MagicMock()
    fx_evaluate.return_value = MagicMock()

    # Create a mock client and set its return value
    mock_client_instance = MagicMock()
    mock_client_instance.list_examples.return_value = []
    fx_client.return_value = mock_client_instance

    run_test(
        MockSolution("param1 value"),
        dataset_name= dataset_name,
        split_data= split_data,
        per_q_repeat= per_q_repeat,
        split_time_buff= split_time_buff,
        experiment_name= experiment_name,
        evaluators= evaluators,
        splits= splits
    )

    # assert evaluation was done the same number of times as there are evaluators (here 1)
    assert fx_evaluate.call_count == 1

# Test case when split_data is True
def test_run_test_with_split(fx_evaluate, fx_client, fx_config_gptpinecone):

    automated_test_config = fx_config_gptpinecone["automated_test_config"]

    dataset_name = automated_test_config["dataset_name"]
    split_data = automated_test_config["split_data"]
    per_q_repeat = automated_test_config["per_q_repeat"]
    split_time_buff = automated_test_config["split_time_buff"]
    evaluators = automated_test_config["evaluators"]
    experiment_name = automated_test_config["experiment_name"]
    splits = automated_test_config["splits"]

    fx_client.return_value = MagicMock()
    fx_evaluate.return_value = MagicMock()

    run_test(
        MockSolution("param1 value"),
        dataset_name= dataset_name,
        split_data= split_data,
        per_q_repeat= per_q_repeat,
        split_time_buff= split_time_buff,
        experiment_name= experiment_name,
        evaluators= evaluators,
        splits= splits,
    )

    # Assert that evaluate has been called for all splits
    assert fx_evaluate.call_count == len(splits)


# Test case when split_data is True but no splits defined
def test_run_test_with_split_no_splits(fx_evaluate, fx_client, fx_config_bedrock):

    automated_test_config = fx_config_bedrock["automated_test_config"]

    dataset_name = automated_test_config["dataset_name"]
    split_data = automated_test_config["split_data"]
    per_q_repeat = automated_test_config["per_q_repeat"]
    split_time_buff = automated_test_config["split_time_buff"]
    experiment_name = automated_test_config["experiment_name"]
    evaluators = automated_test_config["evaluators"]
    splits = None # No splits defined

    fx_client.return_value = MagicMock()
    fx_evaluate.return_value = MagicMock()

    run_test(
        MockSolution("param1 value"),
        dataset_name= dataset_name,
        split_data= split_data,
        per_q_repeat= per_q_repeat,
        split_time_buff= split_time_buff,
        experiment_name= experiment_name,
        evaluators= evaluators,
        splits= splits
    )

    # Assert that evaluate didn't get called
    assert fx_evaluate.call_count == 0


# test case for when some configuration in 'automated_test_configuration' are missing
@pytest.mark.logger_path_error("test")
def test_run_test_with_missing_config(fx_logger_error ,fx_evaluate, fx_client, fx_config_missing_configs):

    # setup configuration (with some missing configs)
    automated_test_config = fx_config_missing_configs["automated_test_config"]

    # mocked langchain client and the evaluation of it
    fx_client.return_value = MagicMock()
    fx_evaluate.return_value = MagicMock()
    
    run_test(
        MockSolution("param1 value"),
        automated_test_config= automated_test_config
    )

    #assert error has been called for missing configs
    fx_logger_error.assert_called_with("Some automated test config are missing. Exiting...")
    

#test case for no chain configuration are found
@pytest.mark.logger_path_error("chain_generator")
@patch('os.path.isfile', return_value=True)
@patch("builtins.open", new_callable=mock.mock_open, read_data=json.dumps({}))
def test_missing_chain_config(  mock_open, mock_isfile, fx_logger_error, fx_load_config,):

    main()
    
    # assert that an error was logged indicating the missing chain configuration
    fx_logger_error.assert_called_with("chain_config does not exist in config file. Aborting...")
    


@patch('builtins.print')
@patch('os.path.isfile', return_value=True)
@patch('builtins.open', new_callable=mock.mock_open, read_data=json.dumps({}))
@patch.dict('os.environ', {"CONFIG_VAR_NAME": "path_to_config"})
@patch('prototype.evaluation.test.generate_chain')
@patch('prototype.evaluation.test.Citation.extract_citations')
def test_simple_test_execution(mock_extract_citations,  mock_generate_chain, mock_open, mock_isfile, mock_print, fx_load_config, fx_config_simple_test):
    
    # set mocks for the needed objects/chains for 'simple test '
    fx_load_config.return_value = fx_config_simple_test
    mock_solution = MagicMock()
    mock_result = MagicMock()
    
    # mock response
    mock_result.response = "There are 7 volumes in the cbb rulebook."
    mock_solution.invoke.return_value = mock_result
    mock_generate_chain.return_value = mock_solution
    
    # mock citation to test that when simple test is executed the citations are printed
    mock_extract_citations.return_value =  [
        MagicMock(page_content="Page content example 1", metadata="Source example 1"),
    ]

    # main function call
    main()

    #assert that the mocked solution was called
    mock_solution.invoke.assert_called_once_with("how many volumes are there in the cbb rulebook?")
    
    #test citations were printed
    mock_print.assert_any_call("There are 7 volumes in the cbb rulebook.")
    mock_print.assert_any_call("Page Content: Page content example 1")
    mock_print.assert_any_call("Source:", "Source example 1")



# test case for executing an 'automated test'
@pytest.mark.logger_path_error("evaluators")
@patch('os.path.isfile', return_value=True)
@patch('builtins.open', new_callable=mock.mock_open, read_data=json.dumps({}))
@patch('os.environ', {"CONFIG_VAR_NAME": "path_to_config"})
@patch('prototype.evaluation.test.generate_chain')
@patch('prototype.evaluation.test.run_test')
def test_automated_test_execution( mock_run_test, mock_generate_chain, mock_open, mock_env, fx_logger_error,fx_config_automated_test, fx_load_config):
    
    # mock configurations return value chain config return value
    fx_load_config.return_value = fx_config_automated_test
    mock_generate_chain.return_value = MagicMock()

    main()

    # assertions that the test was called with the expected configs and the test was mocked correctly with no errors
    mock_generate_chain.assert_called_with("some_chain_config")
    mock_run_test.assert_called_with(solution=mock_generate_chain.return_value, automated_test_config=fx_config_automated_test['automated_test_config'])
    fx_logger_error.assert_not_called()


# test for Abstract Solution Methods : invoke
@patch("prototype.common.chain_generator.AbstractSolution")   
@patch("prototype.common.chain_generator.generate_chain")   
def test_invoke_method(mock_generate_chain, fx_solution_invoke, fx_config_bedrock):
    mock_generate_chain = MagicMock(fx_config_bedrock)
    solution = mock_generate_chain.return_value
    prompt = "input prompt"
    result = solution.invoke(prompt)
    assert result.response
    assert result.context

# test for Abstract Solution Methods : test
@patch("prototype.common.chain_generator.AbstractSolution")   
@patch("prototype.common.chain_generator.generate_chain")   
def test_test_method(mock_generate_chain, fx_solution, fx_config_bedrock):
    mock_generate_chain = MagicMock(fx_config_bedrock)
    solution = mock_generate_chain.return_value
    prompt = {"question" : "example question "}
    result = solution.test(prompt)
    assert result.response
    assert result.context

