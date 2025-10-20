import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./obsidian_chat.db")

# API settings
API_PREFIX = "/api/v1"

# Embedding settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))  # OpenAI's default

# Vector store settings
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", str(BASE_DIR / "vector_store"))

# Chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Obsidian vault settings
DEFAULT_VAULT_PATH = os.getenv("DEFAULT_VAULT_PATH", "")