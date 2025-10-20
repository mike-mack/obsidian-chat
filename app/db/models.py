from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Vault(Base):
    """Model representing an Obsidian vault."""
    __tablename__ = "vaults"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    path = Column(String(1024), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_indexed = Column(Boolean, default=False)
    
    # Relationships
    documents = relationship("Document", back_populates="vault", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vault(name='{self.name}', path='{self.path}')>"


class Document(Base):
    """Model representing a document (note) in the vault."""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vault_id = Column(String(36), ForeignKey("vaults.id"), nullable=False)
    path = Column(String(1024), nullable=False)
    filename = Column(String(255), nullable=False)
    content_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vault = relationship("Vault", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(filename='{self.filename}', path='{self.path}')>"


class Chunk(Base):
    """Model representing a chunk of text from a document."""
    __tablename__ = "chunks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    sequence = Column(Integer, nullable=False)
    chunk_hash = Column(String(64), nullable=False)
    embedding_stored = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(document_id='{self.document_id}', sequence='{self.sequence}')>"