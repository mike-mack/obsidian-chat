import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from app.db.models import Vault, Document, Chunk
from app.db.session import get_db_context
from app.config import VECTOR_STORE_PATH, VECTOR_STORE_TYPE
from app.services.embedder.base import BaseEmbedder


class VectorStore:
    """
    Vector store for managing document embeddings.
    Supports FAISS and other vector databases.
    """
    
    def __init__(self, embedder: BaseEmbedder, vector_store_path: str = None):
        """
        Initialize the vector store.
        
        Args:
            embedder: The embedder to use for embedding text
            vector_store_path: Path to store vector indices (if None, uses config)
        """
        self.embedder = embedder
        self.vector_store_path = vector_store_path or VECTOR_STORE_PATH
        self.vector_store_type = VECTOR_STORE_TYPE
        
        # Create vector store directory if it doesn't exist
        os.makedirs(self.vector_store_path, exist_ok=True)
    
    def get_vault_index_path(self, vault_id: str) -> str:
        """
        Get the path to the vector index for a vault.
        
        Args:
            vault_id: The ID of the vault
            
        Returns:
            str: The path to the vector index
        """
        return os.path.join(self.vector_store_path, f"{vault_id}.index")
    
    def create_or_update_index(self, vault_id: str) -> Dict[str, Any]:
        """
        Create or update the vector index for a vault.
        
        Args:
            vault_id: The ID of the vault
            
        Returns:
            Dict: Statistics about the indexing process
        """
        import faiss
        
        with get_db_context() as db:
            # Get the vault
            vault = db.query(Vault).filter(Vault.id == vault_id).first()
            if not vault:
                raise ValueError(f"Vault with ID '{vault_id}' not found")
                
            # Get all chunks that need embedding
            chunks = db.query(Chunk).join(Document).filter(
                Document.vault_id == vault_id,
                Chunk.embedding_stored == False
            ).all()
            
            # If no chunks need embedding, return early
            if not chunks:
                return {
                    "chunks_processed": 0,
                    "vectors_added": 0,
                    "status": "No new chunks to process"
                }
                
            # Get chunk contents for embedding
            chunk_contents = [chunk.content for chunk in chunks]
            chunk_ids = [chunk.id for chunk in chunks]
            
            # Create embeddings
            embeddings = self.embedder.embed_batch(chunk_contents)
            
            # Create or load index
            index_path = self.get_vault_index_path(vault_id)
            dimension = self.embedder.get_embedding_dimension()
            
            if os.path.exists(index_path):
                # Load existing index
                index = faiss.read_index(index_path)
                
                # Add new vectors
                index.add(np.array(embeddings, dtype=np.float32))
            else:
                # Create new index
                index = faiss.IndexFlatL2(dimension)
                index.add(np.array(embeddings, dtype=np.float32))
            
            # Save index
            faiss.write_index(index, index_path)
            
            # Update chunks to mark as embedded
            for chunk_id in chunk_ids:
                chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
                if chunk:
                    chunk.embedding_stored = True
            
            return {
                "chunks_processed": len(chunks),
                "vectors_added": len(embeddings),
                "status": "Index updated successfully"
            }
    
    def search(self, vault_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the vector store for similar chunks.
        
        Args:
            vault_id: The ID of the vault to search
            query: The query text
            top_k: The number of results to return
            
        Returns:
            List[Dict]: The search results
        """
        import faiss
        
        # Check if index exists
        index_path = self.get_vault_index_path(vault_id)
        if not os.path.exists(index_path):
            raise ValueError(f"No index found for vault with ID '{vault_id}'")
            
        # Load index
        index = faiss.read_index(index_path)
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search index
        D, I = index.search(np.array([query_embedding], dtype=np.float32), top_k)
        
        # Get chunk IDs from database based on sequence
        with get_db_context() as db:
            # Get all chunks for this vault
            all_chunks = db.query(Chunk).join(Document).filter(
                Document.vault_id == vault_id,
                Chunk.embedding_stored == True
            ).order_by(Chunk.id).all()
            
            # If no chunks or index is empty
            if not all_chunks or len(I[0]) == 0:
                return []
                
            # Get chunks for results
            results = []
            for idx in I[0]:
                if idx < len(all_chunks):
                    chunk = all_chunks[idx]
                    document = db.query(Document).filter(Document.id == chunk.document_id).first()
                    
                    results.append({
                        "chunk_id": chunk.id,
                        "document_id": chunk.document_id,
                        "document_path": document.path if document else "Unknown",
                        "document_name": document.filename if document else "Unknown",
                        "content": chunk.content,
                        "sequence": chunk.sequence
                    })
            
            return results