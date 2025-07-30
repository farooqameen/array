"""
Service module for managing index creation and query engine loading.

This module handles building a hierarchical index with rich metadata
from rulebook documents and provides access to a query engine based
on the persisted index.
"""

import os

from config.settings import settings
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
    load_index_from_storage,
)
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.query_engine import RetrieverQueryEngine
from logger import logger

from .metadata_extractor import (
    RulebookMetadataExtractor,
    calculate_importance_score,
    determine_hierarchy_level,
    enhance_node_metadata,
    generate_search_tags,
)


def build_hierarchical_index(data_dir: str, index_path: str) -> None:
    """
    Build a hierarchical RAG index from rulebook documents and persist it to disk.

    This function loads PDF files from the specified directory, extracts
    structured metadata, splits the documents into hierarchical nodes,
    enriches the nodes with domain-specific tags and importance scores,
    and then stores the index in the specified location.

    Args:
        data_dir (str): Path to the directory containing input PDF documents.
        index_path (str): Path where the index will be saved.

    Raises:
        Exception: If index persistence fails.
    """
    logger.info(
        "Starting hierarchical index build from '%s' to '%s'", data_dir, index_path
    )
    extractor = RulebookMetadataExtractor()
    documents = []

    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".pdf") and "rulebook" in fname.lower():
            path = os.path.join(data_dir, fname)
            try:
                doc_objs = SimpleDirectoryReader(input_files=[path]).load_data()
                logger.debug(
                    "Loaded %d document objects from file: %s", len(doc_objs), fname
                )

                for doc in doc_objs:
                    doc.metadata = doc.metadata or {}
                    doc.metadata["filename"] = fname
                    text = doc.text

                    # Extract structured metadata
                    doc.metadata.update(extractor.extract_volume_info(text))
                    doc.metadata.update(extractor.extract_module_info(text))
                    doc.metadata.update(extractor.extract_chapter_info(text))
                    doc.metadata.update(extractor.extract_section_info(text))
                    doc.metadata.update(extractor.extract_date_info(text))
                    doc.metadata.update(extractor.extract_regulatory_context(text))

                    # Determine content type
                    doc.metadata["content_type"] = extractor.determine_content_type(
                        text
                    )

                    # Determine hierarchy level
                    doc.metadata["hierarchy_level"] = determine_hierarchy_level(
                        doc.metadata
                    )

                    # Add search tags
                    skip_tags = ["Unknown", "Other"]
                    if (
                        doc.metadata.get("content_type") not in skip_tags
                        and doc.metadata.get("volume_type") not in skip_tags
                        and doc.metadata.get("module_category") not in skip_tags
                    ):
                        doc.metadata["search_tags"] = generate_search_tags(
                            doc.metadata, text
                        )

                    # Assign importance score
                    doc.metadata["regulatory_importance"] = calculate_importance_score(
                        doc.metadata, text
                    )

                documents.extend(doc_objs)
            except Exception as e:
                logger.error(
                    "Error processing document %s: %s", fname, e, exc_info=True
                )
                continue
        elif fname.lower().endswith(".pdf"):
            # For non-rulebook PDFs, just load them without metadata extraction
            path = os.path.join(data_dir, fname)
            try:
                doc_objs = SimpleDirectoryReader(input_files=[path]).load_data()
                for doc in doc_objs:
                    doc.metadata = doc.metadata or {}
                    doc.metadata = {"filename": fname}
                documents.extend(doc_objs)
            except Exception as e:
                logger.error(
                    "Error processing document %s: %s", fname, e, exc_info=True
                )
                continue

    if not documents:
        logger.warning("No valid documents found. Index will not be built.")
        return

    # Hierarchical chunking configuration
    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=settings.CHUNK_SIZES,
        chunk_overlap=settings.CHUNK_OVERLAP,
        include_metadata=True,
        include_prev_next_rel=True,
    )

    # Convert to hierarchical nodes
    nodes = parser.get_nodes_from_documents(documents)
    logger.info("Generated %d hierarchical nodes from documents.", len(nodes))

    # Enhance metadata for each node
    for node in nodes:
        enhance_node_metadata(node, extractor)
    logger.info("Enhanced metadata for all nodes.")

    # Build and persist the index
    try:
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(index_path)
        logger.info("Successfully built hierarchical index with %d nodes", len(nodes))
        logger.info("Index saved to: %s", index_path)
    except Exception as e:
        logger.error("Failed to persist index to %s: %s", index_path, e, exc_info=True)
        raise


