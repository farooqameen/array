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

  * Python 3.9+
  * `pip` (Python package installer)
  * An AWS account with access to Bedrock and the required models (Claude 3.5 Sonnet, Amazon Titan Embeddings)

### 1. Prepare Environment Variables

Create a `.env` file in the `app/` directory and add your AWS Bedrock credentials:

```env
AWS_ACCESS_KEY_ID="your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_REGION="your_aws_region"  # e.g., us-east-1
# AWS_SESSION_TOKEN="your_aws_session_token"  # Only if using temporary credentials
```

Replace the values with your actual AWS credentials.  
Ensure your AWS user/role has permissions for Bedrock and the models you intend to use.

### 2. Install Dependencies

Navigate to the `app/` directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Add Documents for Indexing

Place your PDF files into the `data/` directory inside `app/`. These documents will be used to build the hierarchical index on application startup.

### 4. Run the Application

From the `app/` directory, start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

* `main:app`: Runs the `app` object from `main.py`.
* `--host 127.0.0.1`: Binds to localhost.
* `--port 8000`: Sets the server port.
* `--reload`: Enables auto-reloading on code changes (development only).

Access the application at `http://127.0.0.1:8000`.

### 5. API Endpoints

* **`POST /upload/`**

  * Upload a single PDF document to the `documents/` directory.
  * `multipart/form-data` with a `file` field.

* **`POST /query`**

  * Query the indexed documents using natural language.

  * JSON body example:

    ```json
    {
      "query": "Summarize the main topics."
    }
    ```

  * Returns generated LLM responses and relevant references.

## 📝 Notes

* On startup, the system:

  * Initializes AWS Bedrock LLM (Claude 3.5 Sonnet) and embedding models (Amazon Titan).
  * Loads existing PDFs from `data/` or builds a new hierarchical index.
  * Loads or builds the hierarchical RAG index stored in `storage/hrag_index/`.
  * Sets up a global query engine for efficient retrieval.
* Logs are written to `logs/app.log` with rotation.
* Ensure PDF documents are in `data/` before first run or index rebuild.