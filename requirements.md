# Obsidian Chat

## Overview
### Goal
A local web-based application that allows users to interact with their personal Obsidian vaults using a local LLM. The app demonstrates core LLM application capabilities: ingestion, vectorization, storage, and retrieval-based querying.

### Primary Use Case
User selects a local Obsidian vault, the app indexes its contents (e.g., markdown files), generates vector embeddings, and allows the user to perform semantic search or question-answering over the vault contents through a simple web interface.

### Primary Users
Single end-user (you / developers) experimenting with LLM app design and RAG (retrieval-augmented generation).
Potentially, other tech-savvy local users comfortable running local web servers.

### Core Capabilities
Discover local Obsidian vaults (by browsing filesystem).
Parse and index vault contents (markdown files).
Generate embeddings and store them locally (SQLite or similar).
Expose a local web UI to query or chat with the indexed content.
Display responses and optionally show retrieved document snippets.


## Functional Requirements
### **FR1. Vault Management**

* **FR1.1** The system shall allow users to identify and register one or more local Obsidian vaults via the web UI (by browsing filesystem directories).
* **FR1.2** The system shall persist metadata for each registered vault (e.g., name, path, embedding status, last updated).
* **FR1.3** The system shall allow users to switch between vaults in the UI.
* **FR1.4** The system shall allow vault deregistration or re-indexing.

### **FR2. Vault Content Processing**

* **FR2.1** The system shall recursively scan the selected vault directory for Markdown files (`.md`).
* **FR2.2** The system shall extract plain text from Markdown files, removing front matter, code blocks, and formatting.
* **FR2.3** The system shall chunk content into suitable text segments for embedding generation.
* **FR2.4** The system shall generate vector embeddings for each chunk using a configured embedding provider (default: OpenAI).
* **FR2.5** The system shall store embeddings and metadata locally in a vector database or similar store (e.g., SQLite + FAISS / Chroma).
* **FR2.6** The system shall maintain an index linking each embedding back to the source file and chunk.

### **FR3. Query Interface**

* **FR3.1** The system shall provide a text input box for users to submit queries about the active vault.
* **FR3.2** The system shall retrieve the top relevant chunks based on vector similarity.
* **FR3.3** The system shall assemble a context from retrieved chunks and submit it to the LLM for response generation.
* **FR3.4** The system shall display the generated response in the UI.
* **FR3.5** The system shall optionally show the retrieved source snippets (file name, text excerpt).

### **FR4. Model Configuration**

* **FR4.1** The system shall allow configuration of the embedding model and LLM via environment variables or a configuration file.
* **FR4.2** The system shall default to OpenAI APIs (e.g., `text-embedding-3-small`, `gpt-4o-mini`).
* **FR4.3** The system shall allow switching to a locally running model (e.g., Ollama, LM Studio) without major architectural change.
* **FR4.4** The configuration shall include model provider, model name, API endpoint, and authentication credentials if required.

### **FR5. Web Interface**

* **FR5.1** The web UI shall be minimal and responsive, with two main views:

  * **Vault Management View:** list of vaults, add/remove/re-index actions.
  * **Query View:** chat or query interface with response display.
* **FR5.2** The UI shall display progress during vault indexing and embedding generation.
* **FR5.3** The UI shall display error messages for failed operations (e.g., embedding API errors, missing files).

### **FR6. System Configuration and Persistence**

* **FR6.1** The system shall persist configuration data locally (e.g., vault list, embedding database location).
* **FR6.2** The system shall resume from prior state upon restart (no need to reindex unless vaults changed).
* **FR6.3** The system shall allow resetting or clearing embeddings for a vault.


## Non-Functional Requirements
### **NFR1. Performance**

* **NFR1.1** The system shall handle vaults up to ~10,000 Markdown files without crashing or excessive memory consumption.
* **NFR1.2** Embedding generation speed will depend on model/API throughput, but the system must stream progress updates in the UI.
* **NFR1.3** Query response time should be ≤ 5 seconds on average when using an external API model (excluding network latency).
* **NFR1.4** Local model inference performance will depend on user hardware; the app should not assume GPU availability.

### **NFR2. Reliability and Fault Tolerance**

* **NFR2.1** The app must handle partial failures gracefully — e.g., if embedding generation fails for a subset of files, others continue.
* **NFR2.2** The app must recover from interruption (e.g., process kill) without data corruption — embeddings persist once written.
* **NFR2.3** Re-indexing should overwrite prior embeddings for a vault cleanly.

### **NFR3. Privacy and Security**

* **NFR3.1** The system shall process all vault contents locally before any external API calls.
* **NFR3.2** When using OpenAI or another remote provider, only text chunks are sent; no metadata or file paths leave the local machine.
* **NFR3.3** No vault content or embeddings are ever transmitted or stored outside the local environment.
* **NFR3.4** The app does not expose any network ports beyond localhost.

### **NFR4. Maintainability and Extensibility**

* **NFR4.1** The embedding and LLM providers shall be abstracted behind an adapter interface to allow new providers (e.g., OpenAI → Ollama) with minimal changes.
* **NFR4.2** The system’s core components (vault management, embeddings, query, UI) shall be modular and independently testable.
* **NFR4.3** The codebase should follow standard Python conventions (PEP8, docstrings, logging).

