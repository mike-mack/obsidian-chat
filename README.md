# Obsidian Chat

A local web-based application for semantic search and question-answering over your Obsidian vaults using vector embeddings and retrieval-augmented generation (RAG).

## Overview

Obsidian Chat enables you to interact with your personal knowledge base using natural language queries. The application indexes your Obsidian vault contents, generates vector embeddings, and provides a web interface for semantic search and contextual question-answering.

### Key Features

- **Vault Management**: Register, index, and manage multiple Obsidian vaults through a web interface
- **Semantic Search**: Vector-based similarity search using FAISS for fast, relevant retrieval
- **Flexible Embedding Models**: Support for OpenAI embeddings or local sentence-transformer models
- **Web Interface**: Clean, responsive UI built with FastAPI, HTMX, and Tailwind CSS
- **Persistent Storage**: SQLite database with FAISS vector indices for efficient retrieval
- **Incremental Indexing**: Track file changes and re-index only modified content
- **Containerized Deployment**: Docker support for consistent local deployment

## Architecture

### System Components

The application follows a modular architecture with clear separation of concerns:

```
app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── api/                   # API route handlers
│   ├── routes_vaults.py   # Vault management endpoints
│   └── routes_query.py    # Query and search endpoints
├── services/              # Core business logic
│   ├── vault_manager.py   # Vault registration and metadata
│   ├── file_parser.py     # Markdown parsing and extraction
│   ├── chunker.py         # Text chunking strategies
│   ├── vectorstore.py     # Vector database operations
│   ├── query_engine.py    # Query processing and retrieval
│   └── embedder/          # Embedding provider abstraction
│       ├── base.py        # Base embedder interface
│       ├── factory.py     # Provider factory
│       ├── openai_impl.py # OpenAI embedding implementation
│       └── local_impl.py  # Local model implementation
├── db/                    # Database layer
│   ├── models.py          # SQLAlchemy ORM models
│   └── session.py         # Database session management
├── core/                  # Core utilities
│   ├── logging.py         # Logging configuration
│   └── middleware.py      # Request middleware
└── templates/             # HTML templates
    ├── index.html         # Landing page
    ├── vaults_list.html   # Vault management view
    └── query.html         # Query interface
```

### Data Flow

**Vault Indexing Flow:**
1. User registers vault via web UI
2. System scans directory for Markdown files
3. Files are parsed, cleaned, and chunked
4. Embeddings generated via configured provider
5. Vectors stored in FAISS index with metadata in SQLite
6. Progress updates streamed to UI

**Query Flow:**
1. User submits natural language query
2. Query embedded using same model as vault content
3. FAISS performs similarity search to retrieve top-k chunks
4. Retrieved context and source metadata returned to user
5. Results displayed with source attribution

## Installation

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (optional, required only for OpenAI embeddings)

### Quick Start with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/mike-mack/obsidian-chat.git
   cd obsidian-chat
   ```

2. (Optional) Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to set your preferences
   ```

3. Start the application:
   ```bash
   ./start-docker.sh
   # Or manually:
   docker-compose up --build
   ```

4. Access the application at `http://localhost:8000`

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mike-mack/obsidian-chat.git
   cd obsidian-chat
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Access the application at `http://localhost:8000`

## Configuration

Configuration is managed through environment variables, either set in a `.env` file or passed directly to the application.

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | SQLite database connection string | `sqlite:///./obsidian_chat.db` | No |
| `EMBEDDING_MODEL` | Embedding provider: `openai` or `local` | `local` | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes (if using OpenAI) |
| `EMBEDDING_DIMENSION` | Vector dimension for embeddings | `1536` | No |
| `VECTOR_STORE_TYPE` | Vector store backend | `faiss` | No |
| `VECTOR_STORE_PATH` | Path for vector index storage | `./vector_store` | No |
| `CHUNK_SIZE` | Maximum characters per text chunk | `1000` | No |
| `CHUNK_OVERLAP` | Character overlap between chunks | `200` | No |
| `DEFAULT_VAULT_PATH` | Default Obsidian vault path | - | No |

### Example Configuration

**For OpenAI Embeddings:**
```bash
EMBEDDING_MODEL=openai
OPENAI_API_KEY=sk-...
EMBEDDING_DIMENSION=1536
```

