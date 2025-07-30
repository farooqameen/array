# pylint: disable=line-too-long
"""
Service functions for CSV chat and analysis.

Includes DataFrame chunking, index building, query engine setup,
summarization, column type detection, and AI-powered chart suggestion logic.
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableLambda

from app.config.settings import settings
from app.logger import logger
from app.services.csv.constants import csv_constants
from app.services.csv.utils import (
    _extract_response_content,
    detect_column_types,
    extract_eda_stats,
    get_dataframe,
)

# Initialize LLM and embedding models
llm = ChatBedrock(
    model=settings.LLM_MODEL,
    region=settings.AWS_REGION,
    streaming=True,
)
embed_model = BedrockEmbeddings(
    model_id=settings.LANGCHAIN_EMBEDDING_MODEL, region_name=settings.AWS_REGION
)


def _estimate_token_count(text: str) -> int:
    """
    Estimate token count using character-to-token ratio approximation.

    Args:
        text (str): Input text to estimate tokens for.

    Returns:
        int: Estimated token count.
    """
    return len(text) // csv_constants.TOKEN_ESTIMATION_RATIO


def chunk_csv_table(
    df: pd.DataFrame,
    max_tokens: int = csv_constants.DEFAULT_CHUNK_SIZE,
    min_rows_per_chunk: int = csv_constants.DEFAULT_MIN_ROWS,
    overlap_rows: int = csv_constants.DEFAULT_OVERLAP_ROWS,
) -> List[Document]:
    """
    Chunk a DataFrame into markdown table documents for embedding.

    Args:
        df (pd.DataFrame): The DataFrame to chunk.
        max_tokens (int): Maximum tokens per chunk.
        min_rows_per_chunk (int): Minimum rows per chunk.
        overlap_rows (int): Number of overlapping rows between chunks.

    Returns:
        List[Document]: List of chunked table documents.
    """
    if df.empty:
        return []

    docs = []
    header = "| " + " | ".join(map(str, df.columns)) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    base_lines = [header, separator]

    chunk_lines = list(base_lines)
    current_token_count = _estimate_token_count("\n".join(base_lines))
    row_buffer = []

    for _, row in df.iterrows():
        # Clean cell values to prevent formatting issues
        cleaned_cells = [str(cell).strip().replace("|", "\\|") for cell in row.values]
        row_line = "| " + " | ".join(cleaned_cells) + " |"
        row_token_count = _estimate_token_count(row_line)

        # Check if we need to create a new chunk
        if (
            current_token_count + row_token_count > max_tokens
            and len(row_buffer) >= min_rows_per_chunk
        ):
            docs.append(Document(page_content="\n".join(chunk_lines)))

            # Prepare next chunk with overlap
            overlap = row_buffer[-overlap_rows:] if overlap_rows > 0 else []
            chunk_lines = list(base_lines) + overlap
            row_buffer = overlap.copy()
            current_token_count = _estimate_token_count("\n".join(chunk_lines))

        chunk_lines.append(row_line)
        row_buffer.append(row_line)
        current_token_count += row_token_count

    # Add final chunk if it has content beyond headers
    if len(chunk_lines) > len(base_lines):
        docs.append(Document(page_content="\n".join(chunk_lines)))

    return docs


def build_csv_index(df: pd.DataFrame, index_path: Path) -> None:
    """
    Build a FAISS vectorstore index from a DataFrame using optimized table chunking.
    Saves the index locally to the specified path.

    Args:
        df (pd.DataFrame): DataFrame to index.
        index_path (Path): Path to save the index.
    """
    docs = chunk_csv_table(df)
    vectorstore = FAISS.from_documents(docs, embedding=embed_model)
    vectorstore.save_local(str(index_path), index_name="index")


def load_csv_query_engine(index_path: Path) -> Runnable:
    """
    Load a query engine for the indexed CSV data with chat history and context retrieval.

    Args:
        index_path (Path): Path to the index directory containing FAISS index and original CSV.

    Returns:
        Runnable: Query engine with memory and retrieval capabilities.

    Raises:
        FileNotFoundError: If index files or original CSV are not found.
        ValueError: If CSV data is invalid or corrupted.
    """
    try:
        # Load vectorstore
        vectorstore = FAISS.load_local(
            str(index_path),
            embeddings=embed_model,
            index_name="index",
            allow_dangerous_deserialization=True,
        )
        retriever = vectorstore.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "lambda_mult": 0.5}
        )

        # Load and analyze original CSV
        original_csv_path = Path(index_path) / "original.csv"
        if not original_csv_path.exists():
            raise FileNotFoundError(f"Original CSV not found at {original_csv_path}")

        df = pd.read_csv(original_csv_path)
        df, types = detect_column_types(df)
        outlier_cols, high_card_cols, low_var_cols = extract_eda_stats(df, types)

        logger.info("outlier_cols: %s", outlier_cols)
        logger.info("high_card_cols: %s", high_card_cols)
        logger.info("low_var_cols: %s", low_var_cols)

        metadata = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "high_cardinality": high_card_cols,
            "low_variance": low_var_cols,
            "outliers": list(outlier_cols.keys()),
        }

        # Rewriter prompt
        question_rewriter_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant that reformulates follow-up questions into standalone questions based on prior chat history. Preserve the user’s intent clearly.",
                ),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_rewriter_chain = question_rewriter_prompt | llm | StrOutputParser()

        # QA prompt
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
You are a data analysis assistant. Answer user questions strictly based on the tabular CSV data provided in the context.

Dataset Metadata:
- Total rows: {metadata["row_count"]}
- Total columns: {metadata["column_count"]}
- Column names: {", ".join(metadata["columns"])}
- High-cardinality columns: {", ".join(metadata["high_cardinality"]) or "None"}
- Low-variance columns: {", ".join(metadata["low_variance"]) or "None"}
- Columns with outliers: {", ".join(metadata["outliers"]) or "None"}

Guidelines:
- Always consider all data rows before making conclusions.
- Do not prioritize recent or early rows unless explicitly asked.
- Do not invent or assume data that isn’t shown.
- Support claims with numerical references from the table when possible.
- Be concise and structured in your analysis.
- Avoid generic commentary unless explicitly asked.
""",
                ),
                MessagesPlaceholder("chat_history"),
                ("assistant", "{context}"),
                ("human", "{input}"),
            ]
        )
        qa_chain = qa_prompt | llm | StrOutputParser()

        async def engine_runner(inputs: dict):
            user_input = inputs["input"]
            chat_history = inputs["chat_history"]

            rewriter_history = chat_history[-4:]
            qa_history = chat_history[-10:]

            logger.info(
                "Processing query with %d rewriter turns, %d QA turns",
                len(rewriter_history),
                len(qa_history),
            )

            # First run the rewriter (not streamed)
            rewritten = await question_rewriter_chain.ainvoke(
                {
                    "input": user_input,
                    "chat_history": rewriter_history,
                }
            )

            # Run retrieval (also not streamed)
            context = retriever.invoke(rewritten)

            # Stream the QA chain
            async for chunk in qa_chain.astream(
                {
                    "input": user_input,
                    "context": context,
                    "chat_history": qa_history,
                }
            ):
                yield chunk

        return RunnableLambda(engine_runner)

    except Exception as e:
        logger.error("Failed to load CSV query engine: %s", e)
        raise


