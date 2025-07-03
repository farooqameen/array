import json
import pytest
from datetime import datetime
from uuid import uuid4
from langsmith.schemas import Example, Run
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def fx_config_bedrock():
    return {
        "exe_simple_test": False,
        "exe_automated_test": True,
        "exe_streamlit_app": False,
        "chain_config": {
            "solution_class": "BedrockSolution",
            "args": {"knowledge_base_id": "---"},
        },
        "automated_test_config": {
            "evaluators": [
                "de_contextual_recall",
                "de_faithfulness",
                "de_noise_awarness",
                "de_correctness",
            ],
            "dataset_name": "test-dataset-3",
            "per_q_repeat": 1,
            "split_data": True,
            "splits": ["definitions"],
            "split_time_buff": 1,
            "evaluator_model": "gpt-4o",
            "experiment_name": "bedrock",
        },
    }


@pytest.fixture
def fx_config_gptpinecone():
    return {
    "exe_simple_test": True,
    "exe_automated_test": False,
    "exe_streamlit_app": False,
    "chain_config":{
        "solution_class":"GPTPineconeSolution",
        "args":{
            "pinecone_index_name":"rulebook-meta",
            "embed_model":"text-embedding-3-small",
            "gen_model":"gpt-4o",
            "pinecone_key":"30c350c6-d4fc-44bd-a6e9-d2e4b95aaef8"
        }
    },
    "automated_test_config":{
        "evaluators":["de_contextual_recall","de_faithfulness","de_noise_awarness","de_correctness"],
        "dataset_name":"cbb-test-dataset-v2",
        "per_q_repeat":1,
        "split_data":True,
        "splits": ["opinion"],
        "split_time_buff": 1,
        "evaluator_model":"gpt-4o",
        "experiment_name": "GPTPineconeSolution"
    }
}

@pytest.fixture
def fx_config_missing_configs():
    return {
        "exe_simple_test": False,
        "exe_automated_test": True,
        "exe_streamlit_app": False,
        "automated_test_config": {
            "evaluators": [
                "de_contextual_recall",
                "de_faithfulness",
                "de_noise_awarness",
                "de_correctness",
            ],
            "dataset_name": "test-dataset-3",
            "per_q_repeat": 1,
            "experiment_name": "bedrock",
        },
    }

@pytest.fixture
def fx_config_automated_test():
    return {
        "chain_config": "some_chain_config",
        "exe_simple_test": False,
        "exe_automated_test": True,
        "automated_test_config": {
            "evaluators":["de_contextual_recall","de_faithfulness","de_noise_awarness","de_correctness"],
            "dataset_name":"dummy dataset",
            "per_q_repeat":1,
            "split_data":True,
            "splits": ["opinion"],
            "evaluator_model":"gpt-4o",
            "experiment_name": "dummy experiment",
        },
    }


@pytest.fixture
def fx_config_simple_test():
    return {
        "chain_config": "some_chain_config",
        "exe_simple_test": True,
        "exe_automated_test": False
    }
    
@pytest.fixture
def fx_evaluate():
    with patch("prototype.evaluation.test.evaluate") as mock:
        yield mock

@pytest.fixture
def fx_client():
    with patch("prototype.evaluation.test.Client") as mock:
        yield mock
        
@pytest.fixture
def fx_load_config():
    with patch("prototype.evaluation.test.load_config") as mock:
        yield mock
        