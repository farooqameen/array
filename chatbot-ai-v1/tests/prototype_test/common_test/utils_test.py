import json
import os
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch, call
import dotenv
import pytest

from prototype.common.constants import CONFIG_VAR_NAME
from prototype.common.utils import (
    Credential,
    load_config,
    validate_credential,
    store_env_var,
)
from tests.prototype_test.evaluation_test.conftest import fx_config_automated_test, fx_config_gptpinecone

# Test Cases for Decorator function (Validate Credential)

@patch("dotenv.find_dotenv", return_value=".env")  # mock for finding the .env file
@patch("dotenv.load_dotenv")  # mock for loading the dotenv
@patch("dotenv.set_key")  # mock for setting key values for env values
def test_validate_credential_all_present(
    mock_set_key, mock_load_dotenv, mock_find_dotenv, monkeypatch
):
    # Set environment variables using monkeypatch (scope = test case)
    monkeypatch.setenv("OPENAI_API_KEY", "openai_key")
    monkeypatch.setenv("AWS_PROFILE", "aws_profile")
    monkeypatch.setenv("AWS_REGION", "aws_region")

    # Decorated function to test
    @validate_credential([Credential.OPENAI, Credential.AWS])
    def test_function():
        return "Function executed"

    # Assert that function acessed and executed correctly (passing the credential validation)
    assert test_function() == "Function executed"

    # Assert that no keys have been set using the mock during the validation process
    mock_set_key.assert_not_called()


# @patch("dotenv.find_dotenv", return_value=".env")
# @patch("dotenv.load_dotenv")
# @patch("dotenv.set_key")
# @patch(  # mock to respond to input prompts with listed values (side effect) in order
#     "builtins.input",
#     side_effect=["new_openai_key", "new_aws_profile", "new_aws_region"],
# )
# def test_validate_credential_missing_credentials(
#     mock_inputs, mock_set_key, mock_load_dotenv, mock_find_dotenv, monkeypatch
# ):
#     # ensure missing env variables (otherwise will fail if user already has credentials in .env)
#     monkeypatch.delenv("OPENAI_API_KEY", raising=False)
#     # monkeypatch.delenv("AWS_PROFILE", raising=False)
#     # monkeypatch.delenv("AWS_REGION", raising=False)

#     # Decorated function to test
#     @validate_credential([Credential.OPENAI, Credential.AWS])
#     def test_function():
#         return "Function executed"

#     assert test_function() == "Function executed"

    # Assert that the mock object used to set the values in the .env file at the following order and values
    # mock_set_key.assert_has_calls(
    #     [
    #         call(".env", "OPENAI_API_KEY", "new_openai_key"),
    #         call(".env", "AWS_PROFILE", "new_aws_profile"),
    #         call(".env", "AWS_REGION", "new_aws_region"),
    #     ]
    # )
    
    # Cleanup any dummy values stored globally during the process
    #os.environ.pop("OPENAI_API_KEY", None)
    # os.environ.pop("AWS_PROFILE", None)
    # os.environ.pop("AWS_REGION", None)


# @patch("dotenv.find_dotenv", return_value=".env")
# @patch("dotenv.load_dotenv")
# @patch("dotenv.set_key")
# @patch("builtins.input", side_effect=["new_aws_profile", "new_aws_region"])
# def test_validate_credential_partial_missing_credentials(
#     mock_inputs, mock_set_key, mock_load_dotenv, mock_find_dotenv, monkeypatch
# ):

#     # ensure missing env variables (otherwise will fail if user already has credentials in .env)
#     monkeypatch.delenv("AWS_PROFILE", raising=False)
#     monkeypatch.delenv("AWS_REGION", raising=False)
#     monkeypatch.setenv("OPENAI_API_KEY", "openai_key")

#     # Decorated function to test
#     @validate_credential([Credential.OPENAI, Credential.AWS])
#     def test_function():
#         return "Function executed"

#     assert test_function() == "Function executed"

#     mock_set_key.assert_has_calls(
#         [
#             call(".env", "AWS_PROFILE", "new_aws_profile"),
#             call(".env", "AWS_REGION", "new_aws_region"),
#         ]
#     )
    
#     # Cleanup any dummy values stored globally during the process
#     os.environ.pop("AWS_PROFILE", None)
#     os.environ.pop("AWS_REGION", None)


@patch("dotenv.find_dotenv", return_value=".env")
@patch("dotenv.load_dotenv")
@patch("dotenv.set_key")
def test_store_env_var(mock_set_key, mock_load_dotenv, mock_find_dotenv):
    store_env_var("TEST_VAR", "test_value")

    mock_set_key.assert_called_once_with(".env", "TEST_VAR", "test_value")
    assert os.environ.get("TEST_VAR") == "test_value"

    
@patch('dotenv.load_dotenv')
@patch('prototype.common.utils.logger.error')
def test_load_config_invalid(mock_error_logger, mock_load_dotenv, monkeypatch):
    
    # Remove the environment variable for the config path
    monkeypatch.delenv(CONFIG_VAR_NAME, None)
    
    # assert that load_config returns 'None' and that an error is logged
    assert load_config() is None
    mock_error_logger.assert_called_once_with("config file path is not found in environment variables...")


@patch('os.path.isfile', return_value=False)
@patch.dict(os.environ, {CONFIG_VAR_NAME: 'no_path'}, clear=True)
@patch('dotenv.load_dotenv', return_value=True)
@patch('prototype.common.utils.logger.error')
def test_load_config_missing(mock_error_logger, mock_load_dotenv, mock_isfile):
    
    # assert that load_config returns 'None' and that an error is logged
    assert load_config() is None    
    mock_error_logger.assert_called_once_with("config file does not exist...")

@patch.dict(os.environ, {CONFIG_VAR_NAME: 'config/test_config.json'})
@patch('os.path.isfile', return_value=True)
@patch('builtins.open', new_callable=mock.mock_open)
@patch('prototype.common.utils.logger.error')
def test_load_config_success(mock_error_logger,  mock_open, mock_isfile, fx_config_gptpinecone):
    # using one of the mocked configurations that has no missing values
    mock_open.return_value.read.return_value = json.dumps(fx_config_gptpinecone)
    assert load_config() is not None
    
    # assert that the returned dictionary matches the expected content and no errors are logged
    assert "automated_test_config" in load_config()
    assert  "chain_config" in load_config()
    assert mock_error_logger.call_count == 0