**For Local Embeddings:**
```bash
EMBEDDING_MODEL=local
EMBEDDING_DIMENSION=384
```

## Usage

### Registering a Vault

1. Navigate to the Vault Management page
2. Click "Add Vault"
3. Enter vault name and select the directory path
4. Click "Register"

### Indexing Vault Content

1. Select a registered vault
2. Click "Index Vault"
3. Monitor indexing progress in the UI
4. Wait for completion (progress updates show processed files)

### Querying Your Vault

1. Navigate to the Query page
2. Select the indexed vault
3. Enter your natural language query
4. View results with source file attribution
5. Adjust `top_k` parameter to retrieve more or fewer chunks

## API Documentation

Once running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

**Vault Management:**
- `POST /api/v1/vaults/` - Register a new vault
- `GET /api/v1/vaults/` - List all vaults
- `GET /api/v1/vaults/{vault_id}` - Get vault details
- `DELETE /api/v1/vaults/{vault_id}` - Remove a vault
- `POST /api/v1/vaults/{vault_id}/scan` - Scan vault for files
- `POST /api/v1/vaults/{vault_id}/index` - Index vault content

**Query:**
- `POST /api/v1/query/{vault_id}` - Query a vault

## Technical Details

### Embedding Providers

**OpenAI (Default for Quality):**
- Model: `text-embedding-3-small`
- Dimension: 1536
- Requires API key
- Higher quality, cost per API call

**Local (Default for Privacy):**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- No API key required
- Runs entirely locally
- Faster for small vaults

### Text Processing

1. **File Parsing**: Extracts plain text from Markdown, removes front matter and code blocks
2. **Chunking**: Splits text into overlapping segments (default: 1000 chars, 200 overlap)
3. **Embedding**: Generates vector representations for each chunk
4. **Storage**: Persists vectors in FAISS index, metadata in SQLite

### Vector Search

- Uses FAISS (Facebook AI Similarity Search) for efficient similarity computation
- Default: Inner Product (IP) similarity metric
- Configurable `top_k` parameter for result count
- Returns chunks with source file metadata

## Development

### Project Structure

See `structure.md` for detailed project organization.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Requirements Coverage

This implementation satisfies the following functional requirements:

- **FR1. Vault Management**: Register, list, switch between, and deregister vaults
- **FR2. Vault Content Processing**: Scan, parse, chunk, embed, and index Markdown files
- **FR3. Query Interface**: Natural language queries with vector similarity retrieval and source attribution
- **FR4. Model Configuration**: Configurable embedding providers (OpenAI/local) via environment variables
- **FR5. Web Interface**: Minimal, responsive UI with vault management and query views
- **FR6. System Configuration**: Persistent configuration and resumable state

See `requirements.md` for complete functional and non-functional requirements.

## Performance Considerations

- **Vault Size**: Tested with vaults up to 10,000 files
- **Indexing Speed**: Depends on embedding provider (OpenAI API vs. local model)
- **Query Latency**: Typically under 2 seconds for local embeddings
- **Memory Usage**: Scales with vector index size (approx. 4KB per chunk)
- **Incremental Updates**: Re-index detects changed files using content hashing

## Privacy and Security

- All vault content processed locally before any external API calls
- When using OpenAI, only text chunks sent (no file paths or metadata)
- Vector embeddings and metadata never leave local environment
- Application binds to localhost only by default
- Docker deployment isolates application in container

## Troubleshooting

### Common Issues

**Indexing fails with OpenAI API errors:**
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and rate limits
- Consider switching to `EMBEDDING_MODEL=local`

**Query returns no results:**
- Ensure vault has been indexed successfully
- Verify vector store path is accessible
- Check that query is semantically related to vault content

**Application won't start:**
- Verify all required dependencies installed
- Check that port 8000 is not already in use
- Review logs for specific error messages

### Logging

Application logs are written to stdout. Adjust log level in `app/core/logging.py`.

## Contributing

Contributions are welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- Built with FastAPI, FAISS, and sentence-transformers
- Inspired by the Obsidian note-taking community
- Implements RAG patterns for personal knowledge management
