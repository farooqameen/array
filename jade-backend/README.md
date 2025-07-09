# Hierarchical Retrieval-Augmented Generation System

## Hierarchical Retrieval-Augmented Generation with FastAPI, LlamaIndex, and AWS Bedrock

This project implements a robust Retrieval-Augmented Generation (RAG) system designed for various document types. It leverages FastAPI for a high-performance API, LlamaIndex for advanced hierarchical indexing and retrieval, and **AWS Bedrock Claude 3.5 Sonnet** as the underlying Large Language Model (LLM).

## Features

  * **FastAPI Backend**: Provides a scalable and asynchronous API for document processing and querying.
  * **Hierarchical Indexing**: Utilizes LlamaIndex's hierarchical node parser for intelligent document segmentation, enabling precise retrieval.
  * **Metadata Extraction**: Extracts and enhances document metadata for improved retrieval accuracy.
  * **AWS Bedrock Integration**: Leverages AWS Bedrock for both language model (LLM) processing and embeddings, ensuring powerful text understanding and generation capabilities.
  * **Lifespan Event Handling**: Properly initializes the LLM, loads/builds the knowledge index on application startup, and handles graceful shutdown.
  * **Structured Logging**: Comprehensive logging to console and a rotating file for better monitoring and debugging.

## Project Structure

```
app/
├── main.py                           # FastAPI application entry point, defines lifespan events and includes API routes.
├── startup.py                        # Contains application initialization logic (LLM setup, index build/load).
├── config/
│   ├── cors.py                       # CORS middleware configuration.
│   └── settings.py                   # Centralized configuration for environment-dependent settings and file paths.
├── controllers/
│   ├── chat_controller.py            # Handles the core business logic for document upload and query processing.
│   └── search_controller.py          # Handles search-related API logic.
├── logger.py                         # Configures and sets up the application-wide logging system.
├── models/
│   └── api_models.py                 # Defines Pydantic models for API request and response validation.
├── routes/
│   ├── chat_routes.py                # Defines API endpoints (e.g., /upload, /query) and routes requests to controllers.
│   └── search_routes.py              # Search-related API routes.
├── services/
│   ├── index_service.py              # Manages the creation, persistence, and loading of the hierarchical LlamaIndex.
│   ├── llm_service.py                # Handles the initialization of AWS Bedrock LLM and embedding models.
│   ├── metadata_extractor.py         # Implements logic for extracting and enriching metadata from document text.
│   ├── bot/
│   │   ├── index_service.py          # Bot-related indexing services.
│   │   ├── llm_service.py            # Bot-related LLM services.
│   │   └── metadata_extractor.py     # Bot-related metadata extraction.
│   └── search/
│       ├── opensearch.py             # OpenSearch integration.
│       └── pdf_parser.py             # PDF parsing logic.
├── utils/
│   └── file_utils.py                 # Provides utility functions, primarily for secure file handling.
├── data/                             #  Place your PDF documents here for indexing.
├── documents/                        # Temporary storage for uploaded PDF documents via API.
├── logs/
│   └── app.log                       # Application log file with rotation.
└── storage/
└── hrag_index/                       # Persistent storage for the LlamaIndex (e.g., vector stores, docstore, graph).

```

## 🛠️ Setup & Running

### Prerequisites

  * Python 3.13 (see `.python-version` for the recommended version)
  * [`uv`](https://github.com/astral-sh/uv) (fast Python package manager; replaces `pip install`)
  * An AWS account with access to Bedrock and the required models (Claude 3.5 Sonnet, Amazon Titan Embeddings)

### 1. Prepare Environment Variables

Run the following comands in your bash terminal to set the AWS environment variables:

```bash
$Env:AWS_ACCESS_KEY_ID="YOUR AWS ACCESS KEY ID"
$Env:AWS_SECRET_ACCESS_KEY= "YOUR AWS SECRET ACCESS KEY"
$Env:AWS_SESSION_TOKEN= "YOUR AWS SESSION TOKEN"
```


Replace the values with your actual AWS credentials.  
Ensure your AWS user/role has permissions for Bedrock and the models you intend to use.

### 2. Install Dependencies

Navigate to the project root and install the required Python packages using [`uv`](https://github.com/astral-sh/uv):

```bash
uv sync
```

> **Note:**  
> This project uses `uv` for dependency management, with a `pyproject.toml` and `uv.lock` file for reproducible installs.  
> Make sure you have `uv` installed (`pip install uv` or see [uv GitHub](https://github.com/astral-sh/uv#installation)).

### 3. Add Documents for Indexing


Use the `POST /chat/upload/` endpoint to upload a PDF for indexing.  
You must specify the `rag_type` as either `HRAG` or `TradRAG`.

- Endpoint: `POST /chat/upload/`
- Form fields:
  - `file`: The PDF file to upload.
  - `rag_type`: `HRAG` or `TradRAG`

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/chat/upload/" \
  -F "file=@your_document.pdf" \
  -F "rag_type=HRAG"
```


### 4. Run the Application

From the `app/` directory, start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
* `main:app`: Runs the `app` object from `main.py`.
* `--host 127.0.0.1`: Binds to localhost.
* `--port 8000`: Sets the server port.
* `--reload`: Enables auto-reloading on code changes (development only).

or simply run the main file:

```bash
python .\main.py
```

Access the application at `http://127.0.0.1:8000`.

### 5. API Endpoints

* **`POST /upload/`**

  * Upload a single PDF document to the `documents/` directory.
  * `multipart/form-data` with a `file` field.

* **`POST /query`**


After uploading and indexing your PDF, use the query endpoints to interact with the indexed content.

- **Hierarchical RAG:**  
  Endpoint: `POST /queryHRAG`  
  Body:
  ```json
  {
    "query": "Summarize the main topics."
  }
  ```

- **Traditional RAG:**  
  Endpoint: `POST /queryRAG`  
  Body:
  ```json
  {
    "query": "Summarize the main topics."
  }
  ```

Both endpoints return generated LLM responses and relevant references.

---
