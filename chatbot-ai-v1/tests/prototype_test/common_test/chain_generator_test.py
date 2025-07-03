from langsmith import expect
import pytest, copy
from unittest.mock import patch

from prototype.common.chain_generator import (
    Citation,
    generate_chain,
)
from langchain_core.documents import Document

from tests.prototype_test.common_test.conftest import (
    fx_mock_boto3_session_good_response,
    fx_result_chunk_empty,
    fx_result_chunk_with_multiple_doc_in_context,
    fx_result_chunk_with_only_context,
    fx_result_chunk_with_only_response,
    fx_result_chunk_with_response_and_context,
    fx_result_chunk_with_no_doc_in_context,
    fx_sample_citation,
    fx_sample_citation_empty_metadata,
    fx_sample_citation_null_metadata,
)
from tests.prototype_test.conftest import MockSolution


class TestResultChunk:
    @pytest.mark.parametrize(
        "result_chunk_fixture, expected_response, expected_context, has_response, has_context",
        [
            (
                fx_result_chunk_with_response_and_context,
                {"key": "value"},
                [
                    Document(
                        page_content="sample content",
                        metadata={
                            "location": {
                                "s3Location": {"uri": '"s3://cbb-rulebook/sample-key"'}
                            }
                        },
                    )
                ],
                True,
                True,
            ),
            (fx_result_chunk_with_only_response, {"key": "value"}, None, True, False),
            (
                fx_result_chunk_with_only_context,
                None,
                [
                    Document(
                        page_content="sample content",
                        metadata={
                            "location": {"s3Location": {"uri": "s3://bucket/key"}}
                        },
                    )
                ],
                False,
                True,
            ),
            (fx_result_chunk_empty, None, None, False, False),
        ],
    )
    def test_result_chunk(
        self,
        result_chunk_fixture,
        expected_response,
        expected_context,
        has_response,
        has_context,
        request,
    ):
        result_chunk = request.getfixturevalue(result_chunk_fixture.__name__)

        assert result_chunk.response == expected_response
        assert result_chunk.context == expected_context
        assert result_chunk.has_response() == has_response
        assert result_chunk.has_context() == has_context


