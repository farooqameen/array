from config.settings import settings as Config
from config.settings import opensearch_config
from logger import logger
from opensearchpy import OpenSearch, NotFoundError

# Initialize the OpenSearch client using the configuration.
client: OpenSearch = opensearch_config.get_client()


def create_index(index_name: str) -> None:
    """
    Creates an OpenSearch index if it does not already exist.
    This ensures that the target index is ready for document storage.
    """
    try:
        if not client.indices.exists(index=index_name):
            logger.info(f"Attempting to create index: {index_name}")
            client.indices.create(index=index_name)
            logger.info(f"Index '{index_name}' created successfully.")
        else:
            logger.info(f"Index '{index_name}' already exists. Skipping creation.")
    except Exception as e:
        logger.error(f"Error creating index '{index_name}': {e}")


def index_chunks(index_name: str, chunks: list[dict]) -> None:
    """
    Indexes a list of document chunks into the specified OpenSearch index.
    Each chunk is treated as a separate document for searchability.
    """
    if not chunks:
        logger.warning(f"No chunks provided for indexing in '{index_name}'.")
        return

    indexed_count = 0
    for chunk in chunks:
        try:
            # OpenSearch automatically generates an _id if not provided,
            # but we use chunk_id for better traceability.
            client.index(index=index_name, body=chunk, id=chunk.get("chunk_id"))
            indexed_count += 1
        except Exception as e:
            logger.error(
                f"Failed to index chunk {chunk.get('chunk_id', 'N/A')} into '{index_name}': {e}"
            )
    logger.info(
        f"Successfully indexed {indexed_count} out of {len(chunks)} chunks into '{index_name}'."
    )


def search_chunks(index_name: str, query: str, size: int = 10) -> list[dict]:
    """
    Executes a match query against the 'text' field within an OpenSearch index.
    Retrieves relevant document chunks based on the provided search query.
    """
    if not query:
        logger.warning("Search query is empty. Returning no results.")
        return []

    try:
        logger.info(
            f"Searching index '{index_name}' for query: '{query}' with size: {size}"
        )
        response = client.search(
            index=index_name,
            body={
                "query": {
                    "match": {
                        "text": {
                            "query": query,
                            "fuzziness": "AUTO",  # Added for better search relevance
                        }
                    }
                }
            },
            size=size,
        )
        hits = response.get("hits", {}).get("hits", [])
        logger.info(
            f"Found {len(hits)} hits for query '{query}' in index '{index_name}'."
        )

        return [
            {
                "chunk_id": hit["_id"],
                "score": hit["_score"],
                "text": hit["_source"].get("text"),
                "page_number": hit["_source"].get("page_number"),
            }
            for hit in hits
        ]
    except NotFoundError:
        logger.warning(
            f"Index '{index_name}' not found during search. No results returned."
        )
        return []
    except Exception as e:
        logger.error(
            f"An error occurred during search in '{index_name}' for query '{query}': {e}"
        )
        return []
