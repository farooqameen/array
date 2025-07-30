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
.
├── .devcontainer       # Development container configuration for VS Code
└── app                 # Main application directory
    ├── .env                # Environment variables/secrets (OpenSearch, S3 Bucket)
    ├── config              # Application configuration settings and constants
    ├── controllers         # Request handlers and business logic coordination 
    ├── core                # Core application components (initialization, lifespan)
    ├── models              # Data models and Pydantic schemas for API requests/responses
    ├── prompts             # LLM prompt templates for RAG and chat functionality
    ├── router              # FastAPI route definitions and endpoint mappings
    ├── services            # Business logic services organized by functionality:
    │   ├── bot                 # Chatbot and conversation handling services
    │   ├── csv                 # CSV file processing and analysis services
    │   ├── search              # OpenSearch integration and search functionality
    │   └── stores              # Data storage and retrieval services
    └── utils             # Utility functions and helper modules


```

## 🛠️ Setup & Running

### Prerequisites

  * [Python 3.13](https://www.python.org/downloads/) (see `.python-version` for the recommended version)
  * [`uv`](https://github.com/astral-sh/uv) (fast Python package manager; replaces `pip install`)
  * AWS account with access to Bedrock and the required models (Claude 3.5 Sonnet, Amazon Titan Embeddings)
  * [AWS CLI version 2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured with appropriate credentials (`aws configure`)

**Important:** Ensure your `.env` file contains all necessary environment variables, including OpenSearch parameters and other required configuration settings.


### 1. Authenticate Using AWS CLI

Configure AWS SSO and authenticate:

```bash
aws configure sso
aws sso login
```


### 2. Prepare Your Environment

Open a terminal in your project root and run:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.\.venv\Scripts\Activate.ps1
```


### 3. Install Dependencies

Navigate to the project root and install the required Python packages using [`uv`](https://github.com/astral-sh/uv):

```bash
uv sync
```

> **Note:**  
> This project uses `uv` for dependency management, with a `pyproject.toml` and `uv.lock` file for reproducible installs.  
> Make sure you have `uv` installed (`pip install uv` or see [uv GitHub](https://github.com/astral-sh/uv#installation)).


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

Access the application at `http://127.0.0.1:8000/docs`.

### 6. API Endpoints

#### Chat Endpoints

- **POST `/chat/upload/`**  
  Upload a document and (re)build the selected RAG index.

- **POST `/queryHRAG`**  
  Query document using the Hierarchical RAG (HRAG) system.

- **POST `/queryRAG`**  
  Query the traditional RAG system.

- **POST `/clearRAGDocs`**  
  Clear the RAG index.

#### OpenSearch Endpoints

- **POST `/search/upload/`**  
  Upload multiple PDFs and index their content into OpenSearch.

- **GET `/search`**  
  Search within a specific OpenSearch index.

#### CSV & PDF Endpoints

- **POST `/csv/upload`**  
  Upload a CSV file and return summary and chart suggestions.

- **POST `/pdf/upload`**  
  Upload a PDF file, extract tables, and return summary and chart suggestions.

- **POST `/csv/query`**  
  Stream query response from uploaded CSV using LLM.

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

## 🐳 Setup & Running with Dev Container in VS Code

### Prerequisites

  * [Docker](https://www.docker.com/get-started) installed and running on your machine (can be installed through the Company Portal)
  * [Visual Studio Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  * AWS account with access to Bedrock and the required models (Claude 3.5 Sonnet, Amazon Titan Embeddings)

**Important:** Ensure your `.env` file contains all necessary environment variables, including OpenSearch parameters and other required configuration settings.

### 1. Open Project in Dev Container

1. Clone the repository and open it in VS Code
2. When prompted, click "Reopen in Container" or use the Command Palette (`Ctrl+Shift+P`) and select "Dev Containers: Reopen in Container"
3. VS Code will build the dev container automatically with all dependencies pre-installed

### 2. Configure AWS Authentication

The dev container includes the AWS CLI pre-installed. Configure your AWS credentials:

```bash
aws configure sso
aws sso login
```

### 3. Run the Application

The dev container automatically sets up the Python environment. From the `app/` directory, start the application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

or simply run:

```bash
python main.py
```

VS Code will automatically forward port 8000, and you can access the application at `http://localhost:8000/docs`.

### Benefits of Using Dev Container

  * **Consistent Environment**: All team members work in identical development environments
  * **Pre-installed Dependencies**: AWS CLI, Git, Python, and all required tools are ready to use
  * **Automatic Port Forwarding**: VS Code automatically forwards application ports to your host machine

---