class TestCitation:

    @pytest.mark.parametrize(
        "citation_fixture",
        [
            fx_sample_citation,
            fx_sample_citation_empty_metadata,
            fx_sample_citation_null_metadata,
        ],
    )
    def test_fetch_s3_metadata_good_response(
        self,
        fx_mock_boto3_session_good_response,
        citation_fixture,
        request,
    ):
        sample_citation = request.getfixturevalue(citation_fixture.__name__)
        input_metadata = sample_citation.metadata
        lambda_has_uri = lambda metadata: metadata is not None and "location" in input_metadata and "s3Location" in input_metadata["location"]\
              and "uri" in input_metadata["location"]["s3Location"]
        
        # Get the S3 Session client
        mock_s3_client = fx_mock_boto3_session_good_response.return_value.client.return_value

        # Call the method fetch
        Citation._fetch_s3_metadata(input_metadata)

        expected_metadata = copy.deepcopy(input_metadata)
        if lambda_has_uri(input_metadata):
            # generate expected metadata
            expected_metadata["s3_uri"] = input_metadata["location"]["s3Location"]["uri"]
            del expected_metadata["location"]
            expected_metadata["attribute1"] = "value1"
            expected_metadata["attribute2"] = "value2"

            # Assert that the S3 client was called with the correct parameters only for non-empty metadata samples
            mock_s3_client.get_object.assert_called_once_with(
                Bucket="sample-bucket", Key="sample-key.metadata.json"
            )
        
        # Assert the metadata is updated correctly
        assert input_metadata == expected_metadata

    
    # def test_fetch_s3_metadata_bad_response(
    #     self,
    #     mock_error,
    #     fx_mock_boto3_session_bad_response,
    #     fx_sample_citation
    # ):
    #     input_metadata = fx_sample_citation.metadata
    #     expected_metadata = copy.deepcopy(input_metadata)
    #     # Get the S3 Session client
    #     mock_s3_client = fx_mock_boto3_session_bad_response.return_value.client.return_value

    #     # Call the method fetch
    #     Citation._fetch_s3_metadata(input_metadata)

    #     mock_error.assert_called_with(
    #         "Failed to fetch metadata from s3 bucket [s3://sample-bucket/sample-key], no changes made.. continuing.."
    #     )

    #     assert expected_metadata == input_metadata

    def test_citation_initialization(self):
        citation = Citation(
            page_content="sample content",
            metadata={"location": {"s3Location": {"uri": "s3://bucket/key"}}},
        )

        assert citation.page_content == "sample content"
        assert citation.metadata == {
            "location": {"s3Location": {"uri": "s3://bucket/key"}}
        }

    @pytest.mark.parametrize(
        "result_fixture, expected_result_length, expected_page_contents",
        [
            (
                fx_result_chunk_with_response_and_context,
                1,
                ["sample content"],
            ),
            (
                fx_result_chunk_with_multiple_doc_in_context,
                3,
                ["sample content", "sample content2", "sample content3"],
            ),
            (fx_result_chunk_with_no_doc_in_context, 0, []),
        ],
    )
    def test_citation_extract_citations(
        self,
        result_fixture,
        expected_result_length,
        expected_page_contents,
        request,
    ):
        result_chunk = request.getfixturevalue(result_fixture.__name__)
        citations = Citation.extract_citations(result_chunk, False)

        assert len(citations) == expected_result_length
        for i, page_content in enumerate(expected_page_contents):
            assert citations[i].page_content == page_content

    @pytest.mark.parametrize(
        "result_fixture, expected_result",
        [
            (fx_result_chunk_with_response_and_context, "sample content\n"),
            (
                fx_result_chunk_with_multiple_doc_in_context,
                "sample content\nsample content2\nsample content3\n",
            ),
            (fx_result_chunk_with_no_doc_in_context, ""),
        ],
    )
    def test_citation_context_to_one_string(
        self, result_fixture, expected_result, request
    ):
        result_chunk = request.getfixturevalue(result_fixture.__name__)
        context = {"context": result_chunk.context}
        result = Citation.context_to_one_string(context)
        assert result == expected_result

    @pytest.mark.parametrize(
        "result_fixture, expected_result",
        [
            (
                fx_result_chunk_with_response_and_context,
                ["sample content"],
            ),
            (
                fx_result_chunk_with_multiple_doc_in_context,
                ["sample content", "sample content2", "sample content3"],
            ),
            (fx_result_chunk_with_no_doc_in_context, []),
        ],
    )
    def test_citation_context_to_list_string(
        self, result_fixture, expected_result, request
    ):
        result_chunk = request.getfixturevalue(result_fixture.__name__)
        context = {"context": result_chunk.context}
        result = Citation.context_to_list_string(context)
        assert result == expected_result


class TestGenerateChain:

    def test_generate_chain_success(self):
        chain_config = {"solution_class": "MockSolution", "args": {"param1": "value1"}}

        solution = generate_chain(chain_config)

        assert isinstance(solution, MockSolution)
        assert solution.param1 == "value1"
        
    @pytest.mark.logger_path_error("chain_generator")
    def test_generate_chain_class_not_exist(self, fx_logger_error):
        chain_config = {
            "solution_class": "NonExistentSolution",
            "args": {"param1": "value1"},
        }

        solution = generate_chain(chain_config)

        assert solution is None
        fx_logger_error.assert_called_once_with(
            "NonExistentSolution is not implmeneted..."
        )
        
    @pytest.mark.logger_path_error("chain_generator")
    def test_generate_chain_missing_config(self, fx_logger_error):
        chain_config = {
            "args": {"param1": "value1"},
        }

        solution = generate_chain(chain_config)

        assert solution is None
        fx_logger_error.assert_called_once_with(
            "'solution_class' cannot be found in config file..."
        )

    
    @pytest.mark.logger_path_error("chain_generator")
    @patch(
        "tests.prototype_test.conftest.MockSolution.__init__",
        side_effect=TypeError("Invalid arguments"),
    )
    def test_generate_chain_exception(self, _init_ , fx_logger_error):
        chain_config = {"solution_class": "MockSolution", "args": {"param1": "value1"}}
        solution = generate_chain(chain_config)

        assert solution is None
        fx_logger_error.assert_any_call(
            "Failed to instantiate solution object MockSolution, likely due to invalid configs."
        )
