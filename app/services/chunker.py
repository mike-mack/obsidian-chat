import hashlib
from typing import List, Dict, Any, Tuple
from app.db.models import Document, Chunk
from app.db.session import get_db_context
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


class Chunker:
    """
    Class responsible for splitting documents into chunks.
    Handles various chunking strategies and stores chunks in the database.
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the chunker with specified or default chunking parameters.
        
        Args:
            chunk_size: The size of each chunk in characters
            chunk_overlap: The overlap between chunks in characters
        """
        self.chunk_size = chunk_size or CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or CHUNK_OVERLAP
        
    def process_document(self, document_id: str) -> List[Chunk]:
        """
        Process a document and split it into chunks.
        
        Args:
            document_id: The ID of the document to process
            
        Returns:
            List[Chunk]: The list of created chunks
        """
        with get_db_context() as db:
            # Get the document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document with ID '{document_id}' not found")
                
            # Read the document content
            doc_path = document.path
            if doc_path.startswith('/'):
                full_path = f"{document.vault.path}{doc_path}"
            else:
                full_path = f"{document.vault.path}/{doc_path}"
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Delete existing chunks for this document
            db.query(Chunk).filter(Chunk.document_id == document_id).delete()
            
            # Create new chunks
            chunks = self._create_chunks(content, document_id)
            
            # Add chunks to database
            db.add_all(chunks)
            db.flush()
            
            return chunks
    
    def _create_chunks(self, text: str, document_id: str) -> List[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to split
            document_id: The ID of the document
            
        Returns:
            List[Chunk]: The list of Chunk objects
        """
        chunks = []
        
        # If text is shorter than chunk size, create a single chunk
        if len(text) <= self.chunk_size:
            chunk_hash = self._calculate_hash(text)
            chunks.append(Chunk(
                document_id=document_id,
                content=text,
                sequence=0,
                chunk_hash=chunk_hash
            ))
            return chunks
        
        # Split text into chunks with overlap
        start = 0
        sequence = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # If this is not the first chunk, adjust start position
            if start > 0:
                start = start - self.chunk_overlap
                end = min(start + self.chunk_size, len(text))
            
            # Extract chunk text
            chunk_text = text[start:end]
            
            # Calculate hash for the chunk
            chunk_hash = self._calculate_hash(chunk_text)
            
            # Create chunk object
            chunk = Chunk(
                document_id=document_id,
                content=chunk_text,
                sequence=sequence,
                chunk_hash=chunk_hash
            )
            chunks.append(chunk)
            
            # Update counters for next iteration
            sequence += 1
            start = end
            
        return chunks
    
    def _calculate_hash(self, content: str) -> str:
        """
        Calculate a SHA-256 hash of the content.
        
        Args:
            content: The content to hash
            
        Returns:
            str: The hexadecimal hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()