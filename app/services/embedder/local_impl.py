from typing import List, Dict, Any, Optional
import numpy as np
from app.services.embedder.base import BaseEmbedder
from app.config import EMBEDDING_DIMENSION

class LocalEmbedder(BaseEmbedder):
    """
    Local embedder implementation using sentence-transformers.
    Provides an alternative to API-based embedders.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the local embedder.
        
        Args:
            model_name: The name of the sentence-transformer model to use
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError("sentence-transformers package is required for LocalEmbedder. "
                             "Install it with 'pip install sentence-transformers'.")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        if not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.embedding_dimension
            
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
            
        # Filter out empty strings and keep track of indices
        non_empty_texts = []
        indices = []
        for i, text in enumerate(texts):
            if text.strip():
                non_empty_texts.append(text)
                indices.append(i)
                
        # If all texts are empty, return zero vectors
        if not non_empty_texts:
            return [[0.0] * self.embedding_dimension for _ in texts]
            
        embeddings = self.model.encode(non_empty_texts)
        
        # Create results list with zero vectors
        results = [[0.0] * self.embedding_dimension for _ in texts]
        
        # Fill in the embeddings for non-empty texts
        for i, idx in enumerate(indices):
            results[idx] = embeddings[i].tolist()
            
        return results
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: The dimension of the embedding vectors
        """
        return self.embedding_dimension