def build_traditional_index(data_dir: str, index_path: str) -> None:
    """
    Build a traditional (flat) RAG index from documents and persist it to disk.

    This function loads PDF files from the specified directory and
    creates a flat index without any hierarchical structure. The index
    is then persisted to the specified location.

    Args:
        data_dir (str): Path to the directory containing input PDF documents.
        index_path (str): Path where the index will be saved.

    Raises:
        Exception: If index persistence fails.
    """
    logger.info(
        "Building traditional RAG index from '%s' to '%s'", data_dir, index_path
    )
    documents = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(data_dir, fname)
            try:
                doc_objs = SimpleDirectoryReader(input_files=[path]).load_data()
                documents.extend(doc_objs)
            except Exception as e:
                logger.error(
                    "Error processing document %s: %s", fname, e, exc_info=True
                )
                continue

    if not documents:
        logger.warning("No valid documents found. Index will not be built.")
        return

    # Flat chunking (no hierarchy)
    nodes = [doc for doc in documents]
    try:
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(index_path)
        logger.info("Traditional RAG index built and saved to: %s", index_path)
    except Exception as e:
        logger.error("Failed to persist traditional index: %s", e, exc_info=True)
        raise


# class LoggingRetriever:
#     def __init__(self, retriever):
#         self.retriever = retriever

#     def retrieve(self, query, *args, **kwargs):
#         results = self.retriever.retrieve(query, *args, **kwargs)
#         # Log the retrieved context (nodes/chunks)
#         print(f"Retrieved {len(results)} chunks for query: '{query}'")
#         logger.info(f"Retrieved context for query '{query}':")
#         for i, node in enumerate(results):
#             logger.info(f"Chunk {i+1}: {getattr(node, 'text', str(node))[:10000]}")  # Log first 500 chars
#         return results

#     def __getattr__(self, name):
#         # Delegate attribute access to the underlying retriever
#         return getattr(self.retriever, name)


class FilteringRetriever:
    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, query, *args, filters=None, **kwargs):
        results = self.retriever.retrieve(query, *args, **kwargs)
        if filters:
            filtered = []
            for node in results:
                meta = getattr(node, "metadata", {})
                keep = False
                for key, allowed in filters.items():
                    if str(meta.get(key)) in allowed:
                        keep = True
                        break
                if keep:
                    filtered.append(node)
            return filtered
        return results

    def __getattr__(self, name):
        return getattr(self.retriever, name)


def get_hrag_query_engine(index_path: str, top_k: int = 20):
    """
    Load a query engine from the persisted index storage with auto-merging retrieval.

    This function restores the hierarchical index from disk and
    returns a query engine instance capable of answering natural language
    questions over the indexed documents, using auto-merging retrieval
    to provide richer context.

    Args:
        index_path (str): Directory path where the index is stored.

    Returns:
        query_engine: A query engine instance built from the loaded index.

    Raises:
        RuntimeError: If the index cannot be loaded successfully.
    """

    logger.info("Attempting to load query engine from storage: %s", index_path)
    try:
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        retriever = index.as_retriever(similarity_top_k=top_k)
        filtering_retriever = FilteringRetriever(retriever)
        response_synthesizer = get_response_synthesizer()
        query_engine = RetrieverQueryEngine(
            retriever=filtering_retriever,
            response_synthesizer=response_synthesizer,
        )
        logger.info("HRAG query engine with auto-merging loaded successfully.")
        return query_engine
    except Exception as e:
        logger.error(
            "Failed to load index from storage at %s: %s", index_path, e, exc_info=True
        )
        raise RuntimeError(f"Failed to load query engine: {e}. Ensure index is built.")


def get_traditional_query_engine(index_path: str, top_k: int = 20):
    logger.info("Loading traditional RAG query engine from: %s", index_path)
    try:
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        retriever = index.as_retriever(similarity_top_k=top_k)
        query_engine = RetrieverQueryEngine.from_args(retriever=retriever)
        logger.info(
            "Traditional RAG query engine loaded successfully with top_k=%d.", top_k
        )
        return query_engine
    except Exception as e:
        logger.error(
            "Failed to load traditional RAG index from %s: %s",
            index_path,
            e,
            exc_info=True,
        )
        raise RuntimeError(f"Failed to load traditional query engine: {e}")
