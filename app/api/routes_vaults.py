from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Any, Optional
import time
import traceback
from pydantic import BaseModel
from app.services.vault_manager import VaultManager
from app.services.chunker import Chunker
from app.services.vectorstore import VectorStore
from app.services.embedder.factory import get_embedder
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.core import get_logger

# Initialize logger
logger = get_logger(__name__)

router = APIRouter(prefix="/vaults", tags=["vaults"])

# Initialize services
vault_manager = VaultManager()
chunker = Chunker()
embedder = get_embedder()
vector_store = VectorStore(embedder)

# Pydantic models for API
class VaultCreate(BaseModel):
    name: str
    path: str


class VaultResponse(BaseModel):
    id: str
    name: str
    path: str
    is_indexed: bool
    created_at: str


class ScanResponse(BaseModel):
    vault_id: str
    stats: Dict[str, Any]


@router.post("/", response_model=VaultResponse)
def create_vault(vault_data: VaultCreate):
    """
    Register a new Obsidian vault.
    """
    try:
        vault = vault_manager.register_vault(vault_data.name, vault_data.path)
        return {
            "id": vault.id,
            "name": vault.name,
            "path": vault.path,
            "is_indexed": vault.is_indexed,
            "created_at": vault.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/", response_model=List[VaultResponse])
def get_all_vaults():
    """
    Get all registered vaults.
    """
    try:
        vaults = vault_manager.get_all_vaults()
        return [
            {
                "id": vault.id,
                "name": vault.name,
                "path": vault.path,
                "is_indexed": vault.is_indexed,
                "created_at": vault.created_at.isoformat()
            }
            for vault in vaults
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{vault_id}", response_model=VaultResponse)
def get_vault(vault_id: str):
    """
    Get a vault by ID.
    """
    vault = vault_manager.get_vault(vault_id)
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    return {
        "id": vault.id,
        "name": vault.name,
        "path": vault.path,
        "is_indexed": vault.is_indexed,
        "created_at": vault.created_at.isoformat()
    }


@router.post("/{vault_id}/scan", response_model=ScanResponse)
def scan_vault(vault_id: str):
    """
    Scan a vault for markdown files and update the database.
    """
    try:
        stats = vault_manager.scan_vault(vault_id)
        return {
            "vault_id": vault_id,
            "stats": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/{vault_id}/process", response_model=Dict[str, Any])
def process_vault(vault_id: str, db: Session = Depends(get_db)):
    """
    Process a vault: scan, chunk documents, and create embeddings.
    """
    try:
        # Step 1: Scan vault for markdown files
        scan_stats = vault_manager.scan_vault(vault_id)
        
        # Step 2: Get all documents for this vault
        documents = db.query(Document).filter(Document.vault_id == vault_id).all()
        document_ids = [doc.id for doc in documents]
        
        # Step 3: Process each document to create chunks
        chunk_count = 0
        for doc_id in document_ids:
            chunks = chunker.process_document(doc_id)
            chunk_count += len(chunks)
        
        # Step 4: Create or update vector index
        index_stats = vector_store.create_or_update_index(vault_id)
        
        return {
            "vault_id": vault_id,
            "scan_stats": scan_stats,
            "documents_processed": len(document_ids),
            "chunks_created": chunk_count,
            "index_stats": index_stats
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.delete("/{vault_id}", response_model=Dict[str, Any])
def delete_vault(vault_id: str):
    """
    Delete a vault and all its associated data.
    """
    success = vault_manager.delete_vault(vault_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    return {"status": "success", "message": "Vault deleted successfully"}


# Import models here to avoid circular imports
from app.db.models import Document