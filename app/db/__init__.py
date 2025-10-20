# This file marks the directory as a Python package
from app.db.models import Base, Vault, Document, Chunk
from app.db.session import engine, SessionLocal, get_db

# Initialize models
Base.metadata.create_all(bind=engine)

__all__ = ["Base", "Vault", "Document", "Chunk", "engine", "SessionLocal", "get_db"]