async def summarize_csv(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Summarize a CSV file with sample data, missing/duplicate values, metrics, and column descriptions.

    Args:
        file_path (Union[str, Path]): Path to the CSV file.

    Returns:
        Dict[str, Any]: Comprehensive summary dictionary containing:
            - initial_data_sample: First 10 rows of data
            - missing_values: Total count of missing values
            - duplicate_values: Count of duplicate rows
            - essential_metrics: Statistical summary
            - column_descriptions: AI-generated column descriptions

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        ValueError: If the CSV file is corrupted or empty.
    """
    try:
        df = get_dataframe(file_path)

        if df.empty:
            raise ValueError("CSV file is empty")

        # Basic statistics
        data_summary = {
            "initial_data_sample": df.head(10).to_dict(orient="records"),
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_values": int(df.duplicated().sum()),
            "essential_metrics": df.describe(include="all").to_dict(),
        }

        # Generate AI column descriptions
        try:
            markdown_sample = df.head(10).to_markdown(index=False)
            prompt = f"""
            Analyze this DataFrame sample and provide concise descriptions for each column:
            {markdown_sample}
            
            Return a JSON list of objects with keys: "Column Name" and "Description".
            Each description should be 1–2 sentences explaining what the column represents.
            Return only valid JSON — no markdown, no explanations, no extra text.
            """

            response = await llm.ainvoke(input=prompt)
            raw_content = _extract_response_content(response)

            cleaned = re.sub(r"```(?:json)?\n?|\n?```", "", raw_content).strip()

            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                parsed = ast.literal_eval(cleaned)

            if isinstance(parsed, list) and all(
                isinstance(item, dict) for item in parsed
            ):
                data_summary["column_descriptions"] = parsed
            else:
                raise ValueError("Parsed column_descriptions is not a list of dicts")

        except Exception as e:
            logger.warning("Failed to parse column descriptions: %s", e)
            data_summary["column_descriptions"] = []

        return data_summary

    except (FileNotFoundError, ValueError) as e:
        logger.error("Error summarizing CSV %s: %s", file_path, e)
        raise
