# services/search/opensearch.py
from opensearchpy import NotFoundError, OpenSearch

from app.config.settings import opensearch_config
from app.logger import logger


class OpenSearchStore:
    def __init__(self):
        self.client: OpenSearch = opensearch_config.get_client()

    def create_index(self, index_name: str) -> None:
        """
        Create an index with the required mapping if it does not exist.
        Logs the result or any errors encountered.
        """
        try:
            if not self.client.indices.exists(index=index_name):
                logger.info("Attempting to create index: %s", index_name)
                mapping = {
                    "properties": {
                        "batch_number": {"type": "integer"},
                        "page_number": {"type": "integer"},
                        "word_count": {"type": "integer"},
                        "timestamp": {"type": "date"},
                    }
                }
                self.client.indices.create(index=index_name, body={"mappings": mapping})
                logger.info("Index '%s' created successfully with mapping.", index_name)
            else:
                logger.info("Index '%s' already exists. Skipping creation.", index_name)
        except Exception as e:
            logger.error("Error creating index '%s': %s", index_name, e, exc_info=True)
            raise

    def get_next_batch_number(self, index_name: str) -> int:
        """
        Get the next batch number for the given index.
        Returns 1 if the index or batch number does not exist.
        """
        logger.info("Querying for max batch number in index '%s'.", index_name)
        try:
            if not self.client.indices.exists(index=index_name):
                logger.info(
                    "Index '%s' does not exist. Starting with batch number 1.",
                    index_name,
                )
                return 1
            query = {
                "size": 0,
                "aggs": {"max_batch": {"max": {"field": "batch_number"}}},
            }
            response = self.client.search(index=index_name, body=query)
            max_batch = response["aggregations"]["max_batch"]["value"]
            if max_batch is None:
                logger.info(
                    "No existing 'batch_number' found in '%s'. Starting with 1.",
                    index_name,
                )
                return 1
            else:
                next_batch = int(max_batch) + 1
                logger.info(
                    "Max batch number found is %d. Next batch will be %d.",
                    int(max_batch),
                    next_batch,
                )
                return next_batch
        except NotFoundError:
            logger.warning(
                "Index '%s' not found while getting batch number. Returning 1.",
                index_name,
            )
            return 1
        except Exception as e:
            logger.error(
                "Error getting next batch number from '%s': %s",
                index_name,
                e,
                exc_info=True,
            )
            return 1

    def index_chunks(self, index_name: str, chunks: list[dict]) -> None:
        """
        Index a list of chunk documents into the specified index.
        Logs the number of successfully indexed chunks.
        """
        if not chunks:
            logger.warning("No chunks provided for indexing in '%s'.", index_name)
            return
        indexed_count = 0
        for chunk in chunks:
            try:
                self.client.index(
                    index=index_name, body=chunk, id=chunk.get("chunk_id")
                )
                indexed_count += 1
            except Exception as e:
                logger.error(
                    "Failed to index chunk %s into '%s': %s",
                    chunk.get("chunk_id", "N/A"),
                    index_name,
                    e,
                )
        logger.info(
            "Successfully indexed %d out of %d chunks into '%s'.",
            indexed_count,
            len(chunks),
            index_name,
        )

    def search_chunks(self, index_name: str, query: str, size: int = 10) -> list[dict]:
        """
        Executes a match query against the 'text' field and returns the entire
        _source document for each hit, providing the frontend with all necessary data.
        """
        if not query:
            logger.warning("Search query is empty. Returning no results.")
            return []

        try:
            logger.info(
                "Searching index '%s' for query: '%s' with size: %d",
                index_name,
                query,
                size,
            )
            search_body = {
                "query": {
                    "match": {"contents.md": {"query": query, "fuzziness": "AUTO"}}
                },
                "size": size,
            }

            response = self.client.search(index=index_name, body=search_body)

            hits = response.get("hits", {}).get("hits", [])
            logger.info(
                "Found %d hits for query '%s' in index '%s'.",
                len(hits),
                query,
                index_name,
            )

            # Map each hit to the SearchResultItem schema
            mapped_results = []
            for hit in hits:
                src = hit.get("_source", {})
                mapped_results.append(
                    {
                        "chunk_id": src.get("id") or src.get("chunk_id"),
                        "score": hit.get("_score", 0.0),
                        "text": (
                            (src.get("contents", {}) or {}).get("md")
                            if src.get("contents")
                            else src.get("text", "")
                        ),
                        "page_number": src.get("rule_page")
                        or src.get("page_number")
                        or 0,
                    }
                )
            return mapped_results

        except NotFoundError:
            logger.warning(
                "Index '%s' not found during search. No results returned.", index_name
            )
            return []
        except Exception as e:
            logger.error(
                "An error occurred during search in '%s' for query '%s': %s",
                index_name,
                query,
                e,
                exc_info=True,
            )
            return []