### **NFR5. Usability**

* **NFR5.1** The web UI shall be minimal, clear, and usable without training.
* **NFR5.2** The user must be able to perform all core actions (add vault, index, query, view results) within two clicks per action.
* **NFR5.3** Progress and error states must be visible and informative.

### **NFR6. Portability**

* **NFR6.1** The application shall run on macOS, Linux, and Windows (Python-based stack).
* **NFR6.2** All dependencies shall be installable via a single `requirements.txt` or `poetry.lock` file.

### **NFR7. Resource Efficiency**

* **NFR7.1** The app must run on a machine with as little as 4 GB RAM and 2 CPU cores without instability.
* **NFR7.2** Background embedding tasks should be throttled to prevent system freeze.



## Technical Implementation
### **High-Level Overview**
**Core Components:**

1. **Frontend (UI Layer)**

   * Built with **HTMX + Alpine.js + TailwindCSS**
   * Provides reactive UI without a full SPA framework.
   * Main pages:

     * Vault Management View
     * Query Interface View
     * Progress and error overlays

2. **Backend (FastAPI Application)**

   * REST + HTML endpoints (HTMX partials).
   * Services for vault management, embedding, and query handling.
   * Runs locally via Docker (containerized with Postgres).

3. **Database Layer (Postgres + pgvector)**

   * Stores:

     * Vault metadata
     * File metadata
     * Embeddings (using `vector` type)
     * Query logs (optional)
   * Provides efficient vector similarity search using pgvector indexes.

4. **Embedding Service**

   * Generates embeddings using a configured provider (default: OpenAI API).
   * Abstracted via a provider interface, allowing drop-in local alternatives (e.g., Ollama, text-embedding models).
   * Handles chunking, batching, and persistence to Postgres.

5. **Query / Retrieval Service**

   * Performs similarity search in pgvector for a given query.
   * Assembles retrieved text chunks into a context prompt.
   * Sends to configured LLM provider for answer generation.
   * Returns both final answer and optionally retrieved source snippets.

6. **Configuration Service**

   * Handles reading/writing config (e.g., model provider, API keys).
   * Uses `.env` or YAML for portability.

---

### **Data Flow**

**Vault Registration Flow:**

1. User selects vault path via UI (directory browser).
2. Backend stores vault record in Postgres.
3. User triggers “Index Vault”.
4. Files are read → cleaned → chunked.
5. Embeddings generated via provider → stored in Postgres.
6. Progress streamed back to UI (via HTMX polling or SSE).

**Query Flow:**

1. User submits query in the web UI.
2. Backend retrieves top N embeddings from Postgres via pgvector similarity.
3. Retrieved text chunks concatenated into context.
4. Context + query sent to LLM provider for completion.
5. LLM response returned to frontend for display (with optional source snippets).

---

### **Key Modules / Subsystems**

| Module           | Responsibility                                                     | Implementation Notes                     |
| ---------------- | ------------------------------------------------------------------ | ---------------------------------------- |
| **VaultManager** | Manage vault registration, path validation, and reindexing         | CRUD via SQLAlchemy ORM                  |
| **FileParser**   | Traverse directories, extract text from Markdown, clean formatting | Can use `frontmatter` or `markdown` libs |
| **Chunker**      | Split long texts into smaller sections                             | Simple token or sentence-based chunking  |
| **Embedder**     | Generate embeddings using configured provider                      | Adapter pattern (OpenAI, Local, etc.)    |
| **VectorStore**  | Handle insert/query operations for embeddings                      | SQLAlchemy + pgvector                    |
| **QueryEngine**  | Retrieve context, call LLM, format response                        | Integrates Embedder + VectorStore        |
| **Frontend**     | Provide minimal, fast HTML interface                               | HTMX partial updates for async actions   |

---

### **Technology Stack**

| Layer            | Technology                      | Rationale                                       |
| ---------------- | ------------------------------- | ----------------------------------------------- |
| Backend          | **FastAPI**                     | Async, simple, well-suited for modular services |
| Frontend         | **HTMX + Alpine.js + Tailwind** | Lightweight interactivity, no heavy JS build    |
| Database         | **Postgres + pgvector**         | Unified relational + vector data store          |
| ORM              | **SQLAlchemy**                  | Stable, well-integrated with FastAPI            |
| Embeddings       | **OpenAI API** (default)        | Reliable baseline model; later pluggable        |
| LLM Inference    | **OpenAI or Local Ollama**      | Configurable                                    |
| Containerization | **Docker + docker-compose**     | Isolated local environment                      |
| Configuration    | **pydantic-settings** or `.env` | Clean separation of config                      |
| Logging          | Python `logging` + middleware   | For monitoring embedding/query ops              |

---

### **Persistence Schema (simplified)**

**vaults**

* `id` (PK)
* `name`
* `path`
* `created_at`
* `last_indexed_at`

**files**

* `id` (PK)
* `vault_id` (FK)
* `path`
* `last_modified`
* `hash` (content hash)

**embeddings**

* `id` (PK)
* `file_id` (FK)
* `chunk_index`
* `content` (text chunk)
* `embedding` (vector)

**queries** (optional)

* `id` (PK)
* `vault_id` (FK)
* `query_text`
* `response_text`
* `created_at`

