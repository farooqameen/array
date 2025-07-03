"""
Service module for managing index creation and query engine loading.

This module handles building a hierarchical index with rich metadata
from rulebook documents and provides access to a query engine based
on the persisted index.
"""

import os
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex,
)
from llama_index.core.node_parser import HierarchicalNodeParser

from config.settings import settings
from logger import logger
from .metadata_extractor import (
    RulebookMetadataExtractor,
    determine_hierarchy_level,
    generate_search_tags,
    calculate_importance_score,
    enhance_node_metadata,
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
        f"Starting hierarchical index build from '{data_dir}' to '{index_path}'"
    )
    extractor = RulebookMetadataExtractor()
    documents = []

    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(data_dir, fname)
            try:
                doc_objs = SimpleDirectoryReader(input_files=[path]).load_data()
                logger.debug(
                    f"Loaded {len(doc_objs)} document objects from file: {fname}"
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
                logger.error(f"Error processing document {fname}: {e}", exc_info=True)
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
    logger.info(f"Generated {len(nodes)} hierarchical nodes from documents.")

    # Enhance metadata for each node
    for node in nodes:
        enhance_node_metadata(node, extractor)
    logger.info("Enhanced metadata for all nodes.")

    # Build and persist the index
    try:
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(index_path)
        logger.info(f"Successfully built hierarchical index with {len(nodes)} nodes")
        logger.info(f"Index saved to: {index_path}")
    except Exception as e:
        logger.error(f"Failed to persist index to {index_path}: {e}", exc_info=True)
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
    logger.info(f"Building traditional RAG index from '{data_dir}' to '{index_path}'")
    documents = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(data_dir, fname)
            try:
                doc_objs = SimpleDirectoryReader(input_files=[path]).load_data()
                documents.extend(doc_objs)
            except Exception as e:
                logger.error(f"Error processing document {fname}: {e}", exc_info=True)
                continue

    if not documents:
        logger.warning("No valid documents found. Index will not be built.")
        return

    # Flat chunking (no hierarchy)
    nodes = [doc for doc in documents]
    try:
        index = VectorStoreIndex(nodes)
        index.storage_context.persist(index_path)
        logger.info(f"Traditional RAG index built and saved to: {index_path}")
    except Exception as e:
        logger.error(f"Failed to persist traditional index: {e}", exc_info=True)
        raise


def get_hrag_query_engine(index_path: str):
    """
    Load a query engine from the persisted index storage.

    This function restores the hierarchical index from disk and
    returns a query engine instance capable of answering natural language
    questions over the indexed documents.

    Args:
        index_path (str): Directory path where the index is stored.

    Returns:
        query_engine: A query engine instance built from the loaded index.

    Raises:
        RuntimeError: If the index cannot be loaded successfully.
    """
    logger.info(f"Attempting to load query engine from storage: {index_path}")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        logger.info("Query engine loaded successfully.")
        return query_engine
    except Exception as e:
        logger.error(
            f"Failed to load index from storage at {index_path}: {e}", exc_info=True
        )
        raise RuntimeError(f"Failed to load query engine: {e}. Ensure index is built.")


def get_traditional_query_engine(index_path: str):
    """
    Load a traditional RAG query engine from the persisted index storage.

    This function restores the traditional index from disk and
    returns a query engine instance capable of answering natural language
    questions over the indexed documents.

    Args:
        index_path (str): Directory path where the index is stored.

    Returns:
        query_engine: A query engine instance built from the loaded index.

    Raises:
        RuntimeError: If the index cannot be loaded successfully.
    """
    logger.info(f"Loading traditional RAG query engine from: {index_path}")
    try:
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        logger.info("Traditional RAG query engine loaded successfully.")
        return query_engine
    except Exception as e:
        logger.error(
            f"Failed to load traditional RAG index from {index_path}: {e}", exc_info=True
        )
        raise RuntimeError(f"Failed to load traditional query engine: {e